import os
import subprocess


class Sniffer:

    def __init__(self, data_interface):
        self.data_interface = data_interface
        self.mode = self.data_interface.get_hound_mode()

    def scan_access_points(self):
        command = 'iwlist wlan0 s'
        response = os.popen(command)
        result = response.read()
        response.close()

        formatted_results = self.parse_access_point_scan(result)
        return self.data_interface.update_access_points(formatted_results)

    def scan_users(self, ssid):
        self.start_monitor_mode()
        self.sniff_ssid(ssid)
        self.stop_monitor_mode()
        self.refresh_hotspot_connection()

    def scan_user(self, ssid):
        self.start_monitor_mode()
        self.sniff_user(ssid)
        self.stop_monitor_mode()
        self.refresh_hotspot_connection()

    def refresh_hotspot_connection(self):
        down = subprocess('ifdown wlan0')
        down.communicate()
        up = subprocess('ifup wlan0')
        up.communicate()

    def start_monitor_mode(self):
        monitor = subprocess('airmon-ng start wlan0')
        monitor.communicate()

    def stop_monitor_mode(self):
        monitor = subprocess('airmon-ng stop mon0')
        monitor.communicate()

    def sniff_ssid(self, ssid):
        command = 'airodump-ng mon0 --bssid {0} --write /home/source/scans/hound_scan --output-format csv'.format(ssid)
        sniffer = subprocess(command)
        sniffer.communicate(timeout=15)
        sniffer.kill()

    def parse_access_point_scan(self, output):
        all_visible = dict()
        arr = output.split('\n')
        MAC = ''
        SSID = ''
        for line in arr:
            if MAC == '' and 'Address: ' in line:
                MAC = line.split('Address: ')[1]
            elif MAC != '' and 'ESSID:' in line:
                SSID = line.split('"')[1]
                all_visible[MAC] = SSID
                MAC = ''
                SSID = ''

        return all_visible

    def execute(self):
        config = self.data_interface.get_hound_mode()

        if config['Mode'] == 'AP':
            self.scan_access_points()
            return self.scan_users(config['Args'])
        elif config['Mode'] == 'MAC':
            self.scan_access_points()
            return self.scan_user(config['Args'])

        return self.scan_access_points()



