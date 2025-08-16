import os
from random import random
import threading
import time
from linux_playground.utils.path_utils.specific_paths import python_playground_path
from multiprocessing import Process


def generate_file(file_path_name, size_of_files):
    with open(file_path_name, "wb") as f:
        # Generate random bytes
        # write in chunks of 1024 bytes
        times_to_write = size_of_files // 1024
        for _ in range(times_to_write):
            f.write(os.urandom(1024))
    

def generate_random_files(num_of_files: int = 10, 
                          size_of_files: int = 1024 * 1024 * 1024, 
                          directory: str = "data"):
    """
    Generate number of files with random content up to the size we're specifing.

    """
    time_start = time.time()
    data_directory = os.path.join(python_playground_path, directory)
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Directory {data_directory} does not exist.")
    if not os.path.isdir(data_directory):
        raise NotADirectoryError(f"{data_directory} is not a directory.")
    for i in range(num_of_files):
        file_path = os.path.join(data_directory, f"file_{i}.txt")
        # use threads
        generate_file(file_path, size_of_files)
        print(f"Generated file: {file_path} with size {size_of_files} bytes")
    time_end = time.time()
    duration = time_end - time_start
    print(f"time duration: {duration}")

def generate_random_files_threads(num_of_files: int = 10, 
                          size_of_files: int = 1024 * 1024 * 1024, 
                          directory: str = "data"):
    """
    Generate number of files with random content up to the size we're specifing.

    """
    start_time = time.time()
    file_generator_threading = []
    data_directory = os.path.join(python_playground_path, directory)
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Directory {data_directory} does not exist.")
    if not os.path.isdir(data_directory):
        raise NotADirectoryError(f"{data_directory} is not a directory.")
    for i in range(num_of_files):
        file_path = os.path.join(data_directory, f"file_{i}.txt")
        # use threads
        t = threading.Thread(target=generate_file, args=(file_path, size_of_files))
        t.start()
        file_generator_threading.append(t)
        print(f"Generated file: {file_path} with size {size_of_files} bytes")
        # wait for whole of the threads 
    for t in file_generator_threading:
        t.join()
    end_time = time.time()
    duration = end_time - start_time
    print("finished time= {duration}")

def generate_random_files_mp(num_of_files: int = 10, 
                              size_of_files: int = 1024 * 1024 * 1024,  # 1GB
                              directory: str = "data"):
    start_time = time.time()
    processes = []
    data_directory = os.path.join(python_playground_path, directory)
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Directory {data_directory} does not exist.")
    if not os.path.isdir(data_directory):
        raise NotADirectoryError(f"{data_directory} is not a directory.")

    for i in range(num_of_files):
        file_path = os.path.join(data_directory, f"file_{i}.txt")
        p = Process(target=generate_file, args=(file_path, size_of_files))
        p.start()
        processes.append(p)
        print(f"Generating: {file_path} with size {size_of_files} bytes")

    for p in processes:
        p.join()
    
    end_time = time.time()

    duration = end_time - start_time 

    print(f"duration: {duration}")





if __name__ == "__main__":
    generate_random_files_threads()
    