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

    def run_aircrack_scan(self, ssid=None):
        try:
            os.remove('/home/source/scans/scan-01.csv')
        except OSError:
            pass
        self.start_monitor_mode()
        if ssid is not None:
            self.sniff_ssid(ssid)
        else:
            self.sniff_all()
        self.stop_monitor_mode()
        self.refresh_hotspot_connection()

    def parse_scan_data(self):
        scan_file = open('/home/source/scans/scan-01.csv')
        raw_data = scan_file.readlines()
        scan_file.close()
        scan_data = dict()
        scan_data['APs'] = dict()
        scan_data['Devices'] = []

        in_basestations = True
        for line in raw_data:
            content = line.split(', ')
            if content[0] == 'BSSID':
                continue
            elif content[0] == 'Station MAC':
                in_basestations = False
                continue
            if in_basestations:
                scan_data['APs'][content[0]] = content[13]
            else:
                scan_data['Devices'].append(content[0])

        return scan_data

    def scan_users(self, ssid):
        self.run_aircrack_scan(ssid)
        scan_data = self.parse_scan_data()
        return self.data_interface.update_mac_addresses(scan_data['Devices'])

    def scan_user(self, mac):
        self.run_aircrack_scan()
        scan_data = self.parse_scan_data()
        all_messages = self.data_interface.update_mac_addresses(scan_data['Devices'])
        reportable_messages = []

        for message in all_messages:
            if mac in message:
                reportable_messages.append(message)

        return reportable_messages

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

    def sniff_all(self):
        command = 'airodump-ng mon0 --write /home/source/scans/hound_scan --output-format csv'
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



