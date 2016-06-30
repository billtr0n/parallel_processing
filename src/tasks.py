import os
import subprocess

"""
Define tasks here. 
"""
def process_gmpe( params = None ):
    if self.__prepare_parameters( self.params['cwd'] ):
        if calc_gmpe( params = params ):
            try:
                plot_gmpe( params=params )
            except Exception as e:
                print 'could not plot gmpe because %s' % e
                raise

def plot_gmpe( params = None ):
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


def calc_gmpe( params = None ):
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

        

"""
Private helping functions below.
"""
def plot_gmpe_group_bias( params ):
    from numpy import log, loadtxt, array, where
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

    freqs = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
    distances = [10, 15, 20, 25, 30]

    
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
                        ind = where(data[:,0] == dist + 0.5)
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
                avgb = b.mean(axis=0)
                minb = b.min(axis=0)
                maxb = b.max(axis=0)
                ylower = avgb - minb
                yupper = maxb - avgb
                ax.errorbar(data[:,0], avgb, yerr=[ylower,yupper], fmt='o', ecolor='g', capthick=2)
                fig.savefig( os.path.join(params['root_dir'], 'dist_bias_%shz.pdf' % key ) )

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
                avgb = b.mean(axis=0)
                minb = b.min(axis=0)
                maxb = b.max(axis=0)
                ylower = avgb - minb
                yupper = maxb - avgb
                ax.errorbar(1./array(freqs), avgb, yerr=[ylower,yupper], fmt='o', ecolor='g', capthick=2)
                fig.savefig(os.path.join(params['root_dir'], 'dist_freq_%skm.pdf' % key) )
    except Exception as e:
        print 'exception: %s' % str(e)

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

def test_task( params ):
    print 'testing.'
    return
