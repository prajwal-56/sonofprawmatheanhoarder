import threading
import json
import time
import watcher
import uploader

print(f"Intitalizing...")

with open("config.json") as config_json:
    config = json.load(config_json)

t1 = threading.Thread(target=watcher.watcher_handler, args=(config,))
t2 = threading.Thread(target=uploader.uploader_handler, args=(config,))

print("Threads initilized. \nThe Bot is UP bot 🤖\n")
print(f"👀watching : {config['watch_folders']}")
t1.start()
t2.start()
t1.join()
t2.join()
