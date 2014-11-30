import sqlite3
from datetime import datetime

DEFAULT_MODE = 'SCAN'
DEFAULT_ARGS = ''
SUPPORTED_MODES = ['SCAN', 'AP', 'MAC']


class DataInterface:

    def __init__(self):
        #Linux: /home/source/db/hound.db
        self.db = sqlite3.connect('V:/CircleS7en/Downloads/hound.db')
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
            ])
        else:
            return dict([
                ('Mode', DEFAULT_MODE),
                ('Args', DEFAULT_ARGS),
            ])

    def set_hound_mode(self, new_mode, new_args):
        current_datetime = datetime.now()
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

    def update_access_points(self, scan):
        insert_command = "INSERT INTO access_points VALUES(?,?,?)"
        update_command = "UPDATE access_points SET LastSeen = ? WHERE Mac = ?"
        current_datetime = datetime.now()
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

    def disconnect(self):
        self.db.close()


