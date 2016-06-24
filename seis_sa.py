from pylab import *
from glob import glob
from mpl_toolkits.axes_grid1 import make_axes_locatable

files = glob("gmrotD50*")

clims = [0.1, 0.25, 0.5, 1.0, 1.0, 1.0, 1.0]
for i, file in enumerate(files):
    fig = figure()
    ax = fig.gca()
    name = file[:-4]
    sa = loadtxt(file).reshape([2800,1600])
    im = imshow(sa.T/9.81, origin='normal')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = colorbar(im, cax=cax)
    cbar.solids.set_rasterized(True)
    cbar.solids.set_edgecolor("face")
    cbar.set_label(label='SA (g)', size=12)
    clim([0,clims[i]])
    savefig('./' + name + '.pdf')
    


    
