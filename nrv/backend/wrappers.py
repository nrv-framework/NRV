"""
NRV-Wrappers and decorator for code clarity
"""
from .MCore import MCH

def singlecore(func):
    '''
    Decorator to restrict the processing on a signel core, always core 0 (master)
    '''
    def wrapper(*args, **kwargs):
        results = None
        if MCH.do_master_only_work():
            results = func(*args, **kwargs)
            return results
        else:
            # do not block other cores
            return results
    return wrapper