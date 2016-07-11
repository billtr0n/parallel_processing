from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from pandas import DataFrame
from numpy import arange, exp


def subplots(fig, shape = (1,1), **kwargs):
	""" wrapper to create subplots using matplotlib api instead of pyplot 

	Inputs:
		fig (matplotlib.figure.Figure) : subplots will be added to this figure. 
		shape (tuple (int)) : shape of the subplot layout, (num_rows, num_cols) 

	Returns:
		ax: list of lists of matplotlib.axes.Axes objects .
	"""

	if not isinstance(fig, Figure):
		raise TypeError("fig must be of type matplotlib.figure.Figure")


	try:
		ny = int(shape[0])
		nx = int(shape[1])
	except TypeError:
		raise TypeError("subplot shape must be an integer.")
	
	ax = []
	ind = 0
	for _ in range( ny ):
		row = []
		for _ in range( nx ):
			ind += 1
			row.append( fig.add_subplot(ny,nx,ind) )
		ax.append( row )
	return ax


fig = Figure()
canvas = FigureCanvas(fig)
ax = subplots(fig, shape=(2,2))
x = arange(0,10,0.001)
y = exp(x/4*x)
df = DataFrame({'x':x,'y':y})
t = df.hist(column=['y'])