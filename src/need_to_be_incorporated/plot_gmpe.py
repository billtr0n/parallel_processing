from pylab import *
rcParams['xtick.direction'] = 'out'
rcParams['ytick.direction'] = 'out'
rcParams['mathtext.default'] = 'regular'

data = loadtxt('seed17_gmrotD50_00.25Hz_plot.dat',delimiter=',')
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


