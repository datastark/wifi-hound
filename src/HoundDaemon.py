import time
import datetime
from Daemon import Daemon
from Sniffer import Sniffer
from DataInterface import DataInterface
from TwitterInterface import TwitterInterface


class HoundDaemon(Daemon):

    def __init__(self, *args, **kwargs):
        super(HoundDaemon, self).__init__(*args, **kwargs)
        self.data_interface = DataInterface()
        self.twitter_interface = TwitterInterface(self.data_interface)
        self.sniffer = Sniffer(self.data_interface)

    def parse_and_execute_command(self, last_mention):
        command = last_mention['text']
        if command[0] == 'SET_MODE':
            current_config = self.data_interface.get_hound_mode()
            if command[1] == current_config['Mode'] and command[2] == current_config['Args']:
                return
            else:
                self.data_interface.set_hound_mode(command[1], command[2])
                self.twitter_interface.post('Mode Successfully Set: {0}, {1}'.format(command[1], command[2]))
        elif command[0] == 'REFRESH':
            current_config = self.data_interface.get_hound_mode()
            if current_config['Mode'] == 'SCAN':
                self.data_interface.refresh_scan()
                self.twitter_interface.post('SCAN Refresh Complete')
            elif current_config['Mode'] == 'AP':
                self.data_interface.refresh_ap()
                self.twitter_interface.post('AP Refresh Complete')
            else:
                self.data_interface.refresh_scan()
                self.twitter_interface.post('MAC Refresh Complete')

    def mention_is_new(self, last_mention):
        mention_time = datetime.datetime.strptime(last_mention['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        current_config = self.data_interface.get_hound_mode()
        if mention_time > datetime.datetime.strptime(current_config['Set Time'], '%Y-%m-%d %H:%M:%S.%f'):
            return True
        else:
            return False

    def run(self):
        while True:
            last_mention = self.twitter_interface.get_last_mention()
            if self.mention_is_new(last_mention):
                self.parse_and_execute_command(last_mention)
            results = self.sniffer.execute()
            if len(results):
                self.twitter_interface.post_many(results)

            time.sleep(300)
