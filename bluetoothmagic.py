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




import os
#os.system("sudo apt install bluetooth bluez libbluetooth-dev")
#os.system("apt install python-bluez")
#os.system("pip3 install pybluez")
#os.system("pip3 install gattlib")
#install_and_import("bluetooth")
install_and_import("pexpect")



#nearby_devices = bluetooth.discover_devices(duration=30) #,lookup_names=True,lookup_class=True,flush_cache=True,device_id=-1)
#print("Found {} devices.".format(len(nearby_devices)))

#for addr, name, class_name in nearby_devices:
#    print("  {} - {} - {}".format(addr, name, class_name))







# bluetooth low energy scan
#from bluetooth.ble import DiscoveryService

#service = DiscoveryService()
#devices = service.discover(2)

#for address, name in devices.items():
#    print("name: {}, address: {}".format(name, address))






import time
import pexpect
import subprocess
import sys
import datetime
import json



class BluetoothctlError(Exception):
    """raised, when bluetoothctl fails to start."""
    pass


class Bluetoothctl: #https://gist.github.com/egorf/66d88056a9d703928f93
    """Wrapper of bluetoothctl utility."""
    stored_devices=list()

    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False)

    def is_number_tryexcept(self,s):
        """ Returns True is string is a number. """
        if type(s)!=type(""):return False
        try:
            float(s)
            return True
        except ValueError:
            return False
        except Exception:
            return False


    def get_output(self, command, pause = 0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        time.sleep(pause)
        start_failed = self.child.expect(["bluetooth", pexpect.EOF])

        if start_failed:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)

        return self.child.before.decode("utf-8").split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            out = self.get_output("scan on")
        except BluetoothctlError as e:
            print(e)
            return None

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            out = self.get_output("discoverable on")
        except BluetoothctlError as e:
            print(e)
            return None
    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        #"Name": attribute_list[2],
                        "Time": str(datetime.datetime.now())
                    }

                    device_info=self.get_device_info(device["mac_address"])
                    #print(device_info)
                    for row in device_info:
                        try:
                            temp=row.split(": ")
                            parm,data=temp[0].strip(),temp[1].strip()
                            if "no"==data:data=False
                            if "yes"==data:data=True
                            if self.is_number_tryexcept(data):data=float(data)
                            if type(data)==type(" ") and "  " in data:data=data.replace('  '," ").replace('  '," ").replace('  '," ").replace("  "," ").replace("  "," ")
                            device.update({parm:data})
                        except Exception as e:
                            #print(e)
                            pass
        if device:self.stored_devices.append(device)
        return device

    def get_stored_devices(self): #call to get all stored data
        return self.stored_devices

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)

            return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = self.get_output("paired-devices")
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)

            return paired_devices

    def get_discoverable_devices(self): #this gets current devices
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()

        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output("info " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            return out

    def record_scan(self): # this records the currnet devices. Call as often as required
        self.get_discoverable_devices()

    def gen_stored_devices(self):
        count=0
        while(1):
            try:
                yield self.stored_devices[count]
                count+=1
            except Exception as e:
                yield None

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = self.get_output("pair " + mac_address, 4)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = self.get_output("remove " + mac_address, 3)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "Device has been removed", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = self.get_output("connect " + mac_address, 2)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = self.get_output("disconnect " + mac_address, 2)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF])
            success = True if res == 1 else False
            return success








#os.system("sudo apt-get install arp-scan")

f= open("/home/pi/bluetooth.json","a")


if __name__ == "__main__":

    print("Init bluetooth...")
    bl = Bluetoothctl()
    print("Ready!")
    bl.start_scan()

    gen=bl.gen_stored_devices()
    #print("Scanning for 10 seconds...")
    while (1):
        #print(i)
        time.sleep(1)
        #bl.get_discoverable_devices()
        bl.record_scan()
        f.write(json.dumps(next(gen)))

    print(bl.get_stored_devices())




