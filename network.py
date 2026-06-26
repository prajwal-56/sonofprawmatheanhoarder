import subprocess
import json

def get_ssid():
    
    print(f"Trying to get the ssid..." , end="\r")
    # result of termux-wifi-connectioninfo
    connection_info = subprocess.run( ['termux-wifi-connectioninfo'], capture_output=True, text=True )

    # check status of the command 
    if connection_info.returncode == 0:
        # turns it into a python dict
        connection_info_dict = json.loads(connection_info.stdout)
        
        ssid = connection_info_dict.get('ssid')
        ip = connection_info_dict.get('ip')
        print(f"The SSID : {ssid}")
        return ssid
    else:
        return None

def is_ssid_on_allow_list( ssid: str):

    try:
        with open("config.json" , "r") as config_file:
            content = json.load(config_file)

            allow_list = content.get("allowed_networks" , [])

            if ssid in allow_list:
                return True
            else:
                return False
    except FileNotFoundError:
        print("config.json file not found")
        return False