def process_dynamic_rupture_simulation( params ):
    """Container task used to process an entire dynamic rupture simulation.  Used when processing multiple
       simulations, so task queue does not get absolutely massive.

    General steps:
        1) Plot kinematic fields
        2) Create one-point statistics
            - histogram using ~100,000 points where rupture velocity is subshear and outside nucleation zone
        and outside velocity weakening zone, the latter will be applied later during the kinematic modeling phase.
        3) Create CSV files for analysis in R based on previous 100,000 points 
            - psv, vrup, slip, mu0
        4) Generate markdown file showing kinematic fields, and summary of one-point statistics
    

    Args:
        params (dict) : contains all parameters necessary for tasks
    Returns:
        Success. Task is expected to fail elegantly and report any issues to the log, but if for some reason
        it does not this function will return false.
    """

    import numpy as np
    import pandas as pd

    import logging
    import os

    import utils

    
    logging.info('beginning work on %s' % outdir)
    # check for required parameters
    # maybe make this subclass SimpleTask and do that in "ready" method
    try:
        nx = params['nx']
        nz = params['nz']
        dx = params['dx']
        cwd = params['cwd'] 
        ihypo = params['ihypo']
        outdir = os.path.join(cwd, 'out')
        figdir = os.path.join(cwd, 'figs')
        if not os.path.exists( figdir ):
            os.makedir( figdir )
    except KeyError:
        logging.error('missing required params. aborting.')
        return False

    # set file names
    files = {
        'su1'  : os.path.join( outdir, 'su1' ),
        'su2'  : os.path.join( outdir, 'su2' ),
        'trup' : os.path.join( outdir, 'trup' ),
        'psv'  : os.path.join( outdir, 'psv' ),
        'tsm'  : os.path.join( outdir, 'tsm' ),
        'tnm'  : os.path.join( outdir, 'tnm' ),
    }
    logging.info( 'working with files: %s' % ', '.join( files.keys() ) )

    # load files into dict
    ex = dx * nx
    ez = dx * nz
    x = np.arange( 0,ex,dx )
    z = np.arange( 0,ez,dx )
    xx, zz = np.meshgrid( x, z )
    material = np.loadtxt( os.path.join(params['cwd'], 'bbp1d_1250_dx_25.asc') )
    vs = material[:,3]
    data = {
        'x'    : xx
        'z'    : zz
        'su1'  : np.fromfile( files['su1'], dtype='np.float32' ).reshape([ nz, nx ])
        'su2'  : np.fromfile( files['su2'], dtype='np.float32' ).reshape([ nz, nx ])
        'trup' : np.fromfile( files['trup'], dtype='np.float32' ).reshape([ nz, nx ])
        'psv'  : np.fromfile( files['psv'], dtype='np.float32' ).reshape([ nz, nx ])
        'tsm'  : np.fromfile( files['tsm'], dtype='np.float32', count=nx*ny ).reshape([ nz, nx ]) / 1e6 # read initial shear stresses
        'tnm'  : np.fromfile( files['tnm'], dtype='np.float32', count=nx*ny ).reshape([ nz, nx ]) / 1e6 # read initial normal stresses
    }
    data['vrup'] = utils.compute_rupture_velocity( trup, dx, cs=vs )
    data['sum']  = np.sqrt( su1**2 + su2**2 )
    data['mu0']  = tsm / np.absolute(tnm)

    clabel = {
        'su1' : r'$u_x$ (m)',
        'su2' : r'$u_z$ (m)',
        'trup': r'$t_{rup}$ (s)',
        'psv' : r'$V_{peak} (m/s)$',
        'tsm' : r'$|\tau_s| (MPa)$',
        'tnm' : r'$|\tau_n| (MPa)$',
        'vrup': r'$v_{rup}$ (m/s)',
        'sum' : r'$|u| (m)$',
        'mu0' : r'$\mu_0$',
    }

    """ plot kinematic fields """
    for field in data:
        if field not in ['x','z']:
            if field in ['sum', 'su1','su2']:
                inp = { 
                        'data'    : data[field], 
                        'contour' : data['trup'],
                      }
                utils.plot_2d_image( inp, filename=os.path.join(figdir, field + '.pdf'),
                    nx=nx, nz=nz, dx=dx, clabel=clabel[field], xlabel='Distance (km)', ylabel='Depth (km)', 
                    surface_plot=True, contour=True )
            else:
                utils.plot_2d_image( inp, filename=os.path.join(figdir, field + '.pdf'),
                    nx=nx, nz=nz, dx=dx, clabel=clabel[field], xlabel='Distance (km)', ylabel='Depth (km)', 
                    surface_plot=False, contour=False )


    """ calculate one-point statistics 
    mask unwanted values 
        1) inside hypocenter 
        2) inside velocity-strengthening 
        3) where super-shear 
        4) within rupturing area on the fault

    compute slip.mean(), slip.std(), psv.mean(), psv.std(), vrup.mean(), vrup.std(), commit to data structure
    """
    simulation_data = {} """ <<----- Add more into this, this will be the data structure holding everything about the model. 
                                     for instance, parameters from json file need to be stored in here as well. """
    include = ['sum', 'vrup', 'psv', 'mu0', 'x', 'z']
    for key in data:
        if key not in include:
            data[key] = data[key].raveled()

    # write old data
    data = pd.DataFrame( data = data )
    
    rcrit = 4000
    data_trimmed = pd.concat([
                # remove square region around hypocenter ~ size of rcrit
                data[ (data['x'] < ihypo[0]-rcrit) | (data['x'] > ihypo[0]+rcrit) ], 
                data[ ((data['x'] > ihypo[0]-rcrit) & (data['x'] < ihypo[0]+rcrit) ) & 
                        ((data['z'] < ihypo[1]-rcrit) | (data['z'] > ihypo[1]+rcrit)) ], 
                # remove velocity strengthening, this will be analyzed and implemented later
                data[ data['z'] > 4000 ],
                # remove super-shear
                data[ data['vrup'] < 1.0],
                # remove areas that did not rupture
                data[ (data['slip'] > 0.1) & (data['slip'] < 1e9)],
    ]).reset_index().drop_duplicates(subset='index').set_index('index')

    # take 20% sample of the data
    data_sample = data_trimmed.sample( frac=0.2 )

    # store one-point statistics
    simulation_data['one_point'] = {
                                    # same sampled version
                                    'avg_slip_tr': data_trimmed['sum'].mean(),
                                    'avg_psv_tr':  data_trimmed['psv'].mean(),
                                    'avg_vrup_tr': data_trimmed['vrup'].mean(),
                                    'std_slip_tr': data_trimmed['sum'].std(),
                                    'std_psv_tr': data_trimmed['psv'].std(),
                                    'std_vrup_tr': data_trimmed['vrup'].std(),

                                    # save sampled version
                                    'avg_slip_sa': data_sample['sum'].mean(),
                                    'avg_psv_sa':  data_sample['psv'].mean(),
                                    'avg_vrup_sa': data_sample['vrup'].mean(),
                                    'std_slip_sa': data_sample'sum'].std(),
                                    'std_psv_sa': data_sample['psv'].std(),
                                    'std_vrup_sa': data_sample['vrup'].std(),
                                    }


    # compute histograms 
    fig, ax = 
    data_sample.hist( bins = np.sqrt(len(data_sample.index)), normed = 1, ax = ax )

    """ write out csv files """
    # write out randomly sampled data points for spatial analysis in R



    """ generate markdown file """
    




