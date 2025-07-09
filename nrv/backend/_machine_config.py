import os
import sys
import psutil
import numpy as np

from ._GPU import getGPUs
from ._NRV_Singleton import NRV_singleton


# miscalleneous constants
Mem_KBytes = 1024
Mem_MBytes = Mem_KBytes**2
Mem_GBytes = Mem_KBytes**3
# Constants for sanity check
suported_platforms = [
    "linux",
    "darwin",
    "win32",
    "cygwin",
]
# python min vesion
NRV_PYTHON_VERSION = {
    "major": 3,
    "minor": 12,
    "patch": 0,
}

MIN_REQUIREMENTS = {"CPU_ncores": 1, "Memory_size": 8000}


class MachineConfig(metaclass=NRV_singleton):
    """Singleton to get all machine properties related to computational performances.

    Parameters
    ----------
    memory_unit: int
        Dividor to express all memomry sizes in a given unit,
        Constant already defined, can be:
        * Mem_KBytes (= 1024)
        * Mem_MBytes (= Mem_KBytes**2)
        * Mem_GBytes (= Mem_KBytes**3
    """

    def __init__(self, memory_unit=Mem_MBytes):
        self._explore_OS()
        self._explore_Python()
        self._explore_Float()
        self._explore_CPU()
        self._explore_GPU()
        self._explore_memory(unit=memory_unit)

    def __str__(self):
        current_str = f"""%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATIONS ON OS %%
%%%%%%%%%%%%%%%%%%%%%%%%
OS platform: {self.OS_name}
OS version: {self.OS_version}

%%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATIONS ON CPU %%
%%%%%%%%%%%%%%%%%%%%%%%%%
Number of available Cores: {self.CPU_ncores}
CPU number of bits: {self.CPU_nbits}
CPU architecture: {self.CPU_arch}

%%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATIONS ON GPU %%
%%%%%%%%%%%%%%%%%%%%%%%%%
Number of available Cores: {self.GPU_ncores}
GPU total memory: {self.GPU_memory_total}
GPU used memory: {self.GPU_memory_used}
GPU free memory: {self.GPU_memory_free}
GPU memory load: {self.GPU_memory_load}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATIONS ON MEMORY %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
MEMORY total size: {self.MEMORY_size} {self.MEMORY_unit}
MEMORY available: {self.MEMORY_available} {self.MEMORY_unit}
MEMORY available in percent: {self.MEMORY_percent}
MEMORY used: {self.MEMORY_used} {self.MEMORY_unit}
MEMORY free: {self.MEMORY_free} {self.MEMORY_unit}
MEMORY active: {self.MEMORY_active} {self.MEMORY_unit}
MEMORY inactive: {self.MEMORY_inactive} {self.MEMORY_unit}
MEMORY wired: {self.MEMORY_wired} {self.MEMORY_unit}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATIONS ON PYTHON %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Python version: {self.Python_version_major}.{self.Python_version_minor}.{self.Python_version_micro}
Release level: {self.Python_version_releaselevel}
serial: {self.Python_version_serial}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% INFORMATION ON FLOAT REPRESENTATION %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Maximum number of decimal digits that can be faithfully represented in a float: {self.dig}
Difference between 1 and the next representable float: {self.epsilon}
Mantissa digits: {self.mant_dig}
Maximum representable finite floats: {self.max}
Maximum int e such that 10**e, that radix**(e-1), are representable: {self.max_10_exp}, {self.max_exp}
Minimum positive normalized float: {self.min}
Minimum int e such that 10**e, that radix**(e-1), is a normalized float{self.min_10_exp}, {self.min_exp}
Radix of exponent: {self.radix}
Rounding mode used for arithmetic operations: {self.rounds}
Float representation style: {self.float_repr_style}"""
        return current_str

    def _explore_OS(self):
        self.OS_name = sys.platform
        self.OS_version = os.uname().release

    def _explore_Python(self):
        # Python version
        self.Python_version_major = sys.version_info.major
        self.Python_version_minor = sys.version_info.minor
        self.Python_version_micro = sys.version_info.micro
        self.Python_version_releaselevel = sys.version_info.releaselevel
        self.Python_version_serial = sys.version_info.serial
        # imported modules from sys.modules, may be track versions

    def _explore_Float(self):
        self.dig = sys.float_info.dig
        self.epsilon = sys.float_info.epsilon
        self.mant_dig = sys.float_info.mant_dig
        self.max = sys.float_info.max
        self.max_10_exp = sys.float_info.max_10_exp
        self.max_exp = sys.float_info.max_exp
        self.min = sys.float_info.min
        self.min_10_exp = sys.float_info.min_10_exp
        self.min_exp = sys.float_info.min_exp
        self.radix = sys.float_info.radix
        self.rounds = sys.float_info.rounds
        self.float_repr_style = sys.float_repr_style

    def _explore_CPU(self):
        # get number of cores
        self.CPU_ncores = psutil.cpu_count(logical=True)
        # get number of bits
        if sys.maxsize == 2**63 - 1:
            self.CPU_nbits = 64
        elif sys.maxsize == 2**31 - 1:
            self.CPU_nbits = 32
        else:
            print("this is really wierd...")
            self.CPU_nbits = 0.5
        self.CPU_arch = os.uname().machine

    def _explore_GPU(self):
        GPUs = getGPUs()
        self.GPU_ncores = len(GPUs)
        self.GPU_total_memory = 0
        self.GPU_memory_total = 0
        self.GPU_memory_used = 0
        self.GPU_memory_free = 0
        self.GPU_memory_load = 0
        if len(GPUs) > 0:
            for g in GPUs:
                self.GPU_memory_total += g.memoryTotal
                self.GPU_memory_used += g.memoryUsed
                self.GPU_memory_free += g.memoryFree
            self.GPU_memory_load = self.GPU_memory_used / self.GPU_memory_total

    def GPU_update(self):
        GPUs = getGPUs()
        self.GPU_memory_used = 0
        self.GPU_memory_free = 0
        self.GPU_memory_load = 0
        if len(GPUs) > 0:
            for g in GPUs:
                self.GPU_memory_used += g.memoryUsed
                self.GPU_memory_free += g.memoryFree
            self.GPU_memory_load = self.GPU_memory_used / self.GPU_memory_total

    def _explore_memory(self, unit=Mem_MBytes):
        """
        Note: everything is in MBytes
        """
        self.MEMORY_unit_value = unit
        if unit == Mem_KBytes:
            self.MEMORY_unit = "kBytes"
        elif unit == Mem_MBytes:
            self.MEMORY_unit = "MBytes"
        else:
            self.MEMORY_unit = "GBytes"
        self.MEMORY_size = psutil.virtual_memory().total / self.MEMORY_unit_value
        self.MEMORY_available = (
            psutil.virtual_memory().available / self.MEMORY_unit_value
        )
        self.MEMORY_percent = psutil.virtual_memory().percent
        self.MEMORY_used = psutil.virtual_memory().used / self.MEMORY_unit_value
        self.MEMORY_free = psutil.virtual_memory().free / self.MEMORY_unit_value
        self.MEMORY_active = psutil.virtual_memory().active / self.MEMORY_unit_value
        self.MEMORY_inactive = psutil.virtual_memory().inactive / self.MEMORY_unit_value
        if "linux" not in self.OS_name:
            self.MEMORY_wired = psutil.virtual_memory().wired / self.MEMORY_unit_value
        else:
            self.MEMORY_wired = None

    def memory_update(self):
        current_MEMORY_available = (
            psutil.virtual_memory().available / self.MEMORY_unit_value
        )
        current_MEMORY_percent = psutil.virtual_memory().percent
        current_MEMORY_used = psutil.virtual_memory().used / self.MEMORY_unit_value
        current_MEMORY_free = psutil.virtual_memory().free / self.MEMORY_unit_value
        current_MEMORY_active = psutil.virtual_memory().active / self.MEMORY_unit_value
        current_MEMORY_inactive = (
            psutil.virtual_memory().inactive / self.MEMORY_unit_value
        )
        # compute deltas
        delta_available = current_MEMORY_available - self.MEMORY_available
        delta_percent = current_MEMORY_percent - self.MEMORY_percent
        delta_used = current_MEMORY_used - self.MEMORY_used
        delta_free = current_MEMORY_free - self.MEMORY_free
        delta_active = current_MEMORY_active - self.MEMORY_active
        delta_inactive = current_MEMORY_inactive - self.MEMORY_inactive
        # store new values
        self.MEMORY_available = current_MEMORY_available
        self.MEMORY_percent = current_MEMORY_percent
        self.MEMORY_used = current_MEMORY_used
        self.MEMORY_free = current_MEMORY_free
        self.MEMORY_active = current_MEMORY_active
        self.MEMORY_inactive = current_MEMORY_inactive
        return (
            delta_available,
            delta_percent,
            delta_used,
            delta_free,
            delta_active,
            delta_inactive,
        )

    def update(self):
        self.memory_update()
        if self.GPU_ncores > 0:
            self.GPU_update()

    def get_report(self):
        print(self)

    def get_Available_CPU_number(self, threshold: float = 20.0):
        assert (
            threshold >= 0 and threshold <= 100
        ), "Threshold must be between 0 and 100"
        available_CPUs = np.asarray(psutil.cpu_percent(percpu=True)) < threshold
        return np.sum(available_CPUs)

    ### Sanity checks ###
    def sanity_check(self):
        # python checks
        if self.Python_version_major < NRV_PYTHON_VERSION["major"]:
            print("Warning: Python 2 not supported")
        elif self.Python_version_minor < NRV_PYTHON_VERSION["minor"]:
            display_str = (
                "Warning: Python version detected: "
                + str(self.Python_version_major)
                + "."
                + str(self.Python_version_minor)
                + "."
                + str(self.Python_version_micro)
                + "\n minimal python version is "
                + str(NRV_PYTHON_VERSION["major"])
                + "."
                + str(NRV_PYTHON_VERSION["minor"])
                + "."
                + str(NRV_PYTHON_VERSION["patch"])
            )
            print(display_str)
        else:
            print("Current configuration is compatible with NRV requirements")
