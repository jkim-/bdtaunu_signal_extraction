#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>

#include <KernelDensity.h>

#include <boost/program_options.hpp>

#include <utils/custom_program_option_utils.h>
#include <utils/general_utils.h>

namespace po = boost::program_options;

namespace {
  using KernelType = bbrcit::EpanechnikovProductKernel2d<float>;
  using KernelDensityType = bbrcit::KernelDensity<2,KernelType,double>;
  using KdtreeType = KernelDensityType::KdtreeType;
  using DataPointType = KernelDensityType::DataPointType;
}

// construct a query tree using data in `fname` 
KdtreeType construct_query_tree(const std::string fname, int leaf_max) {
  std::vector<DataPointType> points = read_2dpoints<DataPointType>(fname);
  KdtreeType qtree(std::move(points), leaf_max);
  return qtree;
}

// construct (adapted) kernel density using data in `fname`
KernelDensityType construct_kernel_density(
  const std::string fname, double alpha, 
  double pilot_bandwidth_x, double pilot_bandwidth_y, 
  double adapt_bandwidth_x, double adapt_bandwidth_y, 
  double rel_tol, double abs_tol, 
  int leaf_max, int block_size) {

  std::vector<DataPointType> points = read_2dpoints<DataPointType>(fname);

  KernelDensityType kde(std::move(points), leaf_max);
  kde.kernel().set_bandwidths(pilot_bandwidth_x, pilot_bandwidth_y);
  kde.adapt_density(alpha, rel_tol, abs_tol, block_size);
  kde.kernel().set_bandwidths(adapt_bandwidth_x, adapt_bandwidth_y);

  return kde;
}

// class whose objects store evaluation result of 
// the kernel density components. 
class EvalResults {

  public: 

    // write the contents to output stream
    friend std::ostream& operator<<(
        std::ostream &os, const EvalResults &r) {
      for (size_t i = 0; i < r.m(); ++i) { 
        for (size_t j = 0; j < r.n(); ++j) { 
          os << r[i][j] << " ";
        }
        os << std::endl;
      }
      return os;
    }

  public: 
    EvalResults() : m_(0), n_(0), results_() {}
    EvalResults(size_t m, size_t n) : 
      m_(m), n_(n), results_(m, std::vector<double>(n, 0.0)) {};

    EvalResults(const EvalResults&) = default;
    EvalResults(EvalResults&&) = default;
    ~EvalResults() = default;
    EvalResults& operator=(const EvalResults&) = default;
    EvalResults& operator=(EvalResults&&) = default;

    // get the dimensions.
    size_t m() const { return m_; }
    size_t n() const { return n_; }

    // get a reference to the `i`th row. 
    const std::vector<double>& operator[](size_t i) const {
      return results_[i];
    }
    std::vector<double>& operator[](size_t i) {
      return const_cast<std::vector<double>&>(
          static_cast<const EvalResults&>(*this)[i]);
    }

    // copy the evaluation results of PointT objects in `source` 
    // into the `j`th column. 
    template<typename PointT> 
    void write_column(size_t j, std::vector<PointT> source, 
                      bool sort_rows) {
      if (source.size() != m_) { 
        throw std::range_error(
            "EvalResults::write_column(...): source vector should have "
            "the same length as the column of `this` result matrix. ");
      }

      // sort the output by point coordinates. required to keep row ordering 
      // across separate invocations of `main()`. 
      if (sort_rows) {
        std::sort(source.begin(), source.end(), ReverseExactLexicoLess<PointT>);
      }

      for (size_t i = 0; i < m_; ++i) { 
        results_[i][j] = source[i].attributes().value();
      }

    }

