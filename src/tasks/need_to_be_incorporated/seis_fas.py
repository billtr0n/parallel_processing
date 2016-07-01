from pylab import *
from subroutines import *

dt = 0.0175
nt = 3000 
nseis = 18
vx_a = fromfile('seis_x0030000','f').reshape([nseis, nt])
vy_a = fromfile('seis_y0030000', 'f').reshape([nseis, nt])
vz_a = fromfile('seis_z0030000','f').reshape([nseis, nt])

t_awp = np.arange(0,nt*dt,dt)
start = 100
for i in range(18):
    dist = (800-start*(i+1))*0.05
    vx_filt = lowpass(vels2acc(vx_a[i,:], dt), dt, 10.0)
    vy_filt = lowpass(vels2acc(vy_a[i,:], dt), dt, 10.0)
    vz_filt = lowpass(vels2acc(vz_a[i,:], dt), dt, 10.0)

    fig = figure()
    ax1 = fig.add_subplot(321)
    fig.suptitle('Fault Normal Distance: ' + str(dist))
    ax1.plot(t_awp, vx_filt)

    f, fas = fourier_amplitude_spectrum(vx_filt, dt)
    ax2 = fig.add_subplot(322)
    ax2.loglog(f, fas)
    ax2.set_xlim([0,12.5])

    ax1 = fig.add_subplot(323)
    ax1.plot(t_awp, vy_filt)

    f, fas = fourier_amplitude_spectrum(vy_filt, dt)
    ax2 = fig.add_subplot(324)
    ax2.loglog(f, fas)
    ax2.set_xlim([0,12.5])

    ax1 = fig.add_subplot(325)
    ax1.plot(t_awp, vz_filt)

    f, fas = fourier_amplitude_spectrum(vz_filt, dt)
    ax2 = fig.add_subplot(326)
    ax2.loglog(f, fas)
    ax2.set_xlim([0,12.5])
    show()






