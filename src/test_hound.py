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
                print 'Mode Successfully Set: {0}, {1}'.format(command[1], command[2])
        elif command[0] == 'REFRESH':
            if last_mention['created_at'] > datetime.utcnow() - timedelta(0,SLEEP_INTERVAL):
                current_config = self.data_interface.get_hound_mode()
                message = '{0} Refresh Complete'.format(current_config['Mode'])
                try:
                    if current_config['Mode'] == 'SCAN':
                        self.data_interface.refresh_scan()
                    elif current_config['Mode'] == 'AP':
                        self.data_interface.refresh_ap()
                    else:
                        self.data_interface.refresh_scan()
                    self.twitter_interface.post(message)
                except Exception:
                    print 'Duplicate Twitter Status'
                    print message
            else:
               print 'REFRESH Command Stale, Skipping Refresh...'

    def mention_is_new(self, last_mention):
        current_config = self.data_interface.get_hound_mode()
        if last_mention['created_at'] > current_config['Set Time']:
            return True
        else:
            return False

    def run(self):
        loop_count = 1
        while True:
            print 'Starting Sequence {0}:'.format(loop_count)
            print 'Getting Last Mentions From Twitter...'
            last_mention = self.twitter_interface.get_last_mention()
            print 'Last Mention Received: {0}'.format(' '.join(last_mention['text']))
            if self.mention_is_new(last_mention):
                if last_mention['text'][0] != 'REFRESH':
                   print 'Executing Command...'
                self.parse_and_execute_command(last_mention)
            else:
               print 'Last Mention Stale, Not Executing...'
            print 'Running Sniffer...'
            results = self.sniffer.execute()
            if len(results):
                print 'Posting Sniffer Results...'
                self.twitter_interface.post_many(results)
            else:
                print 'No New Sniffer Results...'
            print 'Sleeping for {0} Seconds...'.format(SLEEP_INTERVAL)
            time.sleep(SLEEP_INTERVAL)
            print '\n\n'
            loop_count += 1

if __name__ == '__main__':
    test_daemon = HoundDaemon()
    test_daemon.run()
