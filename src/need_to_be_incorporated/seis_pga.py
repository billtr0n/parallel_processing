from pylab import *
from glob import glob
from mpl_toolkits.axes_grid1 import make_axes_locatable

files = ['peak_acceleration_Z.bin','peak_acceleration_H.bin']

for i, file in enumerate(files):
    fig = figure()
    ax = fig.gca()
    name = file[:-4]
    pga = fromfile(file,'f').reshape([1600,2800])
    im = imshow(pga, origin='normal')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = colorbar(im, cax=cax)
    cbar.solids.set_rasterized(True)
    cbar.solids.set_edgecolor("face")
    cbar.set_label(label='PGA (g)', size=12)
    clim(0,1.0)
    savefig('./' + name + '.pdf')
    


    
