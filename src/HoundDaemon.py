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

    def run(self):
        self.twitter_interface.read_commands()

