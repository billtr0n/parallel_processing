import os
import subprocess
import logging
import time

from workers import SimpleTask
from managers import SimpleTaskWorkerManager  
from tasks.dynamic_rupture_task import process_dynamic_rupture_simulation

# TODO: commit information about models to the database (clean-up process).
# TODO: design templates to show models using html (initially markdown).
# TODO: state-machine to keep track of tasks and states of workers, etc.

def main():
    # this dict is used to pass arguments needed for tasks
    home_dir = os.getcwd()
    # params = {
    #          'root_dir'    : '/media/sf_Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa',
    #          'script_dir'  : '/media/sf_Dropbox/Current/processing/utils',
    #          'script_name' : 'gmpe_calc.m',
    #          'home_dir'    :  home_dir,
    #          }

    params = {
             #'root_dir'    : '/Users/williamsavran/Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa',
             'root_dir' : '/Users/williamsavran/Dropbox/Current/simulations/testing',
             'script_dir'  : '/Users/williamsavran/Dropbox/Current/processing/utils',
             'script_name' : 'gmpe_calc.m',
             'home_dir'    : home_dir,
             }
             
    """ initialize log in directory above root_dir and record year, month, day """
    logging.basicConfig( filename = os.path.join( os.path.dirname( params['root_dir'] ), 
                                            'tasks-' + time.strftime("%Y%m%d") + '.log' ),
                         level = logging.INFO 
                       )

    """ get access to a task manager """
    group = SimpleTaskWorkerManager( max_workers = 8 )

    """ define tasks that are applied to each simulation """
    individual_tasks = [
                        process_dynamic_rupture_simulation
                        # plot_gmpe,
                        # calc_gmpe,
                        # one_point_statistics,
                        # plot_kinematic_fields,
                       ]

    """ apply tasks to group """
    if individual_tasks:
        _queue_individual_tasks( group, individual_tasks, params )

    # """ define and apply tasks that are applied to all simulations """
    # group.add_task_to_queue( SimpleTask( plot_gmpe_group_bias, params=params ) )
    group.start_working()
    group.wait_all()

    print 'All Finished!'


def _queue_individual_tasks( group, tasks, params ):
    """
    Queues tasks that will be applied to every model. For instance, "plot_gmpe" or "calc_one_point_statistics."
    """
    for d in os.listdir( params['root_dir'] ):
            cwd = os.path.join( params['root_dir'], d )
            if os.path.isdir( cwd ):
                params['cwd'] = cwd
                simple_tasks = [ SimpleTask( task, params=params ) for task in tasks ]
                for task in simple_tasks:
                    if task.ready():
                        group.add_task_to_queue( task )


if __name__ == "__main__":
    main()
