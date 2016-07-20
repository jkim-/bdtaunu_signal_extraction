import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

def plot_data1d(data1d_fname, ax=None, xlim=None, linestyle='-', marker=None,
                title=None, xlabel=None, axis_fontsize=20, tick_labelsize=16, 
                orientation='vertical'):

    # read in the data file
    data = np.genfromtxt(data1d_fname)

    # plot the data
    if ax is None: ax = plt.gca()
    if orientation == 'vertical':
        ax.plot(data[:,0],data[:,1], linestyle=linestyle, marker=marker)
    elif orientation == 'horizontal':
        ax.plot(data[:,1],data[:,0], linestyle=linestyle, marker=marker)
    else:
        raise RuntimeError("orientation must be 'vertical' or 'horizontal'. ")

    if xlim:
        ax.set_xlim(xlim)


    # customize axis labels
    ax.tick_params(axis='both', which='major', labelsize=tick_labelsize)
    if title:
        ax.set_title(title, fontsize=axis_fontsize)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_fontsize)
    else:
        ax.set_xlabel(r'$X_1$', fontsize=axis_fontsize)


# plot 1d data histrogram using evenly sized bins. 
def plot_data1d_histogram(sample, bins=20, weights=None, normed=False, xlim=None,
                          ax=None, marker='.', color='k', linestyle='None', 
                          title=None, xlabel=None, axis_fontsize=20, tick_labelsize=16, 
                          orientation='vertical'):
    
    # produce the unnormalized histrogram and assign plot coordinates
    y, edges = np.histogram(sample, bins)
    x = (edges[:-1]+edges[1:])*0.5
    
    
    # compute error bar
    y_err = np.sqrt(y)
    
    # if normed is requested, then convert the output into a density
    if normed:
        
        # compute average bin width. perhaps overkill, but no better idea
        bw = np.sum(edges[1:]-edges[:-1])/len(edges[:-1])
        
        # compute density error bar: assume bins are independent and Poisson
        s = np.sum(y)
        y_err = np.sqrt(
            y / (bw*bw*s*s) - y*y / (bw*bw*s*s*s) 
        )
        
        # compute density: density = count / total / binwidth
        y = y / (bw*s)
    
    
    # produce the plot
    if ax is None: ax = plt.gca()
    if orientation == 'vertical':
        ax.errorbar(x,y,yerr=y_err,linestyle=linestyle,marker=marker,color=color)
    elif orientation == 'horizontal':
        ax.errorbar(y,x,xerr=y_err,linestyle=linestyle,marker=marker,color=color)
    else:
        raise RuntimeError("orientation must be 'vertical' or 'horizontal'. ")

    if xlim: ax.set_xlim(xlim)

    # customize axis labels
    ax.tick_params(axis='both', which='major', labelsize=tick_labelsize)
    if title:
        ax.set_title(title, fontsize=axis_fontsize)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_fontsize)
    else:
        ax.set_xlabel(r'$X_1$', fontsize=axis_fontsize)
    
    return ax


def plot_data2d(data2d_fname, undersample=1.0, s=20,
                marker='o', color='b', edgecolor='None', alpha=1.0, 
                ax=None, xlim=None, ylim=None, xlabel=None, ylabel=None,
                title=None, axis_fontsize=20, tick_labelsize=16):

    # read in the specialized data file
    data = np.genfromtxt(data2d_fname)
    
    # undersample if requested
    if undersample < 1.0:
        n_total = data.shape[0]
        data = data[np.random.choice(n_total, int(n_total*undersample))]

    # plot the data
    if ax is None: ax = plt.gca()
    ax.scatter(data[:,0],data[:,1],marker=marker, color=color, edgecolor=edgecolor, alpha=alpha, s=s)

    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)

    # customize axis labels
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_fontsize)
    else:
        ax.set_xlabel(r'$X_1$', fontsize=axis_fontsize)
        
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_fontsize)
    else:
        ax.set_ylabel(r'$X_2$', fontsize=axis_fontsize)
        
    ax.tick_params(axis='both', which='major', labelsize=tick_labelsize)
    
    if title: ax.set_title(title, fontsize=axis_fontsize)

    return


