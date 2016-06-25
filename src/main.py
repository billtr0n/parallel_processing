import os
import subprocess

from workers import ModelWorker, WorkerGroup
from tasks import plot_gmpe, calc_gmpe


# implement way to manage the number of threads that are being launched, so that only n threads can be active
# at any given time, needs to keep track of the threads that are being launched by each worker.

# TODO: implement some type of logging information

# Tasks:
# TODO: implement making other types of figures.
# TODO: incorporate seismogram class into it, and custom figure types
# TODO: commit information about models to the database (another task).
# TODO: figure out how to use web.py framework to server jinja template

def main():
    # this dict is used to pass arguments needed for tasks, tasks should be a function
    # this will also go away when this is set to run in single directory, or will be in python
    # config file with other configurations
    params = {
             'root_dir'    : '/media/sf_Dropbox/Current/simulations/5mpa_a007_mu0_0.225_eq_co_1mpa',
             'script_dir'  : '/media/sf_Dropbox/Current/scripts/scripts',
             'script_name' : 'gmpe_calc.m',
             }

    group = WorkerGroup()
    # initially assume all tasks on each model are sequential
    # will eventually define tasks with dependencies
    # or break them down into groups that can be executed concurrently.
    tasks = [calc_gmpe,]
    # we don't care what the name of the folder is.
    for d in os.listdir(params['root_dir']):
        cwd = os.path.join(params['root_dir'], d)
        params['cwd'] = cwd
        # we only care its a directory
        if os.path.isdir( cwd ):
            # workers must subclass thread, and implement the init() method
            job = ModelWorker( tasks, params=params )
            if job.init():
                # add to workergroup
                group.add(job)

    # launch threads
    if group:
        print 'Processes started. Waiting for completion.'
        for p in group: p.start()
        for p in group: p.join()
        # finalize
        print 'All processes finished!.'
    else:
        print 'No models found. Trying again later'


if __name__ == "__main__":
    main()
