import time
import shlex
import datetime
from twython import Twython


class TwitterInterface:
    def __init__(self, data_interface):
        self.data_interface = data_interface
        self.twitter_name = 'iit_cs549_p'
        self.twitter = self.connect_to_twitter()

    def connect_to_twitter(self):
        tokens = self.data_interface.get_twitter_credentials(self.twitter_name)
        return Twython(tokens['consumer_key'], tokens['consumer_secret'],
                       tokens['access_token_key'], tokens['access_token_secret'])

    def post(self, full_message):
        # Split the message if it's more than 140 characters
        all_messages = [full_message[i:i+140] for i in range(0, len(full_message), 140)]

        for message in all_messages:
            self.twitter.update_status(status=message)

    def post_many(self, messages):
        for message in messages:
            self.post(message)
            time.sleep(1)

    def get_last_mention(self):
        mentions = self.twitter.get_mentions_timeline()
        last_mention = dict()
        mention_text = mentions[0]['text']
        split_mention = shlex.split(mention_text)
        last_mention['text'] = split_mention[1:]
        last_mention['created_at'] = datetime.datetime.strptime(mentions[0]['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        return last_mention