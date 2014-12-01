import time
from datetime import datetime
from datetime import timedelta
from Sniffer import Sniffer
from DataInterface import DataInterface
from TwitterInterface import TwitterInterface

SLEEP_INTERVAL = 30


class HoundDaemon():

    def __init__(self, *args, **kwargs):
        self.data_interface = DataInterface()
        self.twitter_interface = TwitterInterface(self.data_interface)
        self.sniffer = Sniffer(self.data_interface)

    def parse_and_execute_command(self, last_mention):
        command = last_mention['text']
        if command[0] == 'SET_MODE':
            current_config = self.data_interface.get_hound_mode()
            try:
                if command[1] == 'SCAN':
                    if current_config['Mode'] == 'SCAN':
                        return
                    else:
                        self.data_interface.set_hound_mode(command[1])
                        self.twitter_interface.post('Mode Successfully Set: SCAN')
                        return
                elif command[1] == current_config['Mode'] and command[2] == current_config['Args']:
                    print 'No Change In New Command'
                    return
                else:
                    self.data_interface.set_hound_mode(command[1], command[2])
                    self.twitter_interface.post('Mode Successfully Set: {0}, {1}'.format(command[1], command[2]))
            except Exception:
                print 'Duplicate Twitter Status'
        elif command[0] == 'REFRESH':
            if last_mention['created_at'] > datetime.utcnow() - timedelta(0,SLEEP_INTERVAL):
                current_config = self.data_interface.get_hound_mode()
                try:
                    if current_config['Mode'] == 'SCAN':
                        self.data_interface.refresh_scan()
                        self.twitter_interface.post('SCAN Refresh Complete')
                    elif current_config['Mode'] == 'AP':
                        self.data_interface.refresh_ap()
                        self.twitter_interface.post('AP Refresh Complete')
                    else:
                        self.data_interface.refresh_scan()
                        self.twitter_interface.post('MAC Refresh Complete')
                except Exception:
                    print 'Duplicate Twitter Status'

    def mention_is_new(self, last_mention):
        current_config = self.data_interface.get_hound_mode()
        if last_mention['created_at'] > current_config['Set Time']:
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

if __name__ == '__main__':
    test_daemon = HoundDaemon()
    test_deamon.run()