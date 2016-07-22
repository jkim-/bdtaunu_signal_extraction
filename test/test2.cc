#include <iostream>
#include <fstream>
#include <vector>
#include <cassert>
#include <cmath>
#include <chrono>
#include <string>
#include <utility>
#include <iomanip>

#include <KernelDensity.h>

#include <utils/general_utils.h>
#include <utils/KdeEvalContainer.h>

template <typename T> 
void print_vector(std::ostream &os, std::vector<T> &vec) {
  for (const auto &v : vec) { os << v << " "; } os << std::endl;
}

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

double f(const std::vector<std::pair<double,double>> &x,
         std::vector<KernelDensityType> &kdes, KdtreeType &qtree, 
         const std::vector<double> &p, 
         double rel_tol, double abs_tol, size_t gpu_block_size) {

  size_t n_components = kdes.size();

  // save current bandwidths
  std::vector<std::pair<double,double>> curr_bw;
  for (int j = 0; j < n_components; ++j) {
    curr_bw.push_back({kdes[j].kernel().hx(), kdes[j].kernel().hy()});
    kdes[j].kernel().set_hx(x[j].first); 
    kdes[j].kernel().set_hy(x[j].second);
  }

  // evaluate densities
  KdeEvalContainer results(qtree.size(), n_components);
  for (int j = 0; j < n_components; ++j) {

    // evaluate kernel density
    kdes[j].eval(qtree, rel_tol, abs_tol, gpu_block_size);

    // save results
    results.write_column(j, qtree.points(), false);

  }

  // accumulate log likelihood 
  double l = 0;
  for (size_t i = 0; i < results.m(); ++i) {
    double arg = 0;
    for (size_t j = 0; j < n_components; ++j) {
      arg += results[i][j] * p[j];
    }
    l += -std::log(arg);
  }

  // restore bandwidths
  for (int j = 0; j < n_components; ++j) {
    kdes[j].kernel().set_hx(curr_bw[j].first);
    kdes[j].kernel().set_hy(curr_bw[j].second);
  }

  return l;
}

int main() {

  // timers and configurations
  std::chrono::high_resolution_clock::time_point start, end;
  std::chrono::duration<double> elapsed;

  double rel_tol = 1e-6, abs_tol = 1e-8;
  size_t max_leaf_size = 32768;
  size_t gpu_block_size = 128;

  // query points
  std::cout << "+ constructing sample query tree. \n";
  start = std::chrono::high_resolution_clock::now();
  KdtreeType qtree = 
    construct_query_tree("test.small.csv", 32768);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start; 
  std::cout << "  running time: " << elapsed.count() << " s. \n" << std::endl;

  // component kdes
  std::vector<std::string> input_component_fnames = { 
    "data/evttype1.train.csv", "data/evttype2.train.csv", 
    "data/evttype3.train.csv", "data/evttype4.train.csv", 
    "data/evttype5.train.csv" };
  std::vector<double> alphas = { 0.0, 0.0, 0.0, 0.0, 0.0 };
  std::vector<double> pilot_bxs = { 0.0, 0.0, 0.0, 0.0, 0.0 };
  std::vector<double> pilot_bwxs = { 0.1, 0.09, 0.092, 0.075, 0.084 };
  std::vector<double> pilot_bwys = { 0.1, 0.09, 0.065, 0.057, 0.057 };
  std::vector<double> adapt_bwxs = { 0.1, 0.09, 0.092, 0.075, 0.084 };
  std::vector<double> adapt_bwys = { 0.1, 0.09, 0.065, 0.057, 0.057 };

  std::vector<double> p = { 
    0.00527027038150278256, 
    0.01025836847255434590, 
    0.09760324684671536023, 
    0.38860905629706645394, 
    0.49825905800216105737 
  };

  size_t n_components = input_component_fnames.size();

  // coonstruct kernel densities
  std::cout << "+ building kernel densities. " << std::endl;
  std::vector<KernelDensityType> kdes(n_components);
  start = std::chrono::high_resolution_clock::now();
  for (size_t j = 0; j < n_components; ++j) {
    kdes[j] = 
      construct_kernel_density(
          input_component_fnames[j], alphas[j], 
          pilot_bwxs[j], pilot_bwys[j], 
          adapt_bwxs[j], adapt_bwys[j], 
          rel_tol, abs_tol, max_leaf_size, gpu_block_size);
    end = std::chrono::high_resolution_clock::now();
  }
  elapsed = end - start; 
  std::cout << "  running time: " << elapsed.count() << " s. \n" << std::endl;

  std::vector<std::pair<double,double>> x;
  for (size_t j = 0; j < n_components; ++j) {
    x.push_back({adapt_bwxs[j], adapt_bwys[j]});
  }

  std::cout << std::setprecision(13) << std::fixed;

  for (int t = 0; t < 10; ++t) {

    std::cout << "Iteration " << t << ": ";
    start = std::chrono::high_resolution_clock::now();

    double l = f(x, kdes, qtree, p, rel_tol, abs_tol, gpu_block_size);

    end = std::chrono::high_resolution_clock::now();

    elapsed = end - start;
    std::cout << l << ", in " << elapsed.count() << " s. " << std::endl;

  }

  std::cout << std::endl;

  return 0;
}