def plot_contour2d(kde2d_fname, ax=None, colorbar=True,
                   vmin=None, vmax=None,
                   nlevels=10, nlevels_f=50,
                   linewidths=0.4,
                   title=None, axis_fontsize=20, tick_labelsize=16, 
                   xlabel=None, ylabel=None,
                   cmap=plt.cm.Blues, contour_fmt='%1.2f'):

    # read in the specialized file generated from kde_scan
    X, Y = None, None
    with open(kde2d_fname, 'r') as f:
        x = np.array(map(float, f.next().strip().split()))
        y = np.array(map(float, f.next().strip().split()))
        X, Y = np.meshgrid(x, y)
    Z = np.genfromtxt(kde2d_fname,skip_header=2)

    # plot the data
    if ax is None: ax = plt.gca()
    csf = ax.contourf(X, Y, Z, nlevels_f,
                      vmin=vmin,vmax=vmax,
                      cmap=cmap)
    cs = ax.contour(X, Y, Z, nlevels,linewidths=linewidths, colors='k', linestyles='--')


    # custimize contour labels
    if colorbar:
        cbar = plt.gcf().colorbar(csf)
        cbar.ax.tick_params(labelsize=axis_fontsize)
    ax.clabel(cs, inline=1, fmt=contour_fmt, fontsize=axis_fontsize);

    # customize axis labels
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_fontsize)
    else:
        ax.set_xlabel(r'$X_1$', fontsize=axis_fontsize)
        
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_fontsize)
    else:
        ax.set_ylabel(r'$X_2$', fontsize=axis_fontsize)

    ax.tick_params(axis='both', which='major', labelsize=tick_labelsize)
    if title:
        ax.set_title(title, fontsize=axis_fontsize)

    return


# draw kde2d summary: center plot has 2d scatter and contour plots
# while top and right plots have marginal projections. 
def plot_kde2d_summary(
    data2d_fname,kde2d_fname, kde1d_x_fname, kde1d_y_fname, 
    title=None,
    xlabel=None, ylabel=None,
    draw_scatter=True,
    scatter_color='grey', scatter_marker='o', 
    scatter_undersample=1.0, scatter_s=20, scatter_alpha=0.5, 
    contour_nlevels=10, 
    data1d_x_bins=100, 
    data1d_y_bins=100, 
    figsize=(12,12), xlim=None, ylim=None):
    
    # define axes dimensions
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_c = [left, bottom, width, height]
    rect_x = [left, bottom_h, width, 0.18]
    rect_y = [left_h, bottom, 0.2, height]

    # create plot area
    fig = plt.figure(1, figsize=figsize)

    ax_c = plt.axes(rect_c)
    ax_x = plt.axes(rect_x)
    ax_y = plt.axes(rect_y)
    
    nullfmt = NullFormatter() 
    ax_x.xaxis.set_major_formatter(nullfmt)
    ax_y.yaxis.set_major_formatter(nullfmt)
    
    
    # draw center contour plot
    plot_contour2d(kde2d_fname, ax=ax_c, 
                   nlevels=contour_nlevels, colorbar=False,
                   xlabel=xlabel, ylabel=ylabel)
    
    # draw center scatter plot
    if draw_scatter:
        plot_data2d(data2d_fname, ax=ax_c, 
                    color=scatter_color, marker=scatter_marker, 
                    undersample=scatter_undersample, s=scatter_s, alpha=scatter_alpha)

    # draw marginal densities
    plot_data1d(kde1d_x_fname, ax=ax_x, xlabel=' ')
    plot_data1d(kde1d_y_fname, ax=ax_y, xlabel=' ', orientation='horizontal')
    
    # draw marginal histograms
    arr = np.genfromtxt(data2d_fname)
    plot_data1d_histogram(arr[:,0], weights=arr[:,2], bins=data1d_x_bins, 
                          normed=True, ax=ax_x, xlabel=' ');
    plot_data1d_histogram(arr[:,1], weights=arr[:,2], bins=data1d_y_bins, 
                          normed=True, ax=ax_y, xlabel=' ', orientation='horizontal');
    
    ax_c.set_xlim(xlim)
    ax_c.set_ylim(ylim)
    ax_x.set_xlim(ax_c.get_xlim())
    ax_y.set_ylim(ax_c.get_ylim())
    
    if title:
        fig.suptitle(title, fontsize=20)
    
    return fig, ax_c, ax_x, ax_y
