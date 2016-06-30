import numpy as np
from multiprocessing import Process, Pool, JoinableQueue
import logging

class MultiprocessingTest( object ):

	def __init__( self, num_workers = 2 ):
		
		task_queue = JoinableQueue

		def __init__():
			self.num_workers = 8
				self.process = [Process(target=job) for i in range(n)]
		





def job(f):
	""" 100000 ffts on len 32768 length vectors """
	nsim = 100000
	n = 32768
	x = np.linspace(0,2*np.pi,n)
	f = np.sin(x)
	for i in range( nSim ):
		result = np.fft.fft(f)

		






if __name__ == "__main__":
	main()