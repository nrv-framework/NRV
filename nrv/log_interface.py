"""
NRV-materials
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import os
import logging
import sys
from icecream import ic
from .MCore import *

dir_path = os.path.dirname(os.path.realpath(__file__))
# logging config
logging.basicConfig(filename=dir_path+'/log/NRV.log', level=logging.INFO, format=\
    '%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def rise_error(*args, out=1, **kwargs):
    """
    Rises and error to the log and to the prompt for the master process (process ID 0) in case of
    parallel computing. This function exit the programm.

    Parameters
    ----------
    *args   :
        anything to pass as error message
    out     : int
        programm exit value, must be strictly positive. By default equal to 1
    """
    verbose = True
    if 'verbose' in kwargs:
        verbose = kwargs['verbose']

    message = ''
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        logging.error(message)
        if verbose:
            print('NRV ERROR: '+ message)
    else:
        logging.error('NRV ERROR: '+ message + '\n encountered in process '+str(MCH.rank)+' out of '+str(MCH.size))
    if out == 0:
        out = 1
    sys.exit(out)


def rise_warning(*args, abort=False, **kwargs):
    """
    Rises a warning to the log and to the prompt for the master process (process ID 0) in case of
    parallel computing. This function can exit the programm.

    Parameters
    ----------
    *args   :
        anything to pass as warning message
    abort   : boolean
        if true, the programm exits with the value O (no error) and further computation are avoided,
        by default set to False.
    """
    verbose = True
    if 'verbose' in kwargs:
        verbose = kwargs['verbose']
    message = ''
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        logging.warning('NRV WARNING: '+ message)
        if verbose:
            print('NRV WARNING: '+ message)
    else:
        logging.warning('NRV WARNING: '+ message + '\n encountered in process '+str(MCH.rank)+' out of '+str(MCH.size))
    if abort:
        sys.exit(0)

def pass_info(*args, **kwargs):
    """
    Pass an info to the log and to the prompt for the master process (process ID 0) in case of
    parallel computing.

    Parameters
    ----------
    *args   :
        anything to pass as info
    """

    verbose = True
    if 'verbose' in kwargs:
        verbose = kwargs['verbose']
    message = ''
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        logging.info('NRV INFO: '+ message)
        if verbose:
            print('NRV INFO: '+ message)
    else:
        logging.info('NRV INFO: '+ message + '\n from process '+str(MCH.rank)+' out of '+str(MCH.size))

def progression_popup(current, max_iter, begin_message='', end_message='', endl=''):
    """
    Displays the progression on prompt, for single process only, nothing saved to the log

    Parameters
    ----------
    current         : int
        current iteration
    max_iter        : int
        maximum iteration number
    begin_message   : str
        additional message placed at the start of the progression line
    end_message     : str
        additional message placed after iteration and max at the end of the progression line
    endl            : str
        line termination, by default empty string
    """
    if MCH.is_alone():
        print(begin_message + f"{current+1}" + '/' + str(max_iter) + end_message, end=endl)
        if current == max_iter - 1:
            print('\n')

def prompt_debug(*args):
    """
    outputs for debug, simple redirection to icecream without the installation (see icecream help).
    Could be interesting to redirect also to the log...

    Parameters
    ----------
    *args   :
        anything to pass to icecrean
    """
    ic(*args)
