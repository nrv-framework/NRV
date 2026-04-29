import csv
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess

class GPU:
    """
    Container describing one GPU reported by ``nvidia-smi``.
    """

    def __init__(
        self,
        ID,
        uuid,
        load,
        memoryTotal,
        memoryUsed,
        memoryFree,
        driver,
        gpu_name,
        serial,
        display_mode,
        display_active,
        temp_gpu,
        vendor=None,
        architecture=None,
        cores=None,
    ):
        """
        Store the hardware and usage information associated with one GPU.

        Parameters
        ----------
        ID : int
            GPU index reported by ``nvidia-smi``.
        uuid : str
            Unique identifier of the GPU.
        load : float
            Current compute load of the GPU.
        memoryTotal : float
            Total memory available on the GPU.
        memoryUsed : float
            Memory currently used on the GPU.
        memoryFree : float
            Free memory currently available on the GPU.
        driver : str
            Installed GPU driver version.
        gpu_name : str
            Human-readable GPU model name.
        serial : str
            GPU serial number when available.
        display_mode : str
            Display mode returned by ``nvidia-smi``.
        display_active : str
            Display activity state returned by ``nvidia-smi``.
        temp_gpu : float
            Current GPU temperature.
        """
        self.id = ID
        self.uuid = uuid
        self.load = load
        self.memoryUtil = float(memoryUsed) / float(memoryTotal)
        self.memoryTotal = memoryTotal
        self.memoryUsed = memoryUsed
        self.memoryFree = memoryFree
        self.driver = driver
        self.name = gpu_name
        self.serial = serial
        self.display_mode = display_mode
        self.display_active = display_active
        self.temperature = temp_gpu
        self.vendor = vendor
        self.architecture = architecture
        self.cores = cores


def safeFloatCast(strNumber):
    """
    Convert a string to a floating-point value.

    Parameters
    ----------
    strNumber : str
        String representation of the number to convert.

    Returns
    -------
    float
        Converted value, or ``nan`` if conversion fails.
    """
    try:
        number = float(strNumber)
    except ValueError:
        number = float("nan")
    return number


def _run_command(command, timeout=5):
    """
    Run a system command and return its standard output as text.
    """
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("UTF-8", errors="replace")


def _parse_memory_to_mb(value):
    """
    Parse a memory value expressed as bytes, MB/MiB, or GB/GiB to MBytes.
    """
    if value is None:
        return float("nan")
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 1024**2 if number > 1024**3 else number

    text = str(value).strip().replace(",", ".")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([kmgt]?i?b|bytes?)?", text, re.I)
    if match is None:
        return safeFloatCast(text)

    number = float(match.group(1))
    unit = (match.group(2) or "mb").lower()
    if unit in ("b", "byte", "bytes"):
        return number / 1024**2
    if unit in ("kb", "kib"):
        return number / 1024
    if unit in ("gb", "gib"):
        return number * 1024
    if unit in ("tb", "tib"):
        return number * 1024**2
    return number


def _make_gpu(
    ID,
    uuid="",
    load=float("nan"),
    memoryTotal=float("nan"),
    memoryUsed=float("nan"),
    memoryFree=float("nan"),
    driver="",
    gpu_name="",
    serial="",
    display_mode="",
    display_active="",
    temp_gpu=float("nan"),
    vendor=None,
    architecture=None,
    cores=None,
):
    """
    Build a GPU object while avoiding division by zero for partial backends.
    """
    if memoryTotal == 0:
        memoryTotal = float("nan")
    return GPU(
        ID,
        uuid,
        load,
        memoryTotal,
        memoryUsed,
        memoryFree,
        driver,
        gpu_name,
        serial,
        display_mode,
        display_active,
        temp_gpu,
        vendor,
        architecture,
        cores,
    )


def _get_nvidia_smi_path():
    """
    Locate the NVIDIA SMI executable.
    """
    if platform.system() == "Windows":
        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi is None and "systemdrive" in os.environ:
            nvidia_smi = (
                "%s\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe"
                % os.environ["systemdrive"]
            )
        return nvidia_smi
    return shutil.which("nvidia-smi")


