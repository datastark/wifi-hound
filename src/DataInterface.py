import sqlite3
from datetime import datetime

DEFAULT_MODE = 'SCAN'
DEFAULT_ARGS = ''
DEFAULT_TIME = "2014-11-30 00:00:00.00000"
SUPPORTED_MODES = ['SCAN', 'AP', 'MAC']
#Linux: /home/source/db/hound.db
DB_LOCATION = '/home/source/db/hound.db'


class DataInterface:

    def __init__(self):
        self.db = sqlite3.connect(DB_LOCATION)
        self.cursor = self.db.cursor()

    def get_twitter_credentials(self, username):
        statement = "SELECT * FROM twitter_credentials WHERE Owner='{0}'".format(username)
        self.cursor.execute(statement)
        credentials = self.cursor.fetchone()
        if len(credentials) == 5:
            return dict([
                ('access_token_key', credentials[1]),
                ('access_token_secret', credentials[2]),
                ('consumer_key', credentials[3]),
                ('consumer_secret', credentials[4])
            ])
        else:
            return dict()

    def get_hound_mode(self):
        statement = 'SELECT * FROM hound_config WHERE SetTime = (SELECT MAX(SetTime) FROM hound_config)'
        self.cursor.execute(statement)
        result = self.cursor.fetchone()
        if len(result) == 3:
            return dict([
                ('Mode', result[1]),
                ('Args', result[2]),
                ('Set Time', datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')),
            ])
        else:
            return dict([
                ('Mode', DEFAULT_MODE),
                ('Args', DEFAULT_ARGS),
                ('Set Time', datetime.strptime(DEFAULT_TIME, "%Y-%m-%d %H:%M:%S.%f"))
            ])

    def set_hound_mode(self, new_mode, new_args=''):
        current_datetime = datetime.utcnow()
        if new_mode not in SUPPORTED_MODES:
            return

        statement = "INSERT INTO hound_config VALUES(?,?,?)"
        self.cursor.execute(statement, [current_datetime, new_mode, new_args])
        self.db.commit()

    def get_all_access_points(self):
        statement = 'SELECT Mac FROM access_points'
        self.cursor.execute(statement)
        all_macs = []
        for row in self.cursor.fetchall():
            all_macs.append(row[0])
        return all_macs

    def get_mac_addresses_with_state(self, state):
        statement = "SELECT * FROM mac_addresses WHERE State = '{0}'".format(state)
        self.cursor.execute(statement)
        selected_macs = dict()
        for row in self.cursor.fetchall():
            selected_macs[row[0]] = dict([
                ('LastSeen', row[1]),
                ('State', row[2]),
                ('StateDelta', row[3]),
            ])
        return selected_macs

    def drop_table(self, table):
        statement = 'DROP TABLE {0}'.format(table)
        self.cursor.execute(statement)
        self.db.commit()

    def refresh_scan(self):
        self.drop_table('access_points')
        statement = 'CREATE TABLE access_points(Mac TEXT, Ssid TEXT, LastSeen DATETIME);'
        self.cursor.execute(statement)
        self.db.commit()

    def refresh_ap(self):
        self.refresh_scan()
        self.drop_table('mac_addresses')
        statement = 'CREATE TABLE mac_addresses(Mac TEXT, LastSeen DATETIME, StateDelta INT);'
        self.cursor.execute(statement)
        self.db.commit()

    def update_access_points(self, scan):
        insert_command = "INSERT INTO access_points VALUES(?,?,?)"
        update_command = "UPDATE access_points SET LastSeen = ? WHERE Mac = ?"
        current_datetime = datetime.utcnow()
        seen_access_points = self.get_all_access_points()
        messages = []

        for mac, ssid in scan.iteritems():
            if mac in seen_access_points:
                self.cursor.execute(update_command, [current_datetime, mac])
            else:
                self.cursor.execute(insert_command, [mac, ssid, current_datetime])
                messages.append("New AP: {0} - {1}".format(mac, ssid))

        self.db.commit()
        return messages

    def update_mac_addresses(self, scan):
        insert_command = 'INSERT INTO mac_addresses VALUES(?,?,?,?)'
        update_same_state = 'UPDATE mac_addresses SET LastSeen = ? WHERE Mac = ?'
        update_new_connect = 'UPDATE mac_addresses SET StateDelta = ?, LastSeen = ?, State = ? WHERE Mac = ?'
        update_new_disconnect = 'UPDATE mac_addresses SET StateDelta = ?, State = ? WHERE Mac = ?'
        current_datetime = datetime.utcnow()
        connected_mac_addresses = self.get_mac_addresses_with_state('CONNECTED')
        disconnected_mac_addresses = self.get_mac_addresses_with_state('DISCONNECTED')
        messages = []

        for mac in scan:
            if mac in connected_mac_addresses:
                self.cursor.execute(update_same_state, [current_datetime, mac])
            elif mac in disconnected_mac_addresses:
                self.cursor.execute(update_new_connect, [disconnected_mac_addresses[mac]['StateDelta']+1,
                                                         current_datetime, 'CONNECTED', mac])
                messages.append("Device Reconnected: {0}".format(mac))
            else:
                self.cursor.execute(insert_command, [mac, current_datetime, 'CONNECTED', 1])
                messages.append("New Device Detected: {0}".format(mac))

        for mac in connected_mac_addresses.iteritems():
            if mac not in scan:
                self.cursor.execute(update_new_disconnect, [connected_mac_addresses[mac]['StateDelta']+1,
                                                            'DISCONNECTED', mac])
                messages.append("Device Disconnected: {0}".format(mac))
        self.db.commit()
        return messages

    def disconnect(self):
        self.db.close()


