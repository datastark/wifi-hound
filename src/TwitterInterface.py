import time
import shlex
import datetime
from twython import Twython

POST_THROTTLE = 1


class TwitterInterface:
    def __init__(self, data_interface):
        self.data_interface = data_interface
        self.twitter_name = 'iit_cs549_p'
        self.twitter = self.connect_to_twitter()

    def connect_to_twitter(self):
        credentials = self.data_interface.get_twitter_credentials(self.twitter_name)
        return Twython(credentials['consumer_key'], credentials['consumer_secret'],
                       credentials['access_token_key'], credentials['access_token_secret'])

    def post(self, full_message):
        # Split the message if it's more than 140 characters
        all_messages = [full_message[i:i+140] for i in range(0, len(full_message), 140)]

        for message in all_messages:
            self.twitter.update_status(status=message)

    def post_many(self, messages):
        for message in messages:
            self.post(message)
            time.sleep(POST_THROTTLE)

    def get_last_mention(self):
        latest_mention = self.twitter.get_mentions_timeline()[0]
        mention_text = latest_mention['text']
        split_mention = shlex.split(mention_text)

        last_mention = dict()
        last_mention['text'] = split_mention[1:]
        last_mention['created_at'] = datetime.datetime.strptime(latest_mention['created_at'],
                                                                '%a %b %d %H:%M:%S +0000 %Y')
        return last_mention