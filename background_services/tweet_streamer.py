# Simply twitter streaming api
import tweepy
import time
import os
from tqdm import tqdm
import pandas as pd
from background_services.config import *

# Django imports so you can delete and add your Databricks imports
from django.conf import settings
from django.utils.timezone import make_aware
# end Django imports

from background_services import location_finder
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from background_services.location_finder import get_coords_using_here, get_coords_using_opencage, \
    get_coords_using_locationiq

# More django imports needs to be lower than background services to not add redundancies
# Can also remove as needed since you will be using databricks
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMI_Service.settings")
import django
django.setup()
from common.models import SocialMediaUser, SocialMediaPost
from background_services.twitter_services import process_status, process_restatus, create_user_from_twitter_user
# End more django imports and setup


# Twitter keywords
KEYWORDS = ['trump', 'clinton', 'russia', 'ukraine', 'united states', 'usa']

# Twitter influencers
TWITTER_INFLUENCERS = []


# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        process_tweet(status)

    def on_error(self, status_code):
        print('Error in Twitter stream: ', status_code)
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False

    def on_exception(self, exception):
        start_streamer()
        return


def start_streamer():
    df = pd.DataFrame.from_records(SocialMediaUser.objects.filter(is_influencer=True).values())
    global TWITTER_INFLUENCERS
    TWITTER_INFLUENCERS = df[df['twitter_user_id'].notnull()]['twitter_user_id'].astype(int).astype(str).unique().tolist()
    stream_listener = MyStreamListener()
    auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
    auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(follow=TWITTER_INFLUENCERS, is_async=True)


def process_tweet(status):
    try:
        user = SocialMediaUser.objects.get(twitter_user_id=status.author.id)
    except:
        user = create_user_from_twitter_user(status.author)

    if hasattr(status, 'retweeted_status'):
        process_restatus(status, user)
    else:
        process_status(status, user)



def sentiment_analyzer_scores(sentence):
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(sentence)
    if score['compound'] >= 0.05:
        return 'Positive'
    elif score['compound'] > -0.05:
        return 'Neutral'
    else:
        return 'Negative'


def start_geocode_database():
    posts = SocialMediaPost.objects.filter(lat__isnull=True, location__isnull=False)

    print(len(posts))

    for post in tqdm(posts, total=len(posts)):
        lat, lon = location_finder.get_coords_using_locationiq(post.location)
        time.sleep(0.5)
        post.lat = lat
        post.lon = lon
        post.save()
        if lat is not None and lon is not None:
            similar_posts = SocialMediaPost.objects.filter(location__exact=post.location, lat__isnull=True)
            for post_two in similar_posts:
                post_two.lat = lat
                post_two.lon = lon
                post_two.save()


# Start
if __name__ == '__main__':
    start_streamer()
    #start_geocode_database()
