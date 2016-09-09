SYMLINKS = data custom_python_utilities \
					 mle_cvxnl.py precompute_component_densities \
					 condor_mle_cvxnl.py collect_condor_mle_cvxnl_results.py \
					 poll_results.py

all : $(SYMLINKS)

data : 
	ln -s ../data data

custom_python_utilities : 
	ln -s ../custom_python_utilities custom_python_utilities

precompute_component_densities : 
	ln -s ../precompute_component_densities precompute_component_densities

mle_cvxnl.py : 
	ln -s ../mle_cvxnl.py mle_cvxnl.py
	
condor_mle_cvxnl.py : 
	ln -s ../condor_mle_cvxnl.py condor_mle_cvxnl.py

collect_condor_mle_cvxnl_results.py : 
	ln -s ../collect_condor_mle_cvxnl_results.py collect_condor_mle_cvxnl_results.py

poll_results.py :
	ln -s ../poll_results.py poll_results.py

clean : 
	@rm -f $(SYMLINKS)
