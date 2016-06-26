from pylab import *
from matplotlib.backends.backend_pdf import PdfPages

a2 = fromfile('a2','f').reshape([1001,801,1301])/9.81
pdfpages = PdfPages('sord_a2_snaps.pdf')
for i in arange(50,1001,5):
    time = i * 0.02
    fig = figure(dpi=100)
    title('Time: %2.2f' % time)
    imshow(a2[i,:,:],origin='normal',cmap='seismic')
    clim([-0.05,0.05])
    pdfpages.savefig(fig)
pdfpages.close()
