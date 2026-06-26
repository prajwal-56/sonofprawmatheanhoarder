import os, time
import json
# import inotify_simple

# inotify = inotify_simple.INotify()


"""
This script : 
- scans the folders from the config
- list all the files in it
- then polls every `poll_time` - and checks for new files
"""

poll_time = 5
def scan_folders(watch_folders: list):
    found = set()
    for folder in watch_folders:
        for filename in os.listdir(folder):
            found.add( os.path.join(folder , filename) )

    return found


with open("config.json" , "r") as config_json:
    content = json.load(config_json)

    watch_folders = content['watch_folders']
    

known_files = scan_folders(watch_folders)

def add_to_queue(filename):
    with open("queue.json" , "r+") as queue_json:
        queue_json_dict = json.load(queue_json)
        
        queue_json_dict["queued_files"].append(os.path.realpath(filename))
        queue_json.seek(0) 
        json.dump(queue_json_dict , queue_json , indent=2)
        queue_json.truncate()

while True:
    time.sleep(poll_time)
    # files that are currently in each folder
    currentfiles = scan_folders(watch_folders)

    new_files = currentfiles - known_files      # finds the new files that appeared

    if( new_files):
        for file in new_files:
            add_to_queue(file)

    known_files = currentfiles # updates known files, since it's queued