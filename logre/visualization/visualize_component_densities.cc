#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <boost/program_options.hpp>

#include <KernelDensity.h>
#include <MarginalDensityAssociator.h>

#include <utils/visualization_utils.h>
#include <utils/custom_program_option_utils.h>

namespace {
  using KernelType = bbrcit::EpanechnikovProductKernel2d<float>;

  using KernelDensityType = 
    bbrcit::KernelDensity<2,KernelType,double>;
  using MarginalDensityType = 
    typename bbrcit::MarginalDensityAssociator<KernelDensityType>::MarginalDensityType;

  using Point2d = typename KernelDensityType::DataPointType;
  using Point1d = typename MarginalDensityType::DataPointType;
}

namespace po = boost::program_options;

// construct (adapted) kernel density using data in `fname`
KernelDensityType construct_kernel_density(
  std::vector<Point2d> points, double alpha, 
  double pilot_bandwidth_x, double pilot_bandwidth_y, 
  double adapt_bandwidth_x, double adapt_bandwidth_y, 
  double rel_tol, double abs_tol, 
  int leaf_max, int block_size) {

  KernelDensityType kde(std::move(points), leaf_max);
  kde.kernel().set_bandwidths(pilot_bandwidth_x, pilot_bandwidth_y);
  kde.adapt_density(alpha, rel_tol, abs_tol, block_size);
  kde.kernel().set_bandwidths(adapt_bandwidth_x, adapt_bandwidth_y);

  return kde;
}

// main routine. 
void evaluate(const po::variables_map &vm);

int main(int argc, char **argv) {

  try {
    // define program options
    po::options_description generic("Generic options");
    generic.add_options()
        ("help,h", "produce help message")
    ;

    po::options_description config("Configuration options");
    config.add_options()

        ("max_leaf_size", po::value<int>(), "maximum leaf size in Kdtree. ")
        ("rel_tol", po::value<double>(), "relative tolerance for kde evaluations. ")
        ("abs_tol", po::value<double>(), "absolute tolerance for kde evaluations. ")
        ("cuda_device_number", po::value<int>(), "cuda device used for this session. ")
        ("gpu_block_size", po::value<int>(), "gpu block size. ")

        ("input_data_dir", po::value<std::string>(), "directory to the input data. ")
        ("input_component_fname", po::value<std::string>(), "input paths to the components. ")

        ("alpha", po::value<double>(), "sensitivity parameters. ")
        ("pilot_bwx", po::value<double>(), "pilot bandwidths in x. ")
        ("pilot_bwy", po::value<double>(), "pilot bandwidths in y. ")
        ("adapt_bwx", po::value<double>(), "evaluation bandwidths in x. ")
        ("adapt_bwy", po::value<double>(), "evaluation bandwidths in y. ")

        ("output_data_dir", po::value<std::string>(), "directory to output visualization data. ")
        ("output_scatter_fname", po::value<std::string>(), "output paths to scatter plot visualization. ")
        ("output_kde2d_fname", po::value<std::string>(), "output paths to kde2d visualization. ")
        ("output_kde1d_x_fname", po::value<std::string>(), "output paths to kde1d x visualization. ")
        ("output_kde1d_y_fname", po::value<std::string>(), "output paths to kde1d y visualization. ")

        ("start2d_x", po::value<double>(), "starting x coordinate for kde2d visualization. ")
        ("end2d_x", po::value<double>(), "starting x coordinate for kde2d visualization. ")
        ("steps2d_x", po::value<int>(), "number of steps to evaluate in x for kde2d visualization. ")
        ("start2d_y", po::value<double>(), "starting y coordinate for kde2d visualization. ")
        ("end2d_y", po::value<double>(), "starting y coordinate for kde2d visualization. ")
        ("steps2d_y", po::value<int>(), "number of steps to evaluate in y for kde2d visualization. ")

        ("start1d_x", po::value<double>(), "starting x coordinate for kde1d visualization. ")
        ("end1d_x", po::value<double>(), "starting x coordinate for kde1d visualization. ")
        ("steps1d_x", po::value<int>(), "number of steps to evaluate in x for kde1d visualization. ")
        ("start1d_y", po::value<double>(), "starting y coordinate for kde1d visualization. ")
        ("end1d_y", po::value<double>(), "starting y coordinate for kde1d visualization. ")
        ("steps1d_y", po::value<int>(), "number of steps to evaluate in y for kde1d visualization. ")

    ;

    po::options_description hidden("Hidden options");
    hidden.add_options()
        ("config_file", po::value<std::string>(), "name of a configuration file. ")
    ;

    po::options_description cmdline_options;
    cmdline_options.add(generic).add(config).add(hidden);

    po::options_description config_file_options;
    config_file_options.add(config);

    po::options_description visible;
    visible.add(generic).add(config);

    po::positional_options_description p;
    p.add("config_file", -1);

    // parse program options and configuration file
    po::variables_map vm;
    store(po::command_line_parser(argc, argv).
          options(cmdline_options).positional(p).run(), vm);
    notify(vm);

    if (vm.count("help") || !vm.count("config_file")) {
      std::cout << std::endl;
      std::cout << "Usage: prepare_data_format [options] config_fname" << std::endl;
      std::cout << visible << "\n";
      return 0;
    }

    std::ifstream fin(vm["config_file"].as<std::string>());
    if (!fin) {
      std::cout << "cannot open config file: ";
      std::cout << vm["config_file"].as<std::string>() << std::endl;
      return 0;
    }

    store(parse_config_file(fin, config_file_options), vm);
    notify(vm);

    // begin evaluation
    evaluate(vm);

  } catch(std::exception& e) {

    std::cerr << "error: " << e.what() << "\n";
    return 1;

  } catch(...) {

    std::cerr << "Exception of unknown type!\n";
    return 1;
  }

  return 0;
}

