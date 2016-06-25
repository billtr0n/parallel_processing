import os
import subprocess

"""
Define tasks here.

Notes: initially tasks are defined to operate sequentially, eventually i will want to 
let independent tasks start in their own threads.
"""

# TODO: Make a default tasks class that can attach parameters and what not.
def plot_gmpe( params = None ):
    print 'Computing NGA West2 GMPE relationships'
    print '======================================'
    # hard code frequencies, eventhough i shouldn't
    # make more arbitrary to look at more periods when fortran code is implemented
    freq = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]

    for f in freq:
        name = os.path.join(params['cwd'], 'gmrotD50_%05.2fHz_plot.dat' % f)

        # prepare figure
        # have some type of structure that contains all the worker functions
        # probably one level of abstract above this. ie "plot_gmpe" would be alongside plot_sa and plot_pga, the latter 
        # we need to define 1d, 2d, and 3d data types. 3d data types will be at the latter.
        try:
            _plot_individual( name )
            _plot_group_bias( name )
        except IOError:
            print "skipping %05.2fHz. file %s not found" % (f, name)
            continue

def calc_gmpe( params = None ):
    try:
        os.chdir( params['cwd'] )
        out = open('gmpe_comp.log', 'wb')
        p = subprocess.Popen(["matlab", "<", params['script_name']], stdout=out, stderr=subprocess.PIPE)
        p.wait()
        os.chdir( params['home_dir'] )
        out.close()
    except Exception as e:
        print '\n'.join([str(e), 'Unable to launch job.'])
        

"""
Private helping functions below.
"""
def _plot_group_bias():
    # TODO: Stub function
    pass

def _plot_individual( name ):
    from numpy import loadtxt
    from matplotlib import pyplot as plt

    fig = plt.figure()
    data = loadtxt(name, delimiter=',')
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
    ax.set_xlabel(r'$R_{rup} (km) $')
    ax.set_ylabel('SA (g)')
    basename = name[:-4] # strip off file extension
    fig.savefig('./' + fout + '.pdf' )
    fig.close()


