import pylab as np 
import numpy.matlib as ml
import scipy.stats.mstats as mstats
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
# Define a class that forces representation of float to look a certain way
# This remove trailing zero so '1.0' becomes '1'
class nf(float):
    def __repr__(self):
        str = '%.1f' % (self.__float__(),)
        if str[-1] == '0':
            return '%.0f' % self.__float__()
        else:
            return '%.1f' % self.__float__()
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
# Recast levels to new class
    
nx = 2601
nz = 801 
dx = 25.
ex = nx*dx*1e-3
ez = nz*dx*1e-3
xo = 1201 
zo = 401
# loop through 10 models
for seed in [5]: 
    #model = './seed_%i_homostress' % seed
    # model = './seed_1_emb_1e-2.3_homo'
    # model = './seed_1_ts_0.75'
    # model = './seed_1_emb_1e-2.3_1d_incd0'
    # model = './seed-1_1e-2.3_rs_emb_1d_test'
    # model = './seed_1_emb_1d_0.3'
    # model = './seed_1_emb_1d_0.31'
    # model = './seed_1_emb_1e-2'
    # model = './seed_1_emb_1d_0.315'
    # model = './seed_1_emb_1e-2.3_0.33'
    # model = '../modeling/simulations/mu-04_tau-05mpa_sw/seed-5_hypo-1/out'
    # model = '../modeling/simulations/mu-04_tau-5mpa_sw_homo_mat/seed-5_hypo-1/out'
    # model = './seed_1_emb_0.3_h1'
    # model = '/Users/williamsavran/Desktop'
    # model = '../two_step/dx50_test_model/out'
    # model = '/Users/williamsavran/Dropbox/Projects/2016/krg/modeling/simulations/r1/seed3'
    model = './'

    # compute total slip
    slip1 = np.fromfile(model + '/su1', dtype=np.float32).reshape([nz,nx])
    slip2 = np.fromfile(model + '/su2', dtype=np.float32).reshape([nz,nx])
    trup = np.fromfile(model + '/trup', dtype=np.float32).reshape([nz,nx])
    psv = np.fromfile(model + '/psv', dtype=np.float32).reshape([nz,nx])
    slip = np.sqrt(slip1**2+slip2**2)
    # name = model.split('/')[-1] # grab name as last token

    # plot slip
    x = np.arange(0,ex,dx*1e-3)
    fig = plt.figure()
    ax = fig.gca()
    palette = plt.cm.jet
    print 'mean slip: ', np.mean(slip[np.where(psv > 0.01)])
    print 'max slip: ', slip.max()
    print 'min slip: ', slip.min()
    # plot contours of rupture time 
    # xx = 0.001 * np.fromfile(model + '/x1o', dtype=np.float32).reshape([nz,nx])
    # zz = 0.001 * np.fromfile(model + '/x2o', dtype=np.float32).reshape([nz,nx])
    x = np.arange(0,ex,dx*1e-3)
    z = np.arange(0,ez,dx*1e-3)
    xx, zz = np.meshgrid(x,z)
    v = 0.75 * np.arange(-20,20)
    im = ax.imshow(slip, extent=(0, ex, 0, ez), origin='normal',cmap=palette)
    ctrup = ax.contour(xx,zz,trup,v,extent=(0, ex, 0, ez), colors='gray', linewidths=0.25, antialiased=False)
    ctrup.levels = [nf(val) for val in ctrup.levels]
    fmt = '%r'
    # plt.clabel(ctrup, ctrup.levels, inline=True, fmt=fmt, fontsize=10)
    # ax.scatter(1201*dx*1e-3,401*dx*1e-3, marker='*', s=250, color='k')
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = np.colorbar(im, cax=cax)
    cbar.solids.set_rasterized(True)
    cbar.solids.set_edgecolor("face")
    cbar.set_label(label='Slip (m)', size=14)
    ax.set_ylim([20,0])
    ax.set_xlim([0,65])
    ax.set_xlabel('Distance (km)', fontsize=14)
    ax.set_ylabel('Distance (km)', fontsize=14)
    im.set_clim([0,slip.max()])

    # divider = make_axes_locatable(ax)
    tax = divider.append_axes("top", size="25%", pad=0.05)
    tax.plot(x, slip1[0,:], 'k')
    tax.set_yticks([0, slip[0,:].max()])
    tax.tick_params(
            axis = 'x',
            which = 'both',
            bottom = 'off',
            right = 'off',
            labelbottom = 'off',
            )
    ticks = tax.yaxis.get_majorticklabels()
    ticks[0].set_verticalalignment('bottom')
    ticks = ax.yaxis.get_majorticklabels()
    ticks[0].set_verticalalignment('top')
    ax.tick_params(axis='x', top = 'off', labeltop = 'off')
    np.savefig('slip_ncont1.pdf')
    # plot psv
    fig = plt.figure()
    ax = fig.gca()
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    im = ax.imshow(psv, extent=(0, ex, 0, ez), origin='normal', cmap='plasma')

    # plt.scatter(1201*dx*1e-3,401*dx*1e-3, marker='*', s=150, color='k')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = np.colorbar(im, cax=cax)
    cbar.solids.set_rasterized(True)
    cbar.solids.set_edgecolor("face")
    cbar.set_label(label=r'$V^{peak}$ (m/s)', size=14)
    ax.set_xlim([0,65])
    ax.set_ylim([20,0])
    ax.set_xlabel('Distance (km)', fontsize=14)
    ax.set_ylabel('Distance (km)', fontsize=14)
    im.set_clim([0,psv.max()])
    # ax.set_xlabel('Distance (km)', fontsize=14)
    # ax.set_ylabel('Distance (km)', fontsize=14)
    print 'mean psv: ', np.mean(psv[np.where(psv > 0.01)])
    print 'max psv: ', psv.max()
    np.savefig('psv1.pdf')

    # plot vrup 
    material = np.loadtxt('bbp1d_1250_dx_25.asc')
    vs = material[:,2]
    cs = ml.repmat(vs[:-1],nx,1).T * 1e3
    trup_ma = np.ma.masked_values(trup,1e9)
    gy, gx = np.absolute(np.gradient(trup_ma))
    ttime = np.sqrt(gy**2 + gx**2)
    vrup = dx / ttime
    fig = plt.figure()
    ax = fig.gca()
    im = ax.imshow(vrup/cs, extent=(0, ex, 0, ez), origin='normal', cmap='viridis')
    print len(np.where(vrup/cs >= 1.0)[0])
    
    print 'median vrup: ', np.median(vrup.ravel()) 
    # plt.scatter(1201*dx*1e-3,401*dx*1e-3, marker='*', s=150, color='k')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = np.colorbar(im, cax=cax)
    cbar.solids.set_rasterized(True)
    cbar.set_label(label=r'$V_{rup}/c_s$', size=14)
    cbar.solids.set_edgecolor("face")
    ax.set_xlim([0,65])
    ax.set_ylim([20,0])
    im.set_clim([0.5,1.0])
    ax.set_xlabel('Distance (km)', fontsize=14)
    ax.set_ylabel('Distance (km)', fontsize=14)
    np.savefig('vrup1.pdf')

