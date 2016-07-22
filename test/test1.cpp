#include <iostream>
#include <fstream>
#include <vector>
#include <cassert>
#include <cmath>

#include <boost/tokenizer.hpp>

std::vector<std::vector<double>> read_cached(const std::string &fname) {

  // open file
  std::ifstream fin(fname);
  if (!fin) {
    throw std::ios_base::failure("cannot open file " + fname + ". ");
  }

  // initialize tokenizer
  typedef boost::tokenizer<boost::char_separator<char> > tokenizer;
  boost::char_separator<char> sep(" ");

  // populate points
  std::vector<std::vector<double>> points;
  std::vector<double> column_values; column_values.reserve(5);

  std::string line;
  while (std::getline(fin, line)) {

    // populate the coordinates and weights
    column_values.clear();

    int icol = 0;
    tokenizer tokens(line, sep);
    for (tokenizer::iterator tok_iter = tokens.begin();
         tok_iter != tokens.end(); ++tok_iter) {
      column_values.push_back(std::stod(*tok_iter));
      ++icol;
    }

    points.push_back(column_values);

  }

  return points;

}

template <typename T> 
void print_vector(std::ostream &os, std::vector<T> &vec) {
  for (const auto &v : vec) { os << v << " "; } os << std::endl;
}

int main() {

  std::vector<double> p = { 0.00527027038150278256, 0.01025836847255434590, 0.09760324684671536023, 0.38860905629706645394, 0.49825905800216105737};
  //std::vector<double> p = {1.355407273260908e-05, 1.7690107823617702e-10, 0.5169433838540646, 4.213379872835633e-10, 0.4830430614749636};
  //std::vector<double> p = {0.0018619383784078706, 4.173055996280018e-09, 0.4998789891119579, 1.0334417133468883e-08, 0.4982590580021611};
  std::vector<std::vector<double>> f = read_cached("mod_cached_density_evaluations.csv");
  //std::vector<std::vector<double>> f = read_cached("small.csv");
  double l = 0;
  for (size_t i = 0; i < f.size(); ++i) {
    double arg = 0;
    for (size_t j = 0; j < p.size(); ++j) {
      arg += p[j] * f[i][j];
      //std::cout << f[i][j] << " ";
    }
    //std::cout << arg << " ";
    l += -std::log(arg);
    assert(std::isfinite(-std::log(arg)));
    //std::cout << std::log(arg) << std::endl;;
  }

  std::cout << l*1e-8 << std::endl;

  return 0;
}
