import shutil
import os
import threading

class ModelWorker( threading.Thread ):
    def __init__(self, tasks, params=None, *args, **kwargs):
        super(ModelWorker, self).__init__(*args, **kwargs)
        # assign arguments
        self.params = params
        self.tasks = tasks

        # instance variables
        self.success = False
        
    def init( self ):
        if self.__prepare_parameters( self.params['cwd'] ):
            self.success = True
        return self.success

    # overwriting threading.Thread.run
    def run( self, cwd ):
        # needs task class
        for task in tasks:
            task( params = params )

    def __prepare_parameters( self, cwd ):
        from numpy import fromfile
        par = {}
        # copy necessary files
        try:
            # temporary until i get fortran codes implemented
            shutil.copy( '../utils/gmpe_calc.m', cwd )
            shutil.copy( '../utils/ASK_2014_nga.m', cwd )
            shutil.copy( '../utils/BSSA_2014_nga.m', cwd)
            shutil.copy( '../utils/CB_2014_nga.m', cwd )
            shutil.copy( '../utils/CY_2014_nga.m', cwd )
        except IOError:
            print 'unable to copy necessary files.'
            return False

        # try getting the parameters
        try:
            with open(os.path.join(cwd, 'params.txt'),'r') as file:
                temp = file.readlines()
            for line in temp:
                line = line.split()
                if line:
                     key = line[0] 
                     val = line[1]
                     par[key] = val
        except IOError:
            print '\tERROR: unable to read params.txt file.' 
            return False

        # try reading the magnitude
        try:
            mw = self.__read_magnitude( cwd )
            par.update(mw)
        except IOError:
            print '\tERROR: unable to find magnitude file.'
            return False

        # try getting the extent of the fault
        try:
            extent = self.__get_fault_extent( cwd, par )
            par.update(extent)
        except IOError:
            print 'unable to determine fault extent. skipping model...'
            return False

        # now write the parameters file
        # when i get fortran routines, no reason to write file anymore
        with open(os.path.join(cwd, 'params.txt'),'w') as file:
            for k,v in par.iteritems():
                file.write(k + ' ' + str(v) + '\n')
        return self.success

    def __read_magnitude( self, cwd ):
        import os
        from numpy import fromfile, where

        # try finding that file anywhere in the model directory
        for root, dirs, files in os.walk( cwd ):
            for name in files:
                if name == 'mw':
                    mw = fromfile(os.path.join(root, name),'f')[-1]
                    return { 'mw' : mw }
        raise IOError

    def __get_fault_extent( self, cwd, par ):
        import os
        from numpy import fromfile, where, floor

        nx = int(par['fltnx'])
        nz = int(par['fltnz'])

        psv = fromfile( os.path.join(cwd, 'out/psv'), 'f' ).reshape([nz,nx])
        y,x = where( psv > 1.0 ) # returns inds where condition is true
        strtx = x.min()
        print strtx
        endx = x.max()
        print endx
        nflt = floor( (endx - strtx) / 2 )
        if nflt < 0:
            print 'negative fault length, something is wrong.'
            raise ValueError
        return { 'strtx' : strtx, 'nflt' : nflt }
            

class WorkerGroup( object ):
    """
    this needs work, i don't know what im going to use it for
    but i know it will be necessary for more functionality later, maybe managing the
    processes better when i need it, right now it's probably dumber than python's list class
    but that's okay.
    """
    def __init__(self):
        self.jobs = []

    def __iter__(self):
        for job in self.jobs:
            yield job

    def __bool__(self):
        if self.jobs:
            return True
        else:
            return False

    def add( job ):
        self.jobs.append( job )

    def run_all():
        for job in self.jobs: job.start()
        for job in self.jobs: job.join()
