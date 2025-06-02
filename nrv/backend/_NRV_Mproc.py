"""
Interface between NRV and multiprocessing tools handling.

.. note::
  In the future, will also be used to handle the compatibility with threading
"""

from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import current_process, active_children
from psutil import cpu_count

_cpu_max_number = cpu_count(logical=True)

_proc_is_master = current_process().name=="MainProcess"
_proc_is_alone = _proc_is_master and len(active_children())==0
_proc_label = current_process().name