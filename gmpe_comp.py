import os
import subprocess
import shutil
import Queue
from threading import Thread
from utils import plot_gmpe

def gmpe_comp():
    root_dir   = '/Users/williamsavran/Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa'
    script_dir = '/Users/williamsavran/Projects/2016/krg/two_step/scripts/'
    script_name = 'gmpe_comp_04_01_16.m'
    processes = []
    print 'Computing NGA West2 GMPE relationships'
    print '======================================'
    for d in os.listdir(root_dir):
        cwd = os.path.join(root_dir, d)
        if os.path.isdir( cwd ):
            try:
                print 'launching GMPE comparisons for %s' % d  
                os.chdir( cwd )
                # copy matlab script and params.txt file can do this better in the future
                shutil.copy( os.path.join(script_dir,script_name), os.path.join(cwd,script_name) )
                shutil.copy( os.path.join(script_dir,'params.txt'), os.path.join(cwd,'params.txt') )
                okay = prepare_parameters( cwd )
                if okay:        
                    t = threading.Thread(target=process_model)
                    processes.append( t )
                else:
                    print '\terror preparing parameters. skipping model...\n'
            except OSError:
                print '\tscript not found. skipping model...\n'
    if processes:
        for p in processes: p.start()
        print 'waiting for completion'
    else:
        print 'no models found. trying again in 2 hours'
    print 'All processes finished! Be back again in 2 hours.'

# 
def process_model( cwd ):
    # launch gmpe calculation
    # piping output to gmpe_comp.log
    with open('gmpe_comp.log', 'wb') as out:
        p = subprocess.Popen(["matlab", "<", "gmpe_comp_05_01_16.m"], stdout=out, stderr=subprocess.PIPE)
    p.wait()

    # call python plotting figure
    plot_gmpe( cwd )


# first stab is just to automate using minimum index where vrup is 0.
def prepare_parameters( cwd ):
    from numpy import fromfile
    okay = True
    success = True
    params = {}
    try:
        with open(os.path.join(cwd, 'params.txt'),'r') as file:
            temp = file.readlines()
        for line in temp:
            line = line.split()
            if line:
                 key = line[0] 
                 val = line[1]
                 params[key] = val
    except IOError:
        print '\tERROR: unable to read params.txt file.' 
        okay = False

    # try reading the magnitude
    try:
        mw = read_magnitude( cwd )
        params.update(mw)
    except IOError:
        print '\tERROR: unable to find magnitude file.'
        return False

    # try getting the parameters
    try:
        extent = get_fault_extent( cwd, params )
        params.update(extent)
    except IOError:
        print 'unable to determine fault extent. skipping model...'
        return False

    # now write the parameters file
    # when i get fortran routines, no reason to write file anymore
    with open(os.path.join(cwd, 'params.txt'),'w') as file:
        for k,v in params.iteritems():
            file.write(k + ' ' + str(v) + '\n')

    return success

def read_magnitude( cwd ):
    import os
    from numpy import fromfile, where

    # try finding that file anywhere in the model directory
    for root, dirs, files in os.walk( cwd ):
        for name in files:
            if name == 'mw':
                mw = fromfile(os.path.join(root, name),'f')[-1]
                return { 'mw' : mw }
    raise IOError

def get_fault_extent( cwd, params ):
    import os
    from numpy import fromfile, where, floor

    # using numpy here for the ease 
    try:
        # read in as string from file
        nx = int(params['fltnx'])
        nz = int(params['fltnz'])
    except KeyError:
        print 'params needs "fltnx" and "fltnz" defined'
        raise

    psv = fromfile( os.path.join(cwd, 'out/psv'), 'f' ).reshape([nz,nx])
    y,x = where( psv > 1.0 ) # returns inds where condition is true
    strtx = x.min()
    print strtx
    endx = x.max()
    print endx
    nflt = floor( (endx - strtx) / 2 )
    if nflt < 0:
        print 'negative fault length, something is wrong.'
    return { 'strtx' : strtx, 'nflt' : nflt }

def plot_gmpe( cwd ):
    # stylistic choices
    rcParams['xtick.direction'] = 'out'
    rcParams['ytick.direction'] = 'out'
    rcParams['mathtext.default'] = 'regular'

    # hard code frequencies, eventhough i shouldn't
    freq = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]

    for f in freq:
        name = 'gmrotD50_%05.2fHz_plot.dat' % f)
    data = loadtxt(name,delimiter=',')
    bin_edges = data[:,0]
    med_sim = data[:,1]
    min_med_gmpe = data[:,2]
    max_med_gmpe = data[:,3]
    med_sig_gmpe = data[:,4]

    fig = figure()
    ax = fig.add_subplot(111)
    ax.fill_between(bin_edges, min_med_gmpe, max_med_gmpe, color='gray', alpha=0.4)
    ax.loglog(bin_edges, med_sim, 'b')
    ax.loglog(bin_edges, max_med_gmpe*exp(med_sig_gmpe), '--k')
    ax.loglog(bin_edges, min_med_gmpe*exp(-med_sig_gmpe), '--k')
    ax.set_xlim([1.0,30.0])
    ax.set_xlabel(r'$R_{rup} (km) $')
    ax.set_ylabel('SA (g)')
    fout = 'seed17_gmrotD50_00.25Hz_test'
    savefig('/Users/williamsavran/Dropbox/Scratch/' + fout + '.pdf' )
    
# eventually write tests in here
if __name__ == "__main__":
    gmpe_comp()
