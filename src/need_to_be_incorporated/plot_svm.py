from pylab import *
from matplotlib.backends.backend_pdf import PdfPages

sv1 = fromfile('sv1','f').reshape([401,801,2601])
sv2 = fromfile('sv2','f').reshape([401,801,2601])
sv3 = fromfile('sv3','f').reshape([401,801,2601])


t = arange(0,401*0.002*25,0.002*25)
pdfpages = PdfPages('/Users/williamsavran/Dropbox/Scratch/flat_svm.pdf')
for i in range(100,2500,50):
    dist = i * 0.025
    figure()
    title('Distance Along Strike: ' + str(dist))
    plot(t, sv1[:,0,i],label='sv1')
    plot(t, sv2[:,0,i],label='sv2')
    # plot(t, sv3[:,0,i],label='sv3')
    legend(loc='best')
    pdfpages.savefig()
pdfpages.close()
