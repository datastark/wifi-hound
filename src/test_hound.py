import time
from Sniffer import Sniffer
from DataInterface import DataInterface
from TwitterInterface import TwitterInterface


class Hound:
    def __init__(self):
        self.twitter_username = 'iit_cs549_p'
        print 'Initializing Database...'
        self.data_interface = DataInterface()
        print 'Initializing Twitter...'
        self.twitter_interface = TwitterInterface(self.data_interface)
        print 'Initializing Wifi Sniffer...'
        self.sniffer = Sniffer(self.data_interface)

    def parse_and_execute_command(self, last_mention):
        if last_mention[0] == 'SET_MODE':
            current_config = self.data_interface.get_hound_mode()
            if last_mention[1] == current_config['Mode'] and last_mention[2] == current_config['Args']:
                return
            else:
                self.data_interface.set_hound_mode(last_mention[1], last_mention[2])
                if last_mention[1] == 'SCAN':
                    message = 'Mode Set: SCAN'
                else:
                    message = "Mode Set: {0}, '{1}'".format(last_mention[1], last_mention[2])
                print message
                #self.twitter_interface.post(message)

    def execute(self):
        last_mention = self.twitter_interface.get_last_mention()
        self.parse_and_execute_command(last_mention)
        results = self.sniffer.execute()
        if results != '':
            self.twitter_interface.post(results)

    def execute_post(self):
        print 'Sending a Test Post...'
        self.twitter_interface.post("@iit_cs549_p SET_MODE AP 'Test Post'")
        print 'Test Post Complete!'

    def get_twitter_credentials(self):
        tokens = self.data_interface.get_twitter_credentials(self.twitter_username)
        print '\tUsername: ' + self.twitter_username
        print '\tConsumer Key: ' + tokens['consumer_key']
        print '\tConsumer Secret: ' + tokens['consumer_secret']
        print '\tAccess Key: ' + tokens['access_token_key']
        print '\tAccess Secret: ' + tokens['access_token_secret']

    def get_last_mention(self):
        print 'Getting Last Mention...'
        mention = self.twitter_interface.get_last_mention()
        print '\tLast Mention: {0} {1} {2}'.format(mention[0], mention[1], mention[2])
        return mention

    def get_mode(self):
        print 'Getting Mode Info...'
        mode_info = self.data_interface.get_hound_mode()
        print '\tCurrent Mode: ' + mode_info['Mode']
        print '\tMode Arguments: ' + mode_info['Args']

    def set_mode(self):
        print 'Setting Mode Info...'
        self.data_interface.set_hound_mode('SCAN', '')

    def teardown(self):
        self.data_interface.disconnect()

    def record_access_points(self):
        print 'Recording Access Points...'
        found_points = dict([
            ('52:57:1A:02:9D:F0', 'Test Point 1'),
            ('50:60:B1:21:D6:D9', 'Test Point 2'),
        ])
        self.data_interface.update_access_points(found_points)

if __name__ == '__main__':
    print 'Initializing...'
    test = Hound()
    test.record_access_points()
    test.teardown()
    print 'Test Complete!'