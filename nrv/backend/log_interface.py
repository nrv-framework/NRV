"""
log_interface handling.

For the moment, the log interface is managed using the pyswarms reporter class to avoid interference between loggers.
"""
import logging
import os
import sys
import tqdm
from icecream import ic
from time import sleep

from .MCore import MCH
from .parameters import parameters

from pyswarms.utils import Reporter


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def init_reporter():
    rep_nrv = Reporter(log_path=dir_path + "/log/NRV.log")
    rep_nrv._default_config["handlers"]["default"]["level"] = "CRITICAL"
    rep_nrv._default_config["formatters"]["standard"][
        "format"
    ] = "%(asctime)s - %(message)s"
    rep_nrv._load_defaults()
    if MCH.do_master_only_work() and os.path.isfile("report.log"):
        os.remove("report.log")
    return rep_nrv


def set_log_level(level, clear_log_file=False):
    if clear_log_file and MCH.do_master_only_work() and os.path.isfile("report.log"):
        os.remove("report.log")
    if level is not None:
        rep_nrv._default_config["loggers"][""]["level"] = level
        rep_nrv._load_defaults()
    return rep_nrv


dir_path = os.environ["NRVPATH"] + "/_misc"
rep_nrv = init_reporter()


# !! ISSUE:
# Compatibility between logging and pyswarms when pyswarms is imported (not used necessarily)
# all messages log are also printed

# !! TEMPORARY SOLUTION
# Using a pyswarms reporter to log messages
# see old code commented

# logger = logging.getLogger()

# # logging config
# logging.basicConfig(
#     filename=dir_path + "/log/NRV.log",
#     level=logging.INFO,
#     format="%(asctime)s %(message)s",
#     datefmt="%m/%d/%Y %I:%M:%S %p",
# )


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
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]

    message = ""
    error = None
    for arg in args:
        print(type(arg), isinstance(arg, Exception))
        if isinstance(arg, type) and isinstance(arg(), Exception):
            error = arg
        else:
            message += str(arg)
    if MCH.is_alone():
        if parameters.LOG_Status:
            rep_nrv.log(message, lvl=logging.ERROR)
            # logger.error(message, lvl=logging.ERROR)
        if verbose and parameters.VERBOSITY_LEVEL >= 1:
            print(bcolors.FAIL + "NRV ERROR: " + message + bcolors.ENDC)
    else:
        err = (
            "NRV ERROR: "
            + message
            + "\n encountered in process "
            + str(MCH.rank)
            + " out of "
            + str(MCH.size)
        )
        if parameters.LOG_Status:
            rep_nrv.log(err, lvl=logging.ERROR)
            # logger.error(err, lvl=logging.ERROR)
        if parameters.VERBOSITY_LEVEL >= 1:
            print(err)
            sys.stdout.flush()
    if out == 0:
        out = 1
    if not error is None:
        raise error(message)
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
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]
    message = ""
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        if parameters.LOG_Status:
            rep_nrv.log("NRV DEBUG: " + message, lvl=logging.DEBUG)
            # logger.warning("NRV WARNING: " + message)
        if verbose and parameters.VERBOSITY_LEVEL >= 2:
            print(bcolors.WARNING + "NRV WARNING: " + message + bcolors.ENDC)
    else:
        war = (
            "NRV WARNING: "
            + message
            + "\n encountered in process "
            + str(MCH.rank)
            + " out of "
            + str(MCH.size)
        )
        if parameters.LOG_Status:
            rep_nrv.log(war, lvl=logging.DEBUG)
            # logger.warning(war)
        if MCH.do_master_only_work() and parameters.VERBOSITY_LEVEL >= 2:
            print(bcolors.WARNING + war + bcolors.ENDC)
            sys.stdout.flush()
        elif parameters.VERBOSITY_LEVEL >= 4:
            print(bcolors.WARNING + war + bcolors.ENDC)
            sys.stdout.flush()
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
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]
    message = ""
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        if parameters.LOG_Status:
            rep_nrv.log("NRV DEBUG: " + message, lvl=logging.INFO)
            # logger.info("NRV DEBUG: " + message)
        if verbose and parameters.VERBOSITY_LEVEL >= 3:
            print("NRV INFO: " + message)
    else:
        inf = (
            "NRV INFO: "
            + message
            + "\n from process "
            + str(MCH.rank)
            + " out of "
            + str(MCH.size)
        )
        if parameters.LOG_Status:
            rep_nrv.log(inf, lvl=logging.INFO)
            # logger.info(inf)
        if parameters.VERBOSITY_LEVEL >= 4:
            print(inf)
            sys.stdout.flush()


def pass_debug_info(*args, **kwargs):
    """
    Pass an info to the log and to the prompt for the master process (process ID 0) in case of
    parallel computing.

    Parameters
    ----------
    *args   :
        anything to pass as info
    """
    verbose = True
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]
    message = ""
    for arg in args:
        message += str(arg)
    if MCH.is_alone():
        if parameters.LOG_Status and parameters.VERBOSITY_LEVEL >= 4:
            rep_nrv.log("NRV DEBUG: " + message, lvl=logging.DEBUG)
            # logger.info("NRV DEBUG: " + message)
        if verbose and parameters.VERBOSITY_LEVEL >= 4:
            print("NRV DEBUG: " + message)
    else:
        inf = (
            "NRV DEBUG: "
            + message
            + "\n from process "
            + str(MCH.rank)
            + " out of "
            + str(MCH.size)
        )
        if parameters.LOG_Status:
            rep_nrv.log(inf, lvl=logging.DEBUG)
            # logger.info(inf)
        if parameters.VERBOSITY_LEVEL >= 4:
            print(inf)
            sys.stdout.flush()




########
# pbar #
########
class pbar():
    """
    Progess bar object compatible with MPI
    """
    instanciate = True
    def __init__(self, n_tot, label=""):
        if not MCH.is_alone():
            label = f"{MCH.rank}: " + label
        self.__instantiate_delay()
        self._pbar = tqdm.tqdm(total=n_tot, desc=label, position=MCH.rank)
    
    def __del__(self):
        del self._pbar
        if MCH.do_master_only_work():
            # blanck print for new line
            print()
            sys.stdout.flush()

    def __instantiate_delay(self):
        # Dirty hack to prevent skiping two lines 
        sleep(0.05*(MCH.rank))

    def set_label(self, label=""):
        if not MCH.is_alone():
            label = f"{MCH.rank}: " + label
        self.__instantiate_delay()
        self._pbar.set_description(label)
        sys.stdout.flush()

    def reset(self, n_tot=None):
        self.__instantiate_delay()
        if n_tot is None:
            self._pbar.reset()
        else:
            self._pbar.reset(n_tot)

    def update(self, i=1):
        self._pbar.update(i)
        sys.stdout.flush()


def progression_popup(current, max_iter, begin_message="", end_message="", endl=""):
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
        print(
            begin_message + f"{current + 1}" + "/" + str(max_iter) + end_message,
            end=endl,
        )
        if current == max_iter - 1:
            print("\n")


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
