import os
import queue
from pathlib import Path
import requests
import sys
import threading
import time

from linux_playground.utils.path_utils.specific_paths import relative_path

FILTERED = [".jpg", ".gif", ".png", ".css"]
TARGET = "http://localhost:9999/"
THREADS = 150
answers = queue.Queue()
web_paths = queue.Queue()

def gather_paths(wordpress_directory_path: str, specific_filter: list[str] = FILTERED):
    print("[debug] start gathering the paths")
    print(f"[debug] Will walk other the {wordpress_directory_path} path")
    print(f"[debug] search for files, Filter the following(Not looking for that files): {specific_filter}")
    print(f"[debug] starting...")
    for root, _, files in os.walk(wordpress_directory_path):
        root = root.replace(wordpress_directory_path, "")
        root = root or "/"
        print(f"[debug] walking the files: {files}")
        for fname in files:
            if Path(fname).suffix in specific_filter:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(f"found path")
            print(path)
            web_paths.put(path)
    print(f"[debug] finished whole files in wordpress directory. \nfound the following: {web_paths}")


def is_http_server_alive(target: str = TARGET):
    return requests.get(target).status_code == 200



def get_from_real_target_answers(target: str = TARGET):
    paths_to_check = len(web_paths.queue)
    counter = 0
    print(f"paths to check: {paths_to_check}")
    if not is_http_server_alive():
        raise Exception(f"the target: {target} server isn't alive")
    print(f"[debug] starting to find alive-paths status code 200")
    while not web_paths.empty():
        path = web_paths.get() 
        url_with_path = f"{target}{path}"
        time.sleep(0.3)
        res = requests.get(url_with_path)
        if res.status_code == 200:
            answers.put(url_with_path)
            print(f"{counter}/{paths_to_check} + for {path}")
        else:
            print(f"{counter}/{paths_to_check} - status code -> {res.status_code} for {path}")
        counter += 1


def activity_answer_finder():
    my_threads = []
    for _ in range(0, THREADS):
        t = threading.Thread(target=get_from_real_target_answers)
        my_threads.append(t)
    
    # Start each thread
    for t in my_threads:
        t.start()
    
    # wait for whole of the threads to finish
    for t in my_threads:
        t.join()

if __name__ == '__main__':
    wordpress_relative_path = relative_path("wordpress-5.4.1/wordpress")
    
    # producer 
    gather_paths(wordpress_directory_path=wordpress_relative_path)

    # consumer
    activity_answer_finder() # multi-threaded - fast! 
    # get_from_real_target_answers() # single threaded - slow! 
    file_to_write_found_paths = relative_path("wordpress-found-paths.txt")
    with open(file_to_write_found_paths, "w") as f:
        while not answers.empty():
            f.write(f"{answers.get()}\n")
    print("done\n")





    print("[debug] debugging...")
    print("lol")

