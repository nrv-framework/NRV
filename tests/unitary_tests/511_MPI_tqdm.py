from multiprocessing import Pool, Manager
import numpy as np
from time import sleep
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from multiprocessing import current_process, parent_process, active_children
import os


def worker(task_info):
    """Worker function that returns a numpy array."""
    task_name, task_id, total, progress_dict = task_info

    progress = Progress(
        TextColumn(f"{parent_process().name}"),
        TextColumn(f"[cyan]{current_process().name}: {task_name}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    )
    task = progress.add_task(task_name, total=total)

    # Simulate computation to fill a numpy array
    result_array = np.zeros(10)
    for i in range(total):
        sleep(0.05*(1+task_id))  # Simulate work
        result_array += np.random.rand(10)  # Increment values for demonstration
        progress.advance(task)
        # Update the shared progress state
        progress_dict[task_id] = progress.get_renderable()

    return result_array


def rich_multiprocessing_with_pool():
    """Manages multiprocessing with Rich progress bars using Pool and sums numpy arrays."""
    num_processes = 4
    tasks = [{"task_name": f"Task {i+1}", "total": 100, "task_id": i} for i in range(num_processes)]

    print(current_process().name=="MainProcess", active_children())
    manager = Manager()
    print(current_process().name=="MainProcess", active_children())

    progress_dict = manager.dict()  # Shared dictionary for tracking progress renderables

    # Prepare task info for Pool
    task_info_list = [
        (task["task_name"], task["task_id"], task["total"], progress_dict)
        for task in tasks
    ]

    with Pool(processes=num_processes) as pool:
        print(current_process().name=="MainProcess", active_children())
        with Live(refresh_per_second=10) as live:
            async_results = [pool.apply_async(worker, args=(task_info,)) for task_info in task_info_list]

            while any(not result.ready() for result in async_results):
                # Build a table to display progress bars
                table = Table.grid()
                for task_id, progress in progress_dict.items():
                    table.add_row(progress)
                live.update(table)
            for result in async_results:
                result.wait()
                # sleep(0.1)

            # Collect results from all workers
            arrays = [result.get() for result in async_results]

    # Sum all numpy arrays
    summed_array = np.sum(arrays, axis=0)

    # Print the resulting summed array
    print("Summed Array:", summed_array)


if __name__ == "__main__":
    rich_multiprocessing_with_pool()
