from multiprocessing import JoinableQueue
from workers import SimpleTaskWorker

class SimpleTaskWorkerManager( object ): # os.cpu_count() also for default?
    """
    this will use a queue to keep track of all the total tasks and assign a fixed amount of
    workers to finish all of the tasks.
    """
    def __init__(self, tasks = None, max_workers = 8):
        self.workers = []
        if tasks is None:
            self.tasks = JoinableQueue()
        else:
            self.tasks = tasks
        self.total_tasks = 0
        self.num_workers = max_workers
        

    def __nonzero__(self):
        if self.tasks.empty(): 
            return True
        return False

    def add_task_to_queue( self, task ):
        try:
            self.tasks.put( task )
            self.total_tasks += 1
        except Exception as e:
            print 'unable to add worker to queue. error code: %s' % str(e)

    def start_working( self ):
        if self.num_workers > self.total_tasks:
            self.num_workers = self.total_tasks
        print 'assigning %d workers to help you.' % self.num_workers
        for _ in range( self.num_workers ):
            p = SimpleTaskWorker( args=(self.tasks,) )
            p.start()
            self.workers.append(p)
        self.tasks.join()


    def wait_all( self ):
        for worker in self.workers:
            self.tasks.put(None)
        for worker in self.workers:
            worker.join()





            


