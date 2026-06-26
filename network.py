import subprocess
import json

"""
this script :
- checks if the network's ssid is in the allow list 
"""

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

#  get the ssid - check if it's allowed or not
def is_on_allowed_network( config):
    ssid = get_ssid()

    if ssid is None:
        return False
    return ssid in config.get("allowed_networks" , [])
