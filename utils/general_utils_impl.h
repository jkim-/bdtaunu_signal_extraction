#include <vector>
#include <cmath>
#include <ostream>
#include <fstream>
#include <random>
#include <algorithm>
#include <utility>

template<typename PointT>
std::vector<PointT> read_2dpoints(const std::string &fname) {

  // open file
  std::ifstream fin(fname);
  if (!fin) {
    throw std::ios_base::failure("cannot open file " + fname + ". ");
  }

  // populate points
  std::vector<PointT> points;
  double x1 = 0.0, x2 = 0.0, w = 1.0;
  while (fin >> x1 >> x2 >> w) {
    points.push_back({{x1,x2}, {w}});
  }

  return points;

}

template<typename PointT>
bool ReverseExactLexicoLess(const PointT &lhs, const PointT &rhs) {
  int i = 0; while (i < lhs.dim() && lhs[lhs.dim()-i-1] == rhs[lhs.dim()-i-1]) { ++i; }
  return i != lhs.dim() && lhs[lhs.dim()-i-1] < rhs[lhs.dim()-i-1];
}

