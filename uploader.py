import requests
import json


"""
This script sends the post request that contains each file 
after reading from the queue.json
"""

def upload_file(file ):

    # choose the endpoint
    if str(file).endswith( (".png" , "jpeg", ".jpg", ".webp" )):
        with open(file , "rb") as img:
                response = requests.post(
                                f"https://api.telegram.org/bot{token}/sendPhoto",
                            data={"chat_id": chat_id},
                            files={"photo": img}
                )
                return response
    elif str(file).endswith( ( ".mp4", ".mkv" )):
        with open(file , "rb") as vdo:
                response = requests.post(
                                f"https://api.telegram.org/bot{token}/sendVideo",
                            data={"chat_id": chat_id},
                            files={"video": vdo}
                )
                return response
    else:
        pass

def queue_handler():
     with open("queue.json" , "r+") as queue_json:
        queued_files = json.load(queue_json)["queued_files"]

        for file in queued_files.copy():
            response = upload_file(file)

            if response.status_code == 200:
                print(f"yay ! {file} uploaded!")
                queued_files.remove(file)
            else:
                 print(f"{file} wasn't uploaded")

        queue_json.seek(0)
        json.dump({"queued_files" : queued_files} , queue_json , indent=2)
        queue_json.truncate()
