"""
This module demonstrates the difference in execution time between single-threaded and multi-threaded
programs in Python. 
It defines a simple worker function that simulates a task by sleeping for 2 seconds.
It then runs this function in both single-threaded and multi-threaded contexts, measuring the time taken
for each execution.

python time.sleep() is used to simulate a blocking operation, allowing us to see the benefits of concurrency.
it's a blocking operation because it's getting out of python's Global Interpreter Lock (GIL) and allowing other threads to run.
"""
import threading
import time


def worker(name):
    print(f"{name} started")
    time.sleep(2)
    print(f"{name} finished")

# Single-threaded execution
start = time.perf_counter()
worker("Worker-1")
worker("Worker-2")
print(f"Single-threaded time: {time.perf_counter() - start:.2f} seconds")

# Multi-threaded execution
start = time.perf_counter()
thread1 = threading.Thread(target=worker, args=("Thread-1",))
thread2 = threading.Thread(target=worker, args=("Thread-2",))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
print(f"Multi-threaded time: {time.perf_counter() - start:.2f} seconds")