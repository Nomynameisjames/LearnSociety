import time
import psutil
from functools import wraps

def performance_logger(func):
    """
        Decorator to log the memory usage and execution time of a function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        # Get start time
        start_time = time.time()
        # Call the original function
        response = func(*args, **kwargs)
        # Get end time
        end_time = time.time()
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024
        # Log the memory usage and execution time
        print(f"Route: {func.__name__} \t Memory usage: {final_memory-initial_memory:.2f} MB \t Execution time: {(end_time-start_time)*1000:.2f} ms")
        return response
    return wrapper
