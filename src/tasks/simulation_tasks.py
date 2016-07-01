import os
import subprocess

"""
Define tasks here. 
"""
def process_gmpe( params ):
    if self.__prepare_parameters( self.params['cwd'] ):
        if calc_gmpe( params = params ):
            try:
                plot_gmpe( params=params )
            except Exception as e:
                print 'could not plot gmpe because %s' % e
                raise

def plot_gmpe( params ):
    # hard code frequencies, eventhough i shouldn't
    # make more arbitrary to look at more periods when fortran code is implemented

    print 'Plotting GMPE relationships.'
    freq = [ 0.25, 0.5, 1.0, 2.0, 3.0, 5.0 ]
    # freq = [ 0.25 ]

    for f in freq:
        name = os.path.join( params['cwd'], 'gmrotD50_%05.2fHz_plot.dat' % f )

        # prepare figure
        # have some type of structure that contains all the worker functions
        # probably one level of abstract above this. ie "plot_gmpe" would be alongside plot_sa and plot_pga, the latter 
        # we need to define 1d, 2d, and 3d data types. 3d data types will be at the latter.
        try:
            __plot_gmpe_individual( name )
        except IOError:
            print "skipping %05.2fHz. file %s not found" % (f, name)
            raise


def calc_gmpe( params ):
    try:
        print 'Computing NGA West2 GMPE relationships.'
        os.chdir( params['cwd'] )
        out = open('gmpe_comp.log', 'wb')
        # figure out how to return that is successfully started, callback?
        p = subprocess.Popen( ["matlab", "<", params['script_name']], stdout=out, stderr=subprocess.PIPE)
        # p.wait()
        os.chdir( params['home_dir'] )
        out.close()
    except Exception as e:
        # print 'Unable to launch job due to error: %s' % e
        return False
    return

def plot_gmpe_group_bias( params ):
    from numpy import log, loadtxt, array, where, median, percentile
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

    freqs = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
    distances = [9.5, 14.5, 19.5, 24.5, 29.5]

    
    try:
        # create data structure to hold bias results
        bias = {}
        for dist in distances: 
            bias[dist] = []
        for freq in freqs:
            bias[freq] = []

        # loop through all the directories
        for d in os.listdir( params['root_dir'] ):
            cwd = os.path.join( params['root_dir'], d )
            if os.path.isdir( cwd ):
                for freq in freqs:
                    filename = os.path.join(cwd, 'gmrotD50_%05.2fHz_plot.dat' % freq)
                    data = loadtxt(filename, delimiter=',' )
                    gmpe_mid = (data[:,2] + data[:,3]) / 2
                    log_bias = log(data[:,1] / gmpe_mid)
                    bias[freq].append(log_bias)
                    for dist in distances:
                        ind = where(data[:,0] == dist)
                        gmpe_mid = (data[ind,2] + data[ind,3]) / 2
                        log_bias = log(data[ind,1] / gmpe_mid)
                        bias[dist].append(log_bias)

        # make figure
        for key in bias.keys():
            if key in freqs:
                # print key
                fig = Figure()
                canvas = FigureCanvas(fig)
                ax = fig.add_subplot(111)
                ax.set_title( 'log(sim/gmpe) vs. distance @ %s Hz' % key )
                ax.set_xlabel('Distance (km)')
                ax.set_ylabel('log(sim/gmpe)')

                # plot horizontal line at 0
                ax.axhline(y=0, color='black')

                # plot bias and error bars
                b = array(bias[key])
                avgb = median(b, axis=0)
                minb = b.min(axis=0)
                maxb = b.max(axis=0)
                q25s, q75s = percentile(b, [25,75], axis=0)
                ylower = avgb - minb
                yupper = maxb - avgb
                ax.errorbar(data[:,0], avgb, yerr=[ylower,yupper], fmt='o', ecolor='g', capthick=2)
                for dis, avg, q25, q75 in zip(data[:,0], avgb, q25s, q75s):
                    wid = 0.7
                    hei = q75 - q25
                    xloc = dis - wid / 2
                    yloc = q25
                    ax.add_patch( Rectangle( (xloc, yloc), wid, hei, fill=False, color='blue') ) 
                fig.savefig( os.path.join(params['root_dir'], 'dist_bias_%shz.pdf' % key ), bbox_inches='tight' )

            if key in distances:
                fig = Figure()
                canvas = FigureCanvas(fig)
                ax = fig.add_subplot(111)
                ax.set_title('log(sim/gmpe) vs. period @ %s km' % key )
                ax.set_xlabel('Period (s)')
                ax.set_ylabel('log(sim/gmpe)')

                # plot horizontal line at 0
                ax.axhline(y=0, color='black')
                b = array(bias[key])
                b = b.reshape([b.size/len(freqs),len(freqs)])
                
                # plot bias and error bars
                avgb = median(b, axis=0)
                minb = b.min(axis=0)
                maxb = b.max(axis=0)
                q25s, q75s = percentile(b, [25,75], axis=0)
                ylower = avgb - minb
                yupper = maxb - avgb
                ax.errorbar(1./array(freqs), avgb, yerr=[ylower,yupper], fmt='o', ecolor='g', capthick=2)
                for dis, avg, q25, q75 in zip(1./array(freqs), avgb, q25s, q75s):
                    wid = 0.08
                    hei = q75 - q25
                    xloc = dis - wid / 2
                    yloc = q25
                    ax.add_patch( Rectangle( (xloc, yloc), wid, hei, fill=False, color='blue') )
                fig.savefig(os.path.join(params['root_dir'], 'dist_freq_%skm.pdf' % key) )
                ax.set_xlim([0, 5.0])
    except Exception as e:
        print 'exception: %s' % str(e)


def plot_kinematic_fields( params ):
    try:
        import os
        import pylab as np 
        import numpy.matlib as ml
        import scipy.stats.mstats as mstats
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
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

        model = os.path.join(params['cwd'], './out/')

        # compute total slip
        slip1 = np.fromfile(model + 'su1', dtype=np.float32).reshape([nz,nx])
        slip2 = np.fromfile(model + 'su2', dtype=np.float32).reshape([nz,nx])
        trup = np.fromfile(model + 'trup', dtype=np.float32).reshape([nz,nx])
        psv = np.fromfile(model + 'psv', dtype=np.float32).reshape([nz,nx])
        slip = np.sqrt(slip1**2+slip2**2)
        # name = model.split('/')[-1] # grab name as last token

        # plot slip
        x = np.arange(0,ex,dx*1e-3)
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.gca()
        palette = plt.cm.jet
        # print 'mean slip: ', np.mean(slip[np.where(psv > 0.01)])
        # print 'max slip: ', slip.max()
        # print 'min slip: ', slip.min()
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
        fig.savefig(os.path.join(params['cwd'], 'slip_rcont.pdf'))

        # plot psv
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        im = ax.imshow(psv, extent=(0, ex, 0, ez), origin='normal', cmap='jet')

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
        fig.savefig(os.path.join(params['cwd'], 'psv.pdf'))

        # plot vrup 
        # TODO: remove hard-coded velocity model
        material = np.loadtxt( os.path.join(params['cwd'], 'bbp1d_1250_dx_25.asc') )
        vs = material[:,2]
        cs = ml.repmat(vs[:-1],nx,1).T * 1e3
        trup_ma = np.ma.masked_values(trup,1e9)
        gy, gx = np.absolute(np.gradient(trup_ma))
        ttime = np.sqrt(gy**2 + gx**2)
        vrup = dx / ttime
        fig = plt.figure()
        ax = fig.gca()
        im = ax.imshow(vrup/cs, extent=(0, ex, 0, ez), origin='normal', cmap='viridis')
        
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
        fig.savefig(os.path.join(params['cwd'], 'vrup.pdf'))
    except Exception as e:
        print 'unable to plot source fields due to error %s' % str(e)



def compute_one_point_statistics( params ):
    # these one point statistics are going to be for each simulation.
    # take 20000 point sample where not in nucleation zone, or ruptures are supershear
    pass

def prepare_model_csv_files( params ):
    from pandas import DataFrame
    # prepare csv files used for spatial analysis in R
    pass
    

"""
Private helping functions below.
"""

