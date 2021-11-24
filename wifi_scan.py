#function of import and install
def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        from pip._internal import main
        print("installing: "+package)
        main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


install_and_import("pexpect")
install_and_import("json")


import os
import time
import pexpect
import subprocess
import sys
import datetime
import json


class BashError(Exception):
    """raised, when bluetoothctl fails to start."""
    pass


def get_output(command, pause = 0):
    """Run a command in bluetoothctl prompt, return output as a list of lines."""
    out = subprocess.check_output(command, shell = True)
    #child = pexpect.spawn(command, echo = False)

    #child.send(command + "\n")
    time.sleep(pause)
    #start_failed = child.expect(["bluetooth", pexpect.EOF])

    #if start_failed:
    #    raise BashError("Bash failed after running " + command)

    #return child.before.decode("utf-8").split("\r\n")
    return out.decode("utf-8").split("Cell")




lines=get_output("sudo iwlist wlan0 scan")
all_access_points_unclean=dict()
true_count=0

f=open("wifi_data.json","a")

while(1):
    all_access_points=dict()
    for line in lines[1:]:
        true_count+=1
        #print(line)
        count=line.split(" - ")[0]

        data=line.split(" - ")[1]



        address=data.split("\n")[0].replace("Address: ","")

        channel=int(data.split("Channel:")[1].split("\n")[0])

        frequency=data.split("Frequency:")[1].split(" (")[0]

        quality=data.split("Quality=")[1].split(" ")[0]

        signal_level=data.split("Signal level=")[1].split("\n")[0]

        encrypted=data.split("Encryption key:")[1].split("\n")[0]
        if "on" in encrypted:encrypted=True
        else:encrypted=False


        essid=data.split("ESSID:")[1].split("\n")[0]

        other=data.replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")


        all_access_points_unclean.update({int(true_count):{"address":address,
            "channel":channel,
            "frequency":frequency,
            "quality":quality,
            "signal_level":signal_level,
            "encrypted":encrypted,
            "essid":essid,
            "datetime":str(datetime.datetime.now()),
            "other":other}})

        f.write(json.dumps(all_access_points_unclean))

print(all_access_points_unclean)


