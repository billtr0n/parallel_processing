import shutil
import os
from multiprocessing import Process

class SimpleTaskWorker( Process ):
    def __init__(self, *args, **kwargs):
        super(SimpleTaskWorker, self).__init__(*args, **kwargs) 
        self.daemon = True
        self.tasks = kwargs['args'][0]

    # this is called when the process start() is called
    def run(self):
        for t in iter(self.tasks.get, None):
            t.execute_task()
            self.tasks.task_done()
        self.tasks.task_done()

class SimpleTask( object ):
    def __init__(self, task, params=None):
        if hasattr(task, '__call__'):
            self.task = task
        else:
            print 'task should be a function.'
        self.params = params

    def execute_task(self):
        self.task( self.params )

    def ready(self):
        return True
