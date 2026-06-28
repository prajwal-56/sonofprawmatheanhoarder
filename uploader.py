import os
import time
import requests
import json
from watcher import queue_lock, poll_time
from network import is_on_allowed_network
from dotenv import load_dotenv

"""
This script sends the post request that contains each file 
after reading from the queue.json
"""

load_dotenv()

token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

uploaded_json = "uploaded_files.json"

def upload_file(file):
    # choose the endpoint
    ext = str(file).lower()
    if ext.endswith((".png", ".jpeg", ".jpg", ".webp")):
        with open(file, "rb") as img:
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": img}
            )
            return response
    elif ext.endswith((".mp4", ".mkv", ".mov")):
        with open(file, "rb") as vdo:
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo",
                data={"chat_id": chat_id},
                files={"video": vdo}
            )
            return response
    else:
        return None


def log_uploaded_files(file):
    
    try:
        if os.path.exists(uploaded_json):
            with open( uploaded_json , "r") as uploaded:
                uploaded_dict = json.load(uploaded)

                uploaded_dict["uploaded_files"].append(file)

            with open(uploaded_json , "w") as uploaded:

                json.dump(uploaded_dict , uploaded, indent=2)

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"{uploaded_json} file not found or it's broken")
        return 
    
    for file in uploaded_dict:



# reades the queue.json - calls upload_file for every file that's queued and removes if that's uploaded successfully
def queue_handler():
    with queue_lock:
        try:
            with open("queue.json", "r") as queue_json:
                queued_files = json.load(queue_json).get("queued_files", [])
        except (FileNotFoundError, json.JSONDecodeError):
            print("queue.json is empty or doesn't exist. Nothing to upload")
            return

    if not queued_files:
        return

    to_remove = []

    for file in queued_files:
        if not os.path.exists(file):
            print(f"File doesn't exist no more. Removing from queue... : {file}")
            to_remove.append(file)
            continue

        try:
            response = upload_file(file)
            if response is None:
                print(f"Skipping unsupported file format: {file}")
                to_remove.append(file)
                log_uploaded_files(file)
                continue

            if response.status_code == 200:
                print(f"yay ! {file} uploaded!")
                to_remove.append(file)
            else:
                print(f"{file} wasn't uploaded")
                print(f"STATUS CODE : {response.status_code}")
                print(f"RESPONSE : {response.text}")
        except Exception as e:
            print(f"Error uploading {file}: {e}")

    if to_remove:
        with queue_lock:
            try:
                with open("queue.json", "r") as queue_json:
                    current_queue_dict = json.load(queue_json)
            except (FileNotFoundError, json.JSONDecodeError):
                current_queue_dict = {"queued_files": []}

            if "queued_files" not in current_queue_dict:
                current_queue_dict["queued_files"] = []     # adds empty queued_files field

            for file in to_remove:
                if file in current_queue_dict["queued_files"]:
                    current_queue_dict["queued_files"].remove(file)

            print(f"Writing queue : {current_queue_dict['queued_files']}")
            with open("queue.json", "w") as queue_json:
                json.dump(current_queue_dict, queue_json, indent=2)


# handles the flow - argument - the config file
def uploader_handler(config):
     
    print("uploader initialized..")

    while True:
        time.sleep(poll_time)
        if is_on_allowed_network(config):
            queue_handler()
        else: 
            print("Not on allowed List. Skipping...")