import os
import subprocess

from workers import SimpleTask
from managers import SimpleTaskWorkerManager  
from tasks import test_task

# TODO: implement some type of logging information
# TODO: implement other tasks.
# TODO: incorporate seismogram class into it, and custom figure types
# TODO: commit information about models to the database (clean-up process).
# TODO: design templates to show models
# TODO: straighten out if tasks should return true or false or raise exception

def main():
    # this dict is used to pass arguments needed for tasks
    home_dir = os.getcwd()
    params = {
             'root_dir'    : '/media/sf_Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa',
             'script_dir'  : '/media/sf_Dropbox/Current/processing/utils',
             'script_name' : 'gmpe_calc.m',
             'home_dir'    : home_dir,
             }
    # params = {
    #          'root_dir'    : '/Users/williamsavran/Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa',
    #          'script_dir'  : '/Users/williamsavran/Dropbox/Current/processing/utils',
    #          'script_name' : 'gmpe_calc.m',
    #          'home_dir'    : home_dir,
    #          }

    group = SimpleTaskWorkerManager( max_workers = 8 )
    # tasks should be functions or implement __call__.
    tasks_functions = [
                      'plot_gmpe',
                      ]
    for d in os.listdir( params['root_dir'] ):
        cwd = os.path.join( params['root_dir'], d )
        if os.path.isdir( cwd ):
            params['cwd'] = cwd
            tasks = [ SimpleTask( task, params=params ) for task in tasks_functions ]
            for task in tasks:
                if task.ready():
                    group.add_task_to_queue( task )
    group.start_working()              
    group.wait_all()
    print 'All Finished!'
if __name__ == "__main__":
    main()
