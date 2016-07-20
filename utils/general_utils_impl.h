#include <vector>
#include <cmath>
#include <iostream>
#include <fstream>
#include <random>
#include <algorithm>
#include <utility>
#include <string>

#include <boost/tokenizer.hpp>

template<typename PointT>
std::vector<PointT> read_2dpoints(const std::string &fname) {

  // open file
  std::ifstream fin(fname);
  if (!fin) {
    throw std::ios_base::failure("cannot open file " + fname + ". ");
  }

  // initialize tokenizer
  typedef boost::tokenizer<boost::char_separator<char> > tokenizer;
  boost::char_separator<char> sep(" ");

  // populate points 
  std::vector<PointT> points;
  std::vector<double> column_values; column_values.reserve(3);

  // for each line, tokenize and read each column. if there are 2 columns,
  // assume they are x1, x2, set weight equal to 1. if there are 3, assume
  // the last column is the weight. throw an error otherwise. 
  std::string line;
  while (std::getline(fin, line)) {

    // populate the coordinates and weights
    column_values.clear();
    
    int icol = 0; 
    tokenizer tokens(line, sep);
    for (tokenizer::iterator tok_iter = tokens.begin();
         tok_iter != tokens.end(); ++tok_iter) {
      column_values[icol] = std::stod(*tok_iter);
      ++icol;
    }
    if (icol == 2) { column_values[icol] = 1.0; }

    // check whether the number of columns is value 
    if (icol < 2 && icol > 3) {
      throw std::runtime_error(
          "read_2dpoints: must have at most 3 but at least 2 columns per line. "
      );
    }

    points.push_back({{column_values[0],column_values[1]},{column_values[2]}});

  }

  return points;

}

template<typename PointT>
bool ReverseExactLexicoLess(const PointT &lhs, const PointT &rhs) {
  int i = 0; while (i < lhs.dim() && lhs[lhs.dim()-i-1] == rhs[lhs.dim()-i-1]) { ++i; }
  return i != lhs.dim() && lhs[lhs.dim()-i-1] < rhs[lhs.dim()-i-1];
}

