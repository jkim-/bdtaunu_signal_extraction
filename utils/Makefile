OBJECTS = visualization_utils.o custom_program_option_utils.o 

SRCS = $(wildcard *.cc *.cpp)

LIBDIR = lib
LIBNAME = libutils.so

BOOST_ROOT = /usr/local/boost_1_59_0
BOOST_LIBS = $(BOOST_ROOT)/stage/lib

INCFLAGS = -I$(BOOST_ROOT)

CXX := g++
CXXFLAGS = -Wall -Werror -fPIC -pedantic -pthread -std=c++11 -O2

DEPDIR = .d
$(shell mkdir -p $(DEPDIR) > /dev/null)
DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.Td
POSTCOMPILE = @mv -f $(DEPDIR)/$*.Td $(DEPDIR)/$*.d

all : lib

lib : $(addprefix $(LIBDIR)/, $(OBJECTS))
	if [ "$(shell uname)" = "Darwin" ]; then \
    SHARED_LIB_FLAG="-dynamiclib -Wl,-install_name,@rpath/$(LIBNAME)"; \
  else \
    SHARED_LIB_FLAG="-shared -Wl,-soname,$(LIBNAME)"; \
  fi; \
	$(CXX) $${SHARED_LIB_FLAG} $^ -o $(addprefix $(LIBDIR)/, $(LIBNAME))

$(LIBDIR)/%.o : %.cpp
$(LIBDIR)/%.o : %.cpp $(DEPDIR)/%.d
	$(CXX) $(DEPFLAGS) $(CXXFLAGS) $(INCFLAGS) -c $< -o $@
	$(POSTCOMPILE)

$(DEPDIR)/%.d: ;

.PRECIOUS: $(DEPDIR)/%.d

-include $(patsubst %,$(DEPDIR)/%.d,$(basename $(SRCS)))

clean : 
	@rm -f *~ $(LIBDIR)/*

cleanall : clean
	@rm -f $(DEPDIR)/* 
