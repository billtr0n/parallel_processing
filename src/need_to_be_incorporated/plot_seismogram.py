"""
Author: William Savran
plots 3 component seismogram, fourier amplitude spectrum, and kinetic energy
each seismogram is contained in TimeSeries class.
requires: numpy

supports list, or tuple objects, or any container that returns 
a value when iterated over using "in"
"""

from Models import SeismogramFigure

# higher level wrapper
def make_seismogram_figure(seismograms, kind='default'):
    fig = None
    try:
        for seismogram in seismograms:
            fig = plot_seismogram(fig, seismogram, kind=kind)
    except TypeError:
        print 'object not iterable, trying as scalar.'
        fig = plot_seismogram(fig, seismograms, kind=kind)
    return fig
    
"""
notes: this will use the metadata from Seismogram class "name" to
print the legend for the plot

idea: program predefined seismogram figures, so we can make several complex figures automatically, plotting will have to be handled by
      a plot_all function for now it's hard coded.
"""
def plot_seismogram(fig, seismogram, kind='default'):
    
    # im assuming these are installed
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    
    # stylistic choices
    matplotlib.rcParams['xtick.direction']='out'
    matplotlib.rcParams['ytick.direction']='out'
    
    # if there is no figure 
    if fig is None:
        fig = SeismogramFigure(kind=kind)
        fig.initialize_subplots()
    
    # handle a way to pass plotting arguments to the figure
    fig.plot_all( seismogram )
    
    # TODO: add labels, add axes limits, 
    return fig
    
    
        
if __name__ == "__main__":
    import numpy as np
    from Models import TimeSeries
    print 'some usage examples'
    data = {
           'time': np.arange(0,1000*0.01,0.01),
           'x'   : np.random.rand(1000),
           'y'   : np.random.rand(1000),
           'z'   : np.random.rand(1000)
           }
    t = TimeSeries(data)
    fig = make_seismogram_figure( t )
    fig.show()
