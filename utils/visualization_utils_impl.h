#include <vector>
#include <cmath>
#include <ostream>
#include <fstream>
#include <random>
#include <algorithm>
#include <utility>

#include "general_utils.h"

template <typename PointT>
void generate_1dgrid(
    std::vector<PointT> &grid, 
    double start_x, double end_x, int steps_x) {
  
  grid.clear();

  double delta_x = (end_x - start_x) / steps_x;

  double x_coord;
  for (int i = 0; i < steps_x; ++i) {
    x_coord = start_x + i * delta_x;
    PointT p = {{ x_coord }};
    grid.push_back(p);
  }

}

template<typename PointT>
void write_1dpoint_values(std::ostream &os, std::vector<PointT> points) {

  // not strictly necessary, but good for consistency with other write methods. 
  std::sort(points.begin(), points.end(), ReverseExactLexicoLess<PointT>);

  // two columns: x, value
  for (size_t i = 0; i < points.size(); ++i) {
    os << points[i][0] << " ";
    os << points[i].attributes().value();
    os << std::endl;
  }

}


template <typename PointT>
void generate_2dgrid(std::vector<PointT> &grid, 
                     double start_x, double end_x, int steps_x,
                     double start_y, double end_y, int steps_y) {
  
  grid.clear();

  double delta_x = (end_x-start_x)/steps_x;
  double delta_y = (end_y-start_y)/steps_y;
  for (int j = 0; j <= steps_y; ++j) {
    for (int i = 0; i <= steps_x; ++i) {
      grid.push_back({{start_x+i*delta_x, start_y+j*delta_y}});
    }
  }

  return;
}


template<typename PointT>
void write_2dgrid_values(std::ostream &os, std::vector<PointT> &point_values,
                         double start_x, double end_x, int steps_x, 
                         double start_y, double end_y, int steps_y) {

  std::sort(point_values.begin(), point_values.end(), ReverseExactLexicoLess<PointT>);
  std::vector<double> values(point_values.size());
  for (size_t i = 0; i < point_values.size(); ++i) {
    values[i] = point_values[i].attributes().value();
  }
  write_2dgrid_values(os, static_cast<const std::vector<double>>(values), 
                      start_x, end_x, steps_x, start_y, end_y, steps_y);
}


inline 
void write_2dgrid_values(std::ostream &os, std::vector<double> &values,
                         double start_x, double end_x, int steps_x, 
                         double start_y, double end_y, int steps_y) {
  write_2dgrid_values(os, static_cast<const std::vector<double>>(values), 
                      start_x, end_x, steps_x, start_y, end_y, steps_y);
}


template<typename PointT>
void write_2dscatter_data(std::ostream &os, const std::vector<PointT> &data) {
  for (const auto &p : data) { os << p[0] << " " << p[1] << std::endl; }
}
