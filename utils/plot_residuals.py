import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.stats import binned_statistic

def plot_residuals(data, weights, range, fit, proportions, title, x_label, dataset, fname=None):
    fsize = 18
    fig = plt.figure(figsize=(8*1.618,8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    ax = fig.add_subplot(gs[0])
    ax.set_title(title, fontsize=fsize)
    
    step = 0.5*(fit[1,0] - fit[0,0])
    data_bin_counts, bin_edges = np.histogram(data, bins=100, weights=weights,
                                              normed=True, range=(range[0]-step,range[1]-step))
    stacked_counts = [np.sum(x[1:]*proportions) for x in fit]
    sum_n = np.sum(weights)
    bin_result = binned_statistic(data, weights, 
                                  statistic=lambda lst: ((sum_n-np.sum(lst))/sum_n**2/(2*step))**2*np.dot(lst,lst),
                                  bins=100, range=(range[0]-step,range[1]-step))
    
    ax.errorbar(0.5*(bin_edges[:-1] + bin_edges[1:]), data_bin_counts, 
                yerr=np.sqrt(bin_result.statistic), fmt='.', color='black', label=dataset)
    ax.plot(fit[:,0], stacked_counts, lw=1.5, color='r', label='MC')
    ax.set_xlabel(x_label, fontsize=fsize)
    ax.set_ylabel('Density', fontsize=fsize)
    ax.set_xlim(range[0], range[1])
    ax.set_ylim(0)
    ax.legend(prop={'size':fsize})
    ax.tick_params(length=8, width=1, labelsize=fsize)
    
    ax = fig.add_subplot(gs[1])
    diff_counts = [(x-y)/y for x,y in zip(data_bin_counts, stacked_counts)]
    #diff_errors = [(z/x**2)*dx for dx,x,z in zip(np.sqrt(bin_result.statistic), data_bin_counts, diff_counts)]
    diff_errors = [dx/y for dx,y in zip(np.sqrt(bin_result.statistic), stacked_counts)]
    ax.errorbar(fit[:,0], diff_counts, yerr=diff_errors, color='black', fmt='.')
    ax.set_xlabel(x_label, fontsize=fsize)
    ax.set_ylabel('(MC-{0})/{0}'.format(dataset), fontsize=fsize)
    ax.set_xlim(range[0], range[1])
    ax.set_ylim(-0.3,0.3)
    ax.tick_params(length=8, width=1, labelsize=fsize-1)
    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    
    if fname: plt.savefig(fname, format='pdf', bbox_inches='tight')
