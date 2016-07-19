#ifndef __VISUALIZATION_UTILS_H__
#define __VISUALIZATION_UTILS_H__

#include <vector>
#include <ostream>
#include <string>
#include <utility>

// generate a 1-dimensional grid of points. 
template <typename PointT>
void generate_1dgrid(std::vector<PointT> &grid, 
                     double start_x, double end_x, int steps_x);

// write 1-dimensional point values 
template<typename PointT>
void write_1dpoint_values(std::ostream &os, std::vector<PointT> points);


// generate a 2-dimensional grid of points. 
template <typename PointT>
void generate_2dgrid(std::vector<PointT> &grid, 
                     double start_x, double end_x, int steps_x,
                     double start_y, double end_y, int steps_y);

// write 2-dimensional values attached to grid points generated using
// a call to `generate_2dgrid(...)` with arguments `(start|end|steps)_(x|y)`.
void write_2dgrid_values(std::ostream &os, const std::vector<double> &values,
                         double start_x, double end_x, int steps_x, 
                         double start_y, double end_y, int steps_y);
template<typename PointT>
void write_2dgrid_values(std::ostream &os, std::vector<PointT> &point_values,
                         double start_x, double end_x, int steps_x, 
                         double start_y, double end_y, int steps_y);


// write 2-dimensional points in `data` to output stream `os`. 
// each row corresponds to a single point whose value in the 
// `i`th dimension corresponds to the value in column `i`. 
template<typename PointT>
void write_2dscatter_data(std::ostream &os, const std::vector<PointT> &data);


#include "visualization_utils_impl.h"

#endif