# potential refactoring into utils.py
# even break that up into different submodules
# that way whenever i want to do anything, i can import taskmanager and geotools
def __plot_gmpe_individual( name ):
    try:
        from numpy import loadtxt, exp
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

        fig = Figure()
        canvas = FigureCanvas(fig)
        data = loadtxt(name, delimiter=',')

        # read data
        bin_edges = data[:,0]
        med_sim = data[:,1]
        min_med_gmpe = data[:,2]
        max_med_gmpe = data[:,3]
        med_sig_gmpe = data[:,4]

        ax = fig.add_subplot(111)
        ax.fill_between(bin_edges, min_med_gmpe, max_med_gmpe, color='gray', alpha=0.4)
        ax.loglog(bin_edges, med_sim, 'b')
        ax.loglog(bin_edges, max_med_gmpe*exp(med_sig_gmpe), '--k')
        ax.loglog(bin_edges, min_med_gmpe*exp(-med_sig_gmpe), '--k')
        ax.set_xlim([1.0,30.0])
        ax.set_xlabel( r'$R_{rup} (km) $' )
        ax.set_ylabel( 'SA (g)' )
        basename = name[:-4] # strip off file extension
        fig.savefig( basename + '.pdf' )
    except Exception as e:
        print 'Unable to launch job due to error: %s' % e
        return False

    return True


    def __prepare_parameters( self, cwd ):
        from numpy import fromfile
        par = {}

        # read default parameters
        try:
            with open(os.path.join(self.params['root_dir'], 'params.txt'), 'r') as file:
                temp = file.readlines()
            for line in temp:
                line = line.split()
                if line:
                     key = line[0] 
                     val = line[1]
                     par[key] = val
        except IOError:
            print '\tERROR: unable to read params.txt file.' 
            return False

        # try reading the magnitude
        try:
            mw = self.__read_magnitude( cwd )
            par.update(mw)
        except IOError:
            print '\tERROR: unable to find magnitude file.'
            return False

        # try getting the extent of the fault
        try:
            extent = self.__get_fault_extent( cwd, par )
            par.update(extent)
        except IOError:
            print 'unable to determine fault extent. skipping model...'
            return False

        # copy necessary files
        try:
            # temporary until i get fortran codes implemented
            shutil.copy( os.path.join(self.params['script_dir'], 'gmpe_calc.m'), cwd )
            shutil.copy( os.path.join(self.params['script_dir'], 'ASK_2014_nga.m'), cwd )
            shutil.copy( os.path.join(self.params['script_dir'], 'BSSA_2014_nga.m'), cwd )
            shutil.copy( os.path.join(self.params['script_dir'], 'CB_2014_nga.m'), cwd )
            shutil.copy( os.path.join(self.params['script_dir'], 'CY_2014_nga.m'), cwd )
            shutil.copy( os.path.join(self.params['script_dir'], 'bbp1d_1250_dx_25.asc'), cwd )
        except IOError:
            print 'unable to copy necessary files.'
            return False

        # now write the parameters file
        # when i get fortran routines, no reason to write file anymore
        try:
            with open(os.path.join(cwd, 'params.txt'), 'w') as file:
                for k,v in par.iteritems():
                    file.write(k + ' ' + str(v) + '\n')
        except IOError:
            print 'unable to write to params.txt file'
            return False

        # made it through the gauntlet
        return True

    def __read_magnitude( self, cwd ):
        import os
        from numpy import fromfile, where

        # try finding that file anywhere in the model directory
        for root, dirs, files in os.walk( cwd ):
            for name in files:
                if name == 'mw':
                    mw = fromfile(os.path.join(root, name),'f')[-1]
                    return { 'mw' : mw }
        raise IOError

    def __get_fault_extent( self, cwd, par ):
        import os
        from numpy import fromfile, where, floor

        nx = int(par['fltnx'])
        nz = int(par['fltnz'])

        psv = fromfile( os.path.join(cwd, 'out/psv'), 'f' ).reshape([nz,nx])
        y,x = where( psv > 1.0 ) # returns inds where condition is true
        strtx = x.min()
        endx = x.max()
        nflt = floor( (endx - strtx) / 2 )
        if nflt < 0:
            print 'negative fault length, something is wrong.'
            raise ValueError
        return { 'strtx' : strtx, 'nflt' : nflt }

