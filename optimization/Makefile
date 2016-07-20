BINARIES = precompute_component_densities

OBJECTS = 

SRCS = $(wildcard *.cc *.cpp)

SYMLINKS = data

CUDA_ROOT = /usr/local/cuda-7.5
CUDA_LIBS = $(CUDA_ROOT)/lib64

BOOST_ROOT = /usr/local/boost_1_59_0
BOOST_LIBS = $(BOOST_ROOT)/stage/lib

BBRCITKDE_ROOT = /home/dchao/workspace/bbrcit_kde

SIGNAL_EXTRACTION_ROOT = /home/dchao/workspace/bdtaunu_signal_extraction
SIGNAL_EXTRACTION_UTILS_LIBS = $(SIGNAL_EXTRACTION_ROOT)/utils/lib

INCFLAGS = -I$(BBRCITKDE_ROOT)/include -I$(BOOST_ROOT) \
					 -I$(SIGNAL_EXTRACTION_ROOT)
LDFLAGS = -L$(CUDA_LIBS) -lcudart \
          -L$(BOOST_LIBS) -lboost_program_options \
					-L$(SIGNAL_EXTRACTION_UTILS_LIBS) -lutils \
					-Wl,-rpath,$(BOOST_LIBS) \
					-Wl,-rpath,$(SIGNAL_EXTRACTION_UTILS_LIBS)


BUILDDIR = build

CXX := g++
CXXFLAGS = -Wall -Werror -pedantic -pthread -std=c++11 -O2

DEPDIR = .d
$(shell mkdir -p $(DEPDIR) > /dev/null)
DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.Td
POSTCOMPILE = @mv -f $(DEPDIR)/$*.Td $(DEPDIR)/$*.d

NVCC := nvcc -ccbin=$(CXX)
NVCCFLAGS = -std=c++11 -O2 -arch=sm_35 -x cu
NVCCMAKEDEP = @$(NVCC) -M -MT $@ $(NVCCFLAGS) $(INCFLAGS) $< -o\
							$(patsubst $(BUILDDIR)/%.o, $(DEPDIR)/%.d, $@)


all : $(BINARIES) $(SYMLINKS)

data : 
	ln -s $(SIGNAL_EXTRACTION_ROOT)/data data

precompute_component_densities : $(addprefix $(BUILDDIR)/, precompute_component_densities.o $(OBJECTS))
	$(CXX) $^ $(LDFLAGS) -o $@

$(BUILDDIR)/%.o : %.cpp
$(BUILDDIR)/%.o : %.cpp $(DEPDIR)/%.d
	$(CXX) $(DEPFLAGS) $(CXXFLAGS) $(INCFLAGS) -c $< -o $@
	$(POSTCOMPILE)

$(BUILDDIR)/%.o : %.cc
$(BUILDDIR)/%.o : %.cc $(DEPDIR)/%.d
	$(NVCCMAKEDEP)
	$(NVCC) $(NVCCFLAGS) $(INCFLAGS) -c $< -o $@

$(DEPDIR)/%.d: ;

.PRECIOUS: $(DEPDIR)/%.d

-include $(patsubst %,$(DEPDIR)/%.d,$(basename $(SRCS)))

clean : 
	@rm -f *~ $(BINARIES) $(BUILDDIR)/* data

cleanall : clean
	@rm -f $(DEPDIR)/* *.csv
