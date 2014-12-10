import os
import time
import subprocess


class Sniffer:

    def __init__(self, data_interface):
        self.data_interface = data_interface
        self.mode = self.data_interface.get_hound_mode()

    def scan_access_points(self):
        print '\tRunning Access Point Scan'
        command = 'iwlist wlan0 s'
        response = os.popen(command)
        print '\tParsing Scan Results...'
        result = response.read()
        response.close()

        formatted_results = self.parse_access_point_scan(result)
        return self.data_interface.update_access_points(formatted_results)

    def run_aircrack_scan(self, ssid=None):
        try:
            os.remove('/home/efaurie/Source/scans/hound_scan-01.csv')
        except OSError:
            pass
        self.start_monitor_mode()
        if ssid is not None:
            self.sniff_ssid(ssid)
        else:
            self.sniff_all()
        self.stop_monitor_mode()
        #self.refresh_hotspot_connection()

    def parse_scan_data(self):
        scan_file = open('/home/efaurie/Source/scans/hound_scan-01.csv')
        raw_data = scan_file.readlines()
        print '\t\t\tScan Log Contains {0} Lines...'.format(len(raw_data))
        scan_file.close()
        scan_data = dict()
        scan_data['APs'] = dict()
        scan_data['Devices'] = []

        in_basestations = True
        for line in raw_data:
            content = line.split(', ')
            if len(content) < 2:
                continue
            if content[0] == 'BSSID':
                continue
            elif content[0] == 'Station MAC':
                in_basestations = False
                continue
            if in_basestations:
                scan_data['APs'][content[0]] = content[13]
            else:
                scan_data['Devices'].append(content[0])
                print '\t\t\tConnected Device: {0}'.format(content[0])

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
        down = subprocess.Popen(['ifdown', 'wlan0'], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        down.communicate()
        up = subprocess.Popen(['ifup', 'wlan0'], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        up.communicate()

    def start_monitor_mode(self):
        print '\tPlacing wlan0 Into Monitor Mode'
        monitor = subprocess.Popen(['airmon-ng', 'start', 'wlan0'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        monitor.communicate()

    def stop_monitor_mode(self):
        print '\tRemoving mon0 (Monitor Interface)'
        monitor = subprocess.Popen(['airmon-ng', 'stop', 'mon0'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        monitor.communicate()

    def sniff_ssid(self, ssid):
        print '\tRunning aircrack Scan on SSID: {0}'.format(ssid)
        command = ['airodump-ng', 'mon0', '--bssid', ssid,
                   '--write', '/home/efaurie/Source/scans/hound_scan', '--output-format', 'csv']
        sniffer = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(15)
        sniffer.kill()
        print '\tScan Complete!'

    def sniff_all(self):
        print '\tRunning aircrack Scan'
        command = ['airodump-ng', 'mon0', '--write', '/home/efaurie/Source/scans/hound_scan', '--output-format', 'csv']
        sniffer = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(15)
        sniffer.kill()
        print '\tScan Complete!'

    def parse_access_point_scan(self, output):
        all_visible = dict()
        arr = output.split('\n')
        mac = ''
        ssid = ''
        for line in arr:
            if mac == '' and 'Address: ' in line:
                mac = line.split('Address: ')[1]
            elif mac != '' and 'ESSID:' in line:
                ssid = line.split('"')[1]
                all_visible[mac] = ssid
                if ssid == '':
                   ssid = 'Unbroadcasted'
                print '\t\tFound Access Point: {0}'.format(ssid)
                mac = ''
                ssid = ''

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



