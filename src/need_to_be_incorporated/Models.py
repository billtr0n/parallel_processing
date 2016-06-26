"""
Time-Series Class
Class to store n-dimensional time series and store meta-data about them.
accepts a dict that has key = component and value = timeseries, needs to have
a key called "time".  the time-series should be ndarray.  this should only store
related time-series.

"""
class TimeSeries( object ):
    def __init__(self, *args, **kwargs):
        if args:
            data = args[0]
            # fidelity checks, might be missing some? clean this up?
            if type(data) != dict:
                raise TypeError("""data must be of dict type. The dict must contain
                                 at least one time-series (type=numpy.ndarray) and its
                                 associated time vector (type=numpy.ndarray) called 'time'.""")
            if 'time' not in data.keys():
                raise ValueError("Time not defined in the input.")
            if len(data.keys()) < 2:
                raise ValueError("Requires at least two time-series.")
        else:
            raise TypeError('No arguments. One dict required, [optional] input meta-data with kwargs.')
        
        
        # maybe we can remove this in the future, but for now it must stay.
        try:
            from numpy import ndarray
        except ImportError:
            raise ImportError("Numpy is required. Please install.")
        
        # extracting data from input
        for key, val in data.iteritems():
            # last fidelity check
            if not isinstance(val, ndarray):
                raise TypeError("""data must be of dict type. The dict must contain          
                                 at least one time-series (type=numpy.ndarray) and its       
                                 associated time vector (type=numpy.ndarray) called 'time'.""")
            # make sure the values are sensible first, but now we just perform a catch-all
            try:
                setattr(self, key, val)
            except Exception as e:
                print "Unable to set attribute %s because %s" % (key, str(e)) 
                
            
        # handle arbirary metadata, defaults here are used for plotting. more to come?
        self.metadata = {
                        'name'      :  'Unnamed Seismogram',
                        'property'  :  'Time-Series',
                        'units'     :  '[None]'
                        }
        self.metadata.update(kwargs)
        
    """
    Notes: comp should correspond to the name of each component in the 
    TimeSeries class, default is all components
    """
    def fourier_amplitude_spectrum( self, comp=None ):
        pass
        
    def kinetic_energy( self, comp=None ):
        pass
        
"""
SeismogramFigure Class
Wrapper to matplotlib class, which provides functionality for plotting seismograms.

"""
from matplotlib.pyplot import Figure
class SeismogramFigure( Figure ):
    
    def __init__(self, kind='default',  *args,**kwargs):
        super(SeismogramFigure, self).__init__(*args, **kwargs)
        self.subplots = {}
        
    def initialize_subplots( self ):
        from matplotlib.pyplot import subplot2grid
        # X componet
        self.subplots['xts']  = subplot2grid((3,4),(0,0), colspan=2)
        self.subplots['xke']  = subplot2grid((3,4),(0,2))
        self.subplots['xfas'] = subplot2grid((3,4),(0,3))
        
        # Y component
        self.subplots['yts']  = subplot2grid((3,4),(1,0), colspan=2)
        self.subplots['yke']  = subplot2grid((3,4),(1,2))
        self.subplots['yfas'] = subplot2grid((3,4),(1,3))
        
        # Z component
        self.subplots['zts']  = subplot2grid((3,4),(1,0), colspan=2)
        self.subplots['zke']  = subplot2grid((3,4),(1,2))
        self.subplots['zfas'] = subplot2grid((3,4),(1,3))
        return 
        
    def plot_all( self, s ):
        # obviously need some error checking here
        # plot seismograms
        self.subplots['xts'].plot(s.time, s.x)
        self.subplots['yts'].plot(s.time, s.y)
        self.subplots['zts'].plot(s.time, s.z)
        
        # plot kinetic energy
        self.subplots['xke'].plot(s.time, s.kinetic_energy(comp='x'))
        self.subplots['yke'].plot(s.time, s.kinetic_energy(comp='y'))
        self.subplots['zke'].plot(s.time, s.kinetic_energy(comp='z'))
        
        # plot fourier amplitude spectrum
        self.subplots['xfas'].loglog(*s.fourier_amplitude_spectrum(comp='x')) # * because it will return tuple of freq, and fas
        self.subplots['yfas'].loglog(*s.fourier_amplitdue_spectrum(comp='y')) 
        self.subplots['zfas'].loglog(*s.fourier_amplitude_spectrum(comp='z')) 
        return
    
if __name__ == "__main__":
    print 'running basic examples of Time-Series...'
    import numpy as np
    import matplotlib.pyplot as plt
    # test 1d
    data = {
           'time': np.arange(0,1000*0.01,0.01),
           'x'   : np.random.rand(1000)
           }
    t = TimeSeries(data)
    plt.figure()
    plt.plot(t.time, t.x)
    plt.show()
    
    # test 3d
    data = {
           'time': np.arange(0,1000*0.01,0.01),
           'x'   : np.random.rand(1000),
           'y'   : np.random.rand(1000),
           'z'   : np.random.rand(1000)
           }
    t = TimeSeries(data)
    plt.figure()
    plt.plot(t.time, t.x)
    plt.plot(t.time, t.y)
    plt.plot(t.time, t.z)
    plt.show()
    
    # test nd
    nd = 4
    data = {}
    x = np.arange(0,10,0.01)
    data['time'] = x
    for i in range(nd + 1):
        key = 'x' + str(i)
        data[key] = 0.5*(i+1) * x
    
    plt.figure()
    t = TimeSeries(data)
    plt.figure()
    plt.plot(t.time, t.x1)
    plt.plot(t.time, t.x2)
    plt.plot(t.time, t.x3)
    plt.plot(t.time, t.x4)
    plt.show()
        
    # test metadata
    t = TimeSeries(data)
    print t.metadata
    t2 = TimeSeries(data, foo="bar")
    print t2.metadata
    
    