  private:
    size_t m_, n_;
    std::vector<std::vector<double>> results_;
};


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
        ("input_sample_fname", po::value<std::string>(), "input path to the data sample. ")
        ("input_component_fnames", po::value<std::string>(), "input paths to the components. ")
        ("out_fname", po::value<std::string>(), "output file name. ")
        ("sort_rows", po::value<bool>(), "if true, sort output by point coordinates. "
                                         "this is required if row ordering should be "
                                         "the same across separate invocations. ")

        ("alphas", po::value<std::string>(), "sensitivity parameters. ")
        ("pilot_bwxs", po::value<std::string>(), "pilot bandwidths in x. ")
        ("pilot_bwys", po::value<std::string>(), "pilot bandwidths in y. ")
        ("adapt_bwxs", po::value<std::string>(), "evaluation bandwidths in x. ")
        ("adapt_bwys", po::value<std::string>(), "evaluation bandwidths in y. ")
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
  std::chrono::duration<double> elapsed_total;
  start_total = std::chrono::high_resolution_clock::now();

  std::chrono::high_resolution_clock::time_point start, end;
  std::chrono::duration<double> elapsed;

  // performance parameters
  int max_leaf_size = vm["max_leaf_size"].as<int>();
  double rel_tol = vm["rel_tol"].as<double>();
  double abs_tol = vm["abs_tol"].as<double>();

  std::cout << "+ performance parameters: \n" << std::endl;

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


  // 2. construct sample point query tree
  std::string input_data_dir = vm["input_data_dir"].as<std::string>();
  std::string input_sample_fname = vm["input_sample_fname"].as<std::string>();
  if (!input_data_dir.empty()) { 
    input_sample_fname = input_data_dir + "/" + input_sample_fname; 
  }

  std::cout << "+ constructing sample query tree with file: ";
  std::cout << input_sample_fname << std::endl;

  start = std::chrono::high_resolution_clock::now();
  KdtreeType qtree = 
    construct_query_tree(input_sample_fname, max_leaf_size);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start; 
  std::cout << "  running time: " << elapsed.count() << " s. \n" << std::endl;


  // 3. evaluate sample points 

  std::cout << "+ evaluate kernel density components over sample points. \n" << std::endl;
    
  // read in kde component configurations
  std::vector<std::string> input_component_fnames = 
    tokenize<std::string>(vm["input_component_fnames"].as<std::string>());
  std::vector<double> alphas = 
    tokenize<double>(vm["alphas"].as<std::string>());
  std::vector<double> pilot_bwxs = 
    tokenize<double>(vm["pilot_bwxs"].as<std::string>());
  std::vector<double> pilot_bwys = 
    tokenize<double>(vm["pilot_bwys"].as<std::string>());
  std::vector<double> adapt_bwxs = 
    tokenize<double>(vm["adapt_bwxs"].as<std::string>());
  std::vector<double> adapt_bwys = 
    tokenize<double>(vm["adapt_bwys"].as<std::string>());

  bool sort_rows = vm["sort_rows"].as<bool>();

  int n_components = input_component_fnames.size();

  for (int i = 0; i < n_components; ++i) {
    if (!input_data_dir.empty()) { 
      input_component_fnames[i] = input_data_dir + "/" + input_component_fnames[i];
    }
  }

  if (
      (alphas.size() != n_components) ||
      (pilot_bwxs.size() != n_components) ||
      (pilot_bwys.size() != n_components) ||
      (adapt_bwxs.size() != n_components) ||
      (adapt_bwys.size() != n_components)) {
    throw std::invalid_argument(
        "evaluate(): must have same number of " 
        "adaptive kernel parameters as there are kernels. ");
  }

  std::cout << "  will perform evaluation for the following components: \n" << std::endl;
  for (int i = 0; i < n_components; ++i) {
    std::cout << "  component " << i << ":" << std::endl;
    std::cout << "  file name: " << input_component_fnames[i] << std::endl;
    std::cout << "  alpha: " << alphas[i] << std::endl;
    std::cout << "  pilot bandwidths (x, y): " << pilot_bwxs[i] << ", " << pilot_bwys[i] << std::endl;
    std::cout << "  adaptive bandwidths (x, y): " << adapt_bwxs[i] << ", " << adapt_bwys[i] << std::endl;
    std::cout << std::endl;
  }

  std::cout << "  sort output rows by point coordinates: ";
  std::cout << (sort_rows ? "true" : "false") << "\n" << std::endl;

  // evaluation
  EvalResults results(qtree.size(), n_components);
  for (int j = 0; j < n_components; ++j) {

    // construct kernel density
    std::cout << "+ building kernel density for component " << j;
    std::cout << " using file: " << input_component_fnames[j] << std::endl;
    start = std::chrono::high_resolution_clock::now();
    KernelDensityType kde = 
      construct_kernel_density(
          input_component_fnames[j], alphas[j], 
          pilot_bwxs[j], pilot_bwys[j], 
          adapt_bwxs[j], adapt_bwys[j], 
          rel_tol, abs_tol, max_leaf_size, gpu_block_size);
    end = std::chrono::high_resolution_clock::now();
    elapsed = end - start; 
    std::cout << "  running time: " << elapsed.count() << " s. \n" << std::endl;

    // evaluate kernel density
    std::cout << "  evaluating over query samples for component " << j << std::endl;
    start = std::chrono::high_resolution_clock::now();
    kde.eval(qtree, rel_tol, abs_tol, gpu_block_size);
    end = std::chrono::high_resolution_clock::now();
    elapsed = end - start; 
    std::cout << "  running time: " << elapsed.count() << " s. \n" << std::endl;

    // save results
    results.write_column(j, qtree.points(), sort_rows);

  }

  // 4. write results to file
  std::string out_fname = vm["out_fname"].as<std::string>();
  std::cout << "+ writing results to file: " << out_fname << "\n" << std::endl;
  std::ofstream fout(out_fname);
  fout << results;

  // 5. done
  end_total = std::chrono::high_resolution_clock::now();
  elapsed_total = end_total - start_total;
  std::cout << "+ total runtime: " << elapsed_total.count() << " s.\n" << std::endl;

}
