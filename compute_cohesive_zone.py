import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['xtick.direction']='out'
matplotlib.rcParams['ytick.direction']='out'

dt = 0.02
nt = 985
nz = 801
nx = 2601
slip_mag = np.fromfile('sum','f').reshape([nt, nz, nx])

slip_tol = 0.001
dc = 0.15

zz, xx = np.mgrid[:nz,:nx]

# contour intervals
V1 = [slip_tol]
V2 = [0.15]

time = [2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 17.0]
# time = np.arange(0.5,601*0.02,25*0.02)
distmt = []
fig = plt.figure()
ax1 = fig.add_subplot(111)
tot = 0
for T in time:
    t = int(T / dt)
    slip_mag_t = np.squeeze(slip_mag[t,:,:])
    cs1 = ax1.contour(slip_mag_t, V1, color='blue')
    cs2 = ax1.contour(slip_mag_t, V2, color='green')
    plt.xlabel('Nodes in X')
    plt.ylabel('Nodes in Y')
    plt.title('Time: ' + str(T))

# get (x,y) locations of contours
    x1a = []
    y1a = []
    for path in cs1.collections[0].get_paths():
        v = path.vertices
        x1a.extend(v[:,0])
        y1a.extend(v[:,1])

    x2a = []
    y2a = []
    for path in cs2.collections[0].get_paths():
        v = path.vertices
        x2a.extend(v[:,0])
        y2a.extend(v[:,1])

    p1s = np.column_stack([x1a,y1a])
    p2s = np.column_stack([x2a,y2a])

    distm = []
    for i in range(len(p2s)):
        p1t = p1s[i,:]
        p1ts = np.tile(p1t,(len(p2s),1))
        d = np.sqrt(np.sum((p1ts-p2s)**2,axis=1)).min()
        distm.append(d)
    distm = np.array(distm)
    distmt.append(distm.mean())


print np.array(distmt).min()
fig = plt.figure()
ax = fig.gca()
ax.plot(time, distmt)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Cohesive Zone (Nodes)')
ax.grid()
ax1.invert_yaxis()
plt.show()








