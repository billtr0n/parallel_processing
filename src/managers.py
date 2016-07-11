from multiprocessing import JoinableQueue
from workers import SimpleTaskWorker
import logging

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
        logging.info( 'created manager with %d workers' % self.num_workers )
        

    def __nonzero__(self):
        if self.tasks.empty(): 
            return True
        return False

    def add_task_to_queue( self, task ):
        try:
            if task.ready:
                self.tasks.put( task )
                logging.info('adding task %s to queue' % str(task))
                self.total_tasks += 1
            else:
                logging.warning('unable to add task to queue. task could not be made ready') 
        except Exception as e:
            logging.warning( 'unable to add task to queue. error code: %s' % str(e) )

    def start_working( self ):
        if self.num_workers > self.total_tasks:
            self.num_workers = self.total_tasks
            logging.info('less tasks than workers, reducing to %d workers' % self.num_workers )
        print 'assigning %d workers to help you.' % self.num_workers
        for _ in range( self.num_workers ):
            p = SimpleTaskWorker( args=(self.tasks,) )
            p.start()
            self.workers.append(p)
        logging.info('started workers.')
        self.tasks.join()


    def wait_all( self ):
        logging.info('waiting for workers.')
        for worker in self.workers:
            self.tasks.put(None)
        for worker in self.workers:
            worker.join()





            


