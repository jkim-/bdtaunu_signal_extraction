SYMLINKS = grid_search data utils

all : $(SYMLINKS)

grid_search :
	ln -s ../grid_search grid_search

data : 
	ln -s ../data data

utils :
	ln -s ../utils utils

clean : 
	@rm -f $(SYMLINKS) 

cleanall : 
	@rm -f $(SYMLINKS) *.csv *.out
