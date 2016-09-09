#BBRKDE_ROOT = /home/dchao/workspace/bbrcit_kde
BBRKDE_ROOT = /home/jkim/Analysis/bbrcit_kde

all : 
	$(MAKE) -C $(BBRKDE_ROOT)/grid_search
	ln -s $(BBRKDE_ROOT)/grid_search/grid_search grid_search
	ln -s ../data data
	ln -s ../utils utils

clean: 
	@rm -rf grid_search data utils

cleanall: clean
	@$(MAKE) -C $(BBRKDE_ROOT)/grid_search clean
	@rm -rf *.csv *.out
