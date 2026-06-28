import os
import time
import json
import threading
# inotify = inotify_simple.INotify()


"""
This script : 
- scans the folders from the config
- list all the files in it
- then polls every `poll_time` - and checks for new files
"""

poll_time = 5
queue_lock = threading.Lock()


def scan_folders(watch_folders: list, valid_extensions: list = None):
    found = set()
    for folder in watch_folders:
        if not os.path.isdir(folder):
            print(f"Skipping folder (not a directory or does not exist): {folder}")
            continue
        try:
            for filename in os.listdir(folder):
                if filename.startswith("."):    # Skips dot files
                    continue
                filepath = os.path.join(folder, filename)
                if not os.path.isfile(filepath):  # Skips directories
                    continue
                if valid_extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in valid_extensions:
                        continue
                found.add( os.path.realpath(filepath) )
        except Exception as e:
            print(f"Error scanning folder {folder}: {e}")

    return found

def add_to_queue(filename):
    with queue_lock:
        try:
            with open("queue.json" , "r") as queue_json:
                queue_json_dict = json.load(queue_json)
        except (FileNotFoundError , json.JSONDecodeError):
            print(f"The queue.json file likely don't exist :(")
            queue_json_dict = {"queued_files": []}

        if "queued_files" not in queue_json_dict:
            queue_json_dict["queued_files"] = []    # adds queued_file key in the json file

        real_path = os.path.realpath(filename)
        if real_path not in queue_json_dict["queued_files"]: 
            queue_json_dict["queued_files"].append(real_path)

        with open("queue.json" , "w") as queue_json:
            json.dump(queue_json_dict , queue_json , indent=2)


# handles the flow - argument passed - the config file
def watcher_handler(config):
    print(f"The watcher is watching...")
    watch_folders = config.get("watch_folders", [])
    valid_extensions = config.get("valid_extensions", [])
    
    known_files = scan_folders(watch_folders, valid_extensions)

    while True:
        time.sleep(poll_time)
        # files that are currently in each folder
        currentfiles = scan_folders(watch_folders, valid_extensions)

        try:
            with open( "uploaded_files.json" , "r") as uploaded:
                uploaded_dict = json.load(uploaded)

                for file_name in uploaded_dict["uploaded_files"]:
                    known_files.add(file_name)
        except Exception as e:
            pass
        new_files = currentfiles - known_files      # finds the new files that appeared

        if( new_files):
            for file in new_files:
                add_to_queue(file)



        known_files = currentfiles # updates known files, since it's queued