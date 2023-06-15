import time
import psutil

def measure_execution(func, *args, **kwargs):
    start_time = time.time()
    process = psutil.Process()

    # Get the initial memory usage
    initial_memory = process.memory_info().rss

    # Execute the function
    func(*args, **kwargs)

    # Calculate the execution time
    execution_time = time.time() - start_time

    # Calculate the memory usage
    final_memory = process.memory_info().rss
    used_memory = final_memory - initial_memory

    return execution_time, used_memory