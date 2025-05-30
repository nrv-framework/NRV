#pragma parallel
import nrv
from multiprocessing import Process, current_process, parent_process, active_children
import os

def info(title):
    print(title)
    print('module name:', __name__)
    if parent_process() is not None:
        print('parent process:', parent_process().name)
    else:
        print('active childrens:', active_children())
    print('process id:', current_process().name, type(current_process().name))

def f(name):
    info('function f')
    print('hello', name)

if __name__ == '__main__':
    info('main line')
    print(current_process)
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()

