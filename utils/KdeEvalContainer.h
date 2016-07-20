#ifndef __KDEEVALCONTAINER_H__
#define __KDEEVALCONTAINER_H__

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>

// class whose objects store evaluation result of 
// the kernel density components. 
class KdeEvalContainer {

  public: 

    // write the contents to output stream
    friend std::ostream& operator<<(
        std::ostream &os, const KdeEvalContainer &r) {
      for (size_t i = 0; i < r.m(); ++i) { 
        for (size_t j = 0; j < r.n(); ++j) { 
          os << r[i][j] << " ";
        }
        os << std::endl;
      }
      return os;
    }

  public: 
    KdeEvalContainer() : m_(0), n_(0), results_() {}
    KdeEvalContainer(size_t m, size_t n) : 
      m_(m), n_(n), results_(m, std::vector<double>(n, 0.0)) {};

    KdeEvalContainer(const KdeEvalContainer&) = default;
    KdeEvalContainer(KdeEvalContainer&&) = default;
    ~KdeEvalContainer() = default;
    KdeEvalContainer& operator=(const KdeEvalContainer&) = default;
    KdeEvalContainer& operator=(KdeEvalContainer&&) = default;

    // get the dimensions.
    size_t m() const { return m_; }
    size_t n() const { return n_; }

    // get a reference to the `i`th row. 
    const std::vector<double>& operator[](size_t i) const {
      return results_[i];
    }
    std::vector<double>& operator[](size_t i) {
      return const_cast<std::vector<double>&>(
          static_cast<const KdeEvalContainer&>(*this)[i]);
    }

    // copy the evaluation results of PointT objects in `source` 
    // into the `j`th column. 
    template<typename PointT> 
    void write_column(size_t j, std::vector<PointT> source, 
                      bool sort_rows) {
      if (source.size() != m_) { 
        throw std::range_error(
            "KdeEvalContainer::write_column(...): source vector should have "
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

#endif