// main evaluation routine
void evaluate(const po::variables_map &vm) {

  // 1. setup general utilities

  // timers
  std::chrono::high_resolution_clock::time_point start_total, end_total;
  start_total = std::chrono::high_resolution_clock::now();

  std::chrono::high_resolution_clock::time_point start, end;
  std::chrono::duration<double> elapsed;

  // performance parameters
  int max_leaf_size = vm["max_leaf_size"].as<int>();
  double rel_tol = vm["rel_tol"].as<double>();
  double abs_tol = vm["abs_tol"].as<double>();

  std::cout << "+ configuring performance parameters: \n" << std::endl;

  std::cout << "  max leaf size: " << max_leaf_size << std::endl;
  std::cout << "  relative tolerance: " << rel_tol << std::endl;
  std::cout << "  absolute tolerance: " << abs_tol << std::endl;
  std::cout << std::endl;

#ifdef __CUDACC__
  int cuda_device_number = vm["cuda_device_number"].as<int>();
  cudaSetDevice(cuda_device_number);
  cudaDeviceProp deviceProp;
  cudaGetDeviceProperties(&deviceProp, cuda_device_number);
  std::cout << "  gpu device number used for this session: ";
  std::cout << cuda_device_number << "\n";
  std::cout << "  device name: " << deviceProp.name << std::endl;

  int gpu_block_size = vm["gpu_block_size"].as<int>();
  std::cout << "  gpu block size: " << gpu_block_size << std::endl;
  std::cout << std::endl;
#endif


  // 2. job configuration

  std::cout << "+ configuring kde parameters. \n" << std::endl;

  // read and configure I/O paths
  std::string input_data_dir = vm["input_data_dir"].as<std::string>();
  std::string output_data_dir = vm["output_data_dir"].as<std::string>();
  std::string input_component_fname = vm["input_component_fname"].as<std::string>();
  std::string output_scatter_fname = vm["output_scatter_fname"].as<std::string>();
  std::string output_kde2d_fname = vm["output_kde2d_fname"].as<std::string>();
  std::string output_kde1d_x_fname = vm["output_kde1d_x_fname"].as<std::string>();
  std::string output_kde1d_y_fname = vm["output_kde1d_y_fname"].as<std::string>();

  if (!input_data_dir.empty()) { 
    input_component_fname = input_data_dir + "/" + input_component_fname;
  }

  if (!output_data_dir.empty()) { 
    output_scatter_fname = output_data_dir + "/" + output_scatter_fname;
    output_kde2d_fname = output_data_dir + "/" + output_kde2d_fname;
    output_kde1d_x_fname = output_data_dir + "/" + output_kde1d_x_fname;
    output_kde1d_y_fname = output_data_dir + "/" + output_kde1d_y_fname;
  }

  // read in kde component configurations
  double alpha = vm["alpha"].as<double>();
  double pilot_bwx = vm["pilot_bwx"].as<double>();
  double pilot_bwy = vm["pilot_bwy"].as<double>();
  double adapt_bwx = vm["adapt_bwx"].as<double>();
  double adapt_bwy = vm["adapt_bwy"].as<double>();

  // read in grid coordinates
  double start2d_x = vm["start2d_x"].as<double>();
  double end2d_x = vm["end2d_x"].as<double>();
  int steps2d_x = vm["steps2d_x"].as<int>();
  double start2d_y = vm["start2d_y"].as<double>();
  double end2d_y = vm["end2d_y"].as<double>();
  int steps2d_y = vm["steps2d_y"].as<int>();

  double start1d_x = vm["start1d_x"].as<double>();
  double end1d_x = vm["end1d_x"].as<double>();
  int steps1d_x = vm["steps1d_x"].as<int>();
  double start1d_y = vm["start1d_y"].as<double>();
  double end1d_y = vm["end1d_y"].as<double>();
  int steps1d_y = vm["steps1d_y"].as<int>();

  // print configuration parameters
  std::cout << "  input file name: " << input_component_fname << std::endl;
  std::cout << "  output scatter file name: " << output_scatter_fname << std::endl;
  std::cout << "  output kde2d file name: " << output_kde2d_fname << std::endl;
  std::cout << "  output kde1d x file name: " << output_kde1d_x_fname << std::endl;
  std::cout << "  output kde1d y file name: " << output_kde1d_y_fname << std::endl;
  std::cout << std::endl;
  std::cout << "  alpha: " << alpha << std::endl;
  std::cout << "  pilot bandwidths (x, y): " << pilot_bwx << ", " << pilot_bwy << std::endl;
  std::cout << "  adaptive bandwidths (x, y): " << adapt_bwx << ", " << adapt_bwy << std::endl;
  std::cout << std::endl;
  std::cout << "  start2d_x, end2d_x, steps2d_x: ";
  std::cout << start2d_x << " " << end2d_x << " " << steps2d_x << std::endl;
  std::cout << "  start2d_y, end2d_y, steps2d_y: ";
  std::cout << start2d_y << " " << end2d_y << " " << steps2d_y << std::endl;
  std::cout << "  start1d_x, end1d_x, steps1d_x: ";
  std::cout << start1d_x << " " << end1d_x << " " << steps1d_x << std::endl;
  std::cout << "  start1d_y, end1d_y, steps1d_y: ";
  std::cout << start1d_y << " " << end1d_y << " " << steps1d_y << std::endl;
  std::cout << std::endl;


  // 3. evaluate for visualization

  std::cout << "+ main evaluation. \n" << std::endl;

  // read in sample points
  std::vector<Point2d> reference_points 
    = read_2dpoints<Point2d>(input_component_fname);

  std::cout << "  number of sample points: " << reference_points.size() << std::endl;
  std::cout << "  number of 2d grid points: " << steps2d_x * steps2d_y << std::endl;
  std::cout << "  number of 1d grid points (x, y): ";
  std::cout << steps1d_x << ", " << steps1d_y << "\n" << std::endl;

  // construct the 2d kde
  std::cout << std::left << std::setfill('.') << std::setw(40) << "  constructing 2d kde";
  start = std::chrono::high_resolution_clock::now();
  KernelDensityType kde = 
    construct_kernel_density(reference_points, 
                             alpha, 
                             pilot_bwx, pilot_bwy, 
                             adapt_bwx, adapt_bwy,
                             rel_tol, abs_tol, max_leaf_size, gpu_block_size);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  // evaluate 2d kde
  std::cout << std::left << std::setfill('.') << std::setw(40) << "  evaluating 2d kde";
  std::vector<Point2d> grid2d;
  generate_2dgrid(grid2d, start2d_x, end2d_x, steps2d_x,
                          start2d_y, end2d_y, steps2d_y);

  start = std::chrono::high_resolution_clock::now();
  kde.eval(grid2d, rel_tol, abs_tol, max_leaf_size);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  // evaluate marginal 1d kde: x
  std::cout << std::left << std::setfill('.') << std::setw(40) << "  constructing marginal kde in x";
  std::vector<Point1d> grid1d_x;
  generate_1dgrid(grid1d_x, start1d_x, end1d_x, steps1d_x);

  start = std::chrono::high_resolution_clock::now();
  MarginalDensityType kde_x = 
    bbrcit::MarginalDensityAssociator<KernelDensityType>::marginal_density_x(kde);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  std::cout << std::left << std::setfill('.') << std::setw(40) << "  evaluating marginal kde in x";
  start = std::chrono::high_resolution_clock::now();
  kde_x.eval(grid1d_x, rel_tol, abs_tol, max_leaf_size);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  // evaluate marginal 1d kde: y
  std::cout << std::left << std::setfill('.') << std::setw(40) << "  constructing marginal kde in y";
  std::vector<Point1d> grid1d_y;
  generate_1dgrid(grid1d_y, start1d_y, end1d_y, steps1d_y);

  start = std::chrono::high_resolution_clock::now();
  MarginalDensityType kde_y = 
    bbrcit::MarginalDensityAssociator<KernelDensityType>::marginal_density_y(kde);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  std::cout << std::left << std::setfill('.') << std::setw(40) << "  evaluating marginal kde in y";
  start = std::chrono::high_resolution_clock::now();
  kde_y.eval(grid1d_y, rel_tol, abs_tol, max_leaf_size);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << " " << elapsed.count() << " s. " << std::endl;

  std::cout << std::endl;


  // write output
  std::ofstream fout;
  fout.open(output_scatter_fname);
  write_2dscatter_data(fout, reference_points);
  fout.close();

  fout.open(output_kde2d_fname);
  write_2dgrid_values(fout, grid2d, 
                      start2d_x, end2d_x, steps2d_x,
                      start2d_y, end2d_y, steps2d_y);
  fout.close();

  fout.open(output_kde1d_x_fname);
  write_1dpoint_values(fout, grid1d_x);
  fout.close();

  fout.open(output_kde1d_y_fname);
  write_1dpoint_values(fout, grid1d_y);
  fout.close();


  std::cout << "+ done. ";
  end_total = std::chrono::high_resolution_clock::now();
  elapsed = end_total - start_total;
  std::cout << "total running time: " << elapsed.count() << " s. \n" << std::endl;

}