def _get_nvidia_gpus():
    """
    Query the local machine for NVIDIA GPUs using ``nvidia-smi``.

    Returns
    -------
    list[GPU]
        List of detected GPUs. An empty list is returned when ``nvidia-smi``
        is unavailable or the query fails.
    """
    nvidia_smi = _get_nvidia_smi_path()
    if nvidia_smi is None:
        return []

    # Get ID, processing and memory utilization for all GPUs
    output = _run_command(
        [
            nvidia_smi,
            "--query-gpu=index,uuid,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode,temperature.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    if output is None:
        return []

    GPUs = []
    for vals in csv.reader(output.splitlines(), skipinitialspace=True):
        if len(vals) < 12:
            continue
        GPUs.append(
            _make_gpu(
                int(vals[0]),
                vals[1],
                safeFloatCast(vals[2]) / 100,
                safeFloatCast(vals[3]),
                safeFloatCast(vals[4]),
                safeFloatCast(vals[5]),
                vals[6],
                vals[7],
                vals[8],
                vals[10],
                vals[9],
                safeFloatCast(vals[11]),
                vendor="NVIDIA",
                architecture="cuda",
            )
        )
    return GPUs  # (deviceIds, gpuUtil, memUtil)


def _load_system_profiler(data_type):
    """
    Return parsed macOS system_profiler items for one data type.
    """
    system_profiler = shutil.which("system_profiler")
    if system_profiler is None:
        return []
    output = _run_command([system_profiler, data_type, "-xml"], timeout=10)
    if output is None:
        return []
    try:
        reports = plistlib.loads(output.encode("UTF-8"))
    except (plistlib.InvalidFileException, ValueError):
        return []

    items = []
    for report in reports:
        items.extend(report.get("_items", []))
    return items


def _get_apple_unified_memory_mb():
    """
    Read total unified memory on macOS in MBytes.
    """
    for item in _load_system_profiler("SPHardwareDataType"):
        memory = item.get("physical_memory")
        if memory:
            return _parse_memory_to_mb(memory)

    sysctl = shutil.which("sysctl")
    if sysctl is not None:
        output = _run_command([sysctl, "-n", "hw.memsize"])
        if output is not None:
            return _parse_memory_to_mb(safeFloatCast(output.strip()))
    return float("nan")


def _get_vm_stat_memory_mb(total_memory):
    """
    Estimate available and used macOS unified memory from vm_stat.
    """
    vm_stat = shutil.which("vm_stat")
    if vm_stat is None:
        return float("nan"), float("nan")
    output = _run_command([vm_stat])
    if output is None:
        return float("nan"), float("nan")

    page_size = 4096
    first_line = output.splitlines()[0] if output.splitlines() else ""
    page_size_match = re.search(r"page size of ([0-9]+) bytes", first_line)
    if page_size_match is not None:
        page_size = int(page_size_match.group(1))

    pages = {}
    for line in output.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        pages[key.strip()] = safeFloatCast(value.strip().rstrip("."))

    free_pages = (
        pages.get("Pages free", 0)
        + pages.get("Pages inactive", 0)
        + pages.get("Pages speculative", 0)
    )
    free_memory = free_pages * page_size / 1024**2
    used_memory = total_memory - free_memory
    return used_memory, free_memory


def _get_apple_gpus():
    """
    Query Apple GPUs through macOS system_profiler.
    """
    if platform.system() != "Darwin":
        return []

    total_memory = _get_apple_unified_memory_mb()
    used_memory, free_memory = _get_vm_stat_memory_mb(total_memory)
    driver = platform.release()
    GPUs = []
    for device_id, item in enumerate(_load_system_profiler("SPDisplaysDataType")):
        vendor = item.get("spdisplays_vendor", "")
        name = item.get("sppci_model") or item.get("_name", "")
        if "apple" not in str(vendor).lower() and "apple" not in str(name).lower():
            continue

        metal_status = item.get("spdisplays_metal", "")
        cores = safeFloatCast(item.get("sppci_cores", "nan"))
        GPUs.append(
            _make_gpu(
                device_id,
                uuid=item.get("spdisplays_device-id", ""),
                load=float("nan"),
                memoryTotal=total_memory,
                memoryUsed=used_memory,
                memoryFree=free_memory,
                driver=driver,
                gpu_name=name,
                serial="",
                display_mode=item.get("sppci_bus", ""),
                display_active=metal_status,
                temp_gpu=float("nan"),
                vendor="Apple",
                architecture="metal",
                cores=int(cores) if not cores != cores else None,
            )
        )
    return GPUs


def _flatten_json(data, prefix=""):
    """
    Flatten nested dictionaries/lists into path-value pairs.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            yield from _flatten_json(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            yield from _flatten_json(value, f"{prefix}.{index}" if prefix else str(index))
    else:
        yield prefix, data


def _find_json_value(data, *patterns):
    """
    Return the first flattened JSON value whose key path contains all patterns.
    """
    lowered_patterns = [pattern.lower() for pattern in patterns]
    for key, value in _flatten_json(data):
        lower_key = key.lower()
        if all(pattern in lower_key for pattern in lowered_patterns):
            return value
    return None


def _load_amd_smi_json(*arguments):
    """
    Run amd-smi and parse JSON output.
    """
    amd_smi = shutil.which("amd-smi")
    if amd_smi is None:
        return None
    output = _run_command([amd_smi, *arguments, "--json"], timeout=10)
    if output is None:
        return None
    try:
        return json.loads(output)
    except ValueError:
        return None


def _get_amd_smi_gpus():
    """
    Query AMD GPUs through the newer amd-smi command when available.
    """
    device_list = _load_amd_smi_json("list")
    if device_list is None:
        return []

    devices = device_list if isinstance(device_list, list) else list(device_list.values())
    GPUs = []
    for device_id, device in enumerate(devices):
        static = _load_amd_smi_json("static", "-g", str(device_id)) or {}
        metric = _load_amd_smi_json("metric", "-g", str(device_id)) or {}
        name = (
            _find_json_value(static, "market", "name")
            or _find_json_value(static, "product", "name")
            or _find_json_value(device, "name")
            or f"AMD GPU {device_id}"
        )
        total_memory = _parse_memory_to_mb(
            _find_json_value(metric, "memory", "total")
            or _find_json_value(static, "memory", "total")
            or _find_json_value(static, "vram", "size")
        )
        used_memory = _parse_memory_to_mb(
            _find_json_value(metric, "memory", "used")
            or _find_json_value(metric, "vram", "used")
        )
        free_memory = (
            total_memory - used_memory
            if not total_memory != total_memory and not used_memory != used_memory
            else float("nan")
        )
        GPUs.append(
            _make_gpu(
                device_id,
                uuid=str(_find_json_value(device, "uuid") or ""),
                load=safeFloatCast(_find_json_value(metric, "gfx", "activity") or "nan")
                / 100,
                memoryTotal=total_memory,
                memoryUsed=used_memory,
                memoryFree=free_memory,
                driver=str(_find_json_value(static, "driver") or ""),
                gpu_name=str(name),
                serial=str(_find_json_value(static, "serial") or ""),
                display_mode="",
                display_active="",
                temp_gpu=safeFloatCast(
                    _find_json_value(metric, "temperature", "edge")
                    or _find_json_value(metric, "temperature")
                    or "nan"
                ),
                vendor="AMD",
                architecture="rocm",
            )
        )
    return GPUs


def _get_rocm_smi_gpus():
    """
    Query AMD GPUs through rocm-smi when amd-smi is unavailable.
    """
    rocm_smi = shutil.which("rocm-smi")
    if rocm_smi is None:
        return []
    output = _run_command(
        [
            rocm_smi,
            "--showproductname",
            "--showuniqueid",
            "--showdriverversion",
            "--showuse",
            "--showmemuse",
            "--showmeminfo",
            "vram",
            "--showtemp",
            "--json",
        ],
        timeout=10,
    )
    if output is None:
        return []
    try:
        data = json.loads(output)
    except ValueError:
        return []

    GPUs = []
    devices = data.values() if isinstance(data, dict) else data
    for device_id, device in enumerate(devices):
        if not isinstance(device, dict):
            continue
        name = (
            _find_json_value(device, "card", "series")
            or _find_json_value(device, "product", "name")
            or f"AMD GPU {device_id}"
        )
        total_memory = _parse_memory_to_mb(_find_json_value(device, "total", "memory"))
        used_memory = _parse_memory_to_mb(_find_json_value(device, "used", "memory"))
        free_memory = (
            total_memory - used_memory
            if not total_memory != total_memory and not used_memory != used_memory
            else float("nan")
        )
        GPUs.append(
            _make_gpu(
                device_id,
                uuid=str(_find_json_value(device, "unique", "id") or ""),
                load=safeFloatCast(_find_json_value(device, "gpu", "use") or "nan")
                / 100,
                memoryTotal=total_memory,
                memoryUsed=used_memory,
                memoryFree=free_memory,
                driver=str(_find_json_value(device, "driver") or ""),
                gpu_name=str(name),
                serial="",
                display_mode="",
                display_active="",
                temp_gpu=safeFloatCast(_find_json_value(device, "temperature") or "nan"),
                vendor="AMD",
                architecture="rocm",
            )
        )
    return GPUs


def getGPUs():
    """
    Query the local machine for GPUs.

    Returns
    -------
    list[GPU]
        List of detected NVIDIA, AMD, and Apple GPUs. An empty list is
        returned when no supported system query backend is available.
    """
    GPUs = []
    GPUs.extend(_get_nvidia_gpus())
    GPUs.extend(_get_amd_smi_gpus())
    GPUs.extend(_get_rocm_smi_gpus())
    GPUs.extend(_get_apple_gpus())
    return GPUs


# end of functions taken from GPutils
