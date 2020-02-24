import tweepy
import os
import pandas as pd
from background_services.config import *
import time
from tqdm import tqdm

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

auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=60)


# Creates or updates users from the provided ids
def update_create_user_data_from_ids_of_followers(id_list, influencer):
    users_return = []

    # If no ids exit
    if len(id_list) <= 0:
        return users_return

    # First check to see if the ids are already in the database
    ids_to_get = []
    users = SocialMediaUser.objects.filter(twitter_user_id__in=id_list)
    for user in tqdm(users, total=len(users)):
        user.twitter_follows.add(influencer)
        user.save()
        users_return.append(user)

    # Get the ids not in the database
    if len(users) <= 0:
        ids_to_get = id_list
    else:
        users_df = pd.DataFrame.from_records(users.values())
        user_ids = users_df['twitter_user_id'].to_list()
        ids_to_get = [x for x in id_list if x not in user_ids]

    if len(ids_to_get) <= 0:
        return users_return

    iterations = int(len(ids_to_get) / 100)

    elapsed_time = 3
    for i in range(iterations + 1):
        if elapsed_time < 3:
            time.sleep(3 - elapsed_time)

        time_start = time.time()

        if len(ids_to_get) > i * 100 + 100:
            ids = ids_to_get[(i * 100):(i * 100 + 100)]
        elif len(ids_to_get) == 1:
            ids = ids_to_get
        else:
            ids = ids_to_get[(i * 100):-1]

        if len(ids) <= 0:
            return users_return

        try:
            twitter_users = api.lookup_users(user_ids=ids)
            for y in tqdm(range(len(twitter_users)), total=len(twitter_users)):
                tmp_follower = create_user_from_twitter_user(twitter_users[y])
                tmp_follower.twitter_follows.add(influencer)
                users_return.append(tmp_follower)
        except Exception as e:
            print(e, 'pk: ', influencer.pk)

        elapsed_time = time.time() - time_start

    return users_return


# Get the twitter ids from twitter
def get_missing_twitter_ids():
    try:
        influencer_records = SocialMediaUser.objects.filter(twitter_user_id__isnull=True, is_influencer=True).values()
        df = pd.DataFrame.from_records(influencer_records)
        influencers = df[df['twitter_user_id'].isnull()]['twitter_screen_name'].tolist()

        if len(influencers) <= 0:
            return

        iterations = int(len(influencers) / 100)

        elapsed_time = 3
        for i in range(iterations + 1):
            if elapsed_time < 3:
                time.sleep(3 - elapsed_time)

            time_start = time.time()

            if len(influencers) >= i * 100 + 100:
                names = influencers[(i * 100):(i * 100 + 100)]
            elif len(influencers) == 1:
                names = influencers
            else:
                names = influencers[(i * 100):-1]

            users = api.lookup_users(screen_names=names)
            for y in tqdm(range(len(users)), total=len(users)):
                db_user = SocialMediaUser.objects.get(twitter_screen_name__iexact=users[y].screen_name)
                if db_user:
                    db_user.twitter_user_id = users[y].id
                    if users[y].location != '':
                        db_user.location = users[y].location
                    db_user.twitter_posts = users[y].statuses_count
                    db_user.save()

            elapsed_time = time.time() - time_start
    except Exception as e:
        print(e)


def update_twitter_followers_single(is_initial, pk):
    elapsed_time = 60
    # Save the ids to the user
    user = SocialMediaUser.objects.get(pk=pk)
    if user is None:
        return

    # Get the follower ids
    try:
        for follower_ids in tweepy.Cursor(api.followers_ids, user_id=user.twitter_user_id).pages():

            # Pause as needed for rate limiting
            if elapsed_time < 60:
                time.sleep(60 - elapsed_time)

            # Start timer
            time_start = time.time()

            # Now get the user info for all the followers
            new_followers = update_create_user_data_from_ids_of_followers(follower_ids, user)

            # Update users followers
            user.twitter_followers.add(*new_followers)
            user.save()

            elapsed_time = time.time() - time_start

    except tweepy.error.RateLimitError as e:
        print(e, ' pk: ', pk)


def update_twitter_followers_multi(pks):
    pass


def update_twitter_followers_all(is_initial=False):
    influencer_records = SocialMediaUser.objects.filter(twitter_user_id__isnull=False, is_influencer=True,
                                                        twitter_followers=[]).values()
    df = pd.DataFrame.from_records(influencer_records)
    influencers = df[df['twitter_user_id'].notnull()]['twitter_user_id'].tolist()

    if len(influencers) <= 0:
        return

    elapsed_time = 60
    for influencer_id in influencers:

        # Save the ids to the user
        user = SocialMediaUser.objects.get(twitter_user_id__exact=influencer_id)
        if user is None:
            continue

        # Get the follower ids
        try:
            for follower_ids in tweepy.Cursor(api.followers_ids, user_id=influencer_id).pages():

                # Pause as needed for rate limiting
                if elapsed_time < 60:
                    time.sleep(60 - elapsed_time)

                # Start timer
                time_start = time.time()

                new_followers = [x for x in follower_ids if x not in user.twitter_followers]

                # Now get the user info for all the followers
                if is_initial:
                    update_create_user_data_from_ids_of_followers(new_followers, influencer_id)

                # Update users followers
                user.twitter_followers += new_followers
                user.save()

                elapsed_time = time.time() - time_start

        except tweepy.error.RateLimitError as e:
            print(e)


def update_twitter_followers(is_initial, pk=-1):
    if isinstance(pk, list):
        update_twitter_followers_multi(pk)
        return

    if pk == -1:  # all
        update_twitter_followers_all(is_initial)
    else:
        update_twitter_followers_single(is_initial, pk)


def update_twitter_following():
    pass


def get_past_tweets(pk):
    if isinstance(pk, list):
        update_twitter_followers_multi(pk)
        return

    if pk == -1:  # all
        start = 0
        for i in range(start, SocialMediaUser.objects.filter(is_influencer=True).count()):
            get_past_tweets_for_user(i)
    else:
        get_past_tweets_for_user(pk)


def get_past_tweets_for_user(pk):
    # Get the user to get tweets for
    user = SocialMediaUser.objects.get(pk=pk)

    print('Getting tweets for: ', user.twitter_screen_name)

    elapsed_time = 1
    for page in tweepy.Cursor(api.user_timeline, user_id=user.twitter_user_id, tweet_mode='extended').pages():

        # Pause as needed for rate limiting
        if elapsed_time < 0.6:
            time.sleep(0.6 - elapsed_time)

        # Start timer
        time_start = time.time()

        for status in tqdm(page, total=len(page)):
            # process status here
            # Check to see if re post
            if hasattr(status, 'retweeted_status'):
                process_restatus(status, user)
            else:
                process_status(status, user)

        elapsed_time = time.time() - time_start


def process_restatus(status, user):
    # Find the original message
    try:
        post = SocialMediaPost.objects.get(post_id=status.retweeted_status.id)
        post.reposted_by.add(user)
        post.save()
    except Exception as e:
        # See if the original author is in the db
        if SocialMediaUser.objects.filter(twitter_user_id=status.retweeted_status.author.id).exists():
            original_user = SocialMediaUser.objects.get(twitter_user_id=status.retweeted_status.author.id)
            new_post = process_status(status.retweeted_status, original_user)
            new_post.reposted_by.add(user)
            new_post.save()
        else:
            # Need to crete the new user
            new_user = create_user_from_twitter_user(status.retweeted_status.author)
            new_post = process_status(status.retweeted_status, new_user)
            new_post.reposted_by.add(user)
            new_post.save()


def create_user_from_twitter_id(twitter_id):
    # Get the user object from twitter
    try:
        twitter_user = api.get_user(user_id=twitter_id)
    except Exception as e:
        print(e)
        return None
    return create_user_from_twitter_user(twitter_user)


def process_status(status, user):
    # First check to see if post is already in db
    if SocialMediaPost.objects.filter(post_id=status.id).exists():
        return

    # Datetime
    settings.TIME_ZONE  # 'UTC'

    # Created At
    created_at = make_aware(status.created_at)

    # Hashtags
    hashtags = []
    for tag in status.entities['hashtags']:
        hashtags.append(tag['text'])

    # Post ID
    post_id = status.id

    # Reply to user id
    in_reply_to_user_id = status.in_reply_to_user_id

    # Reply to post id
    in_reply_to_post_id = status.in_reply_to_status_id

    # Lang
    lang = status.lang

    # Reply Count
    if hasattr(status, 'reply_count'):
        reply_count = status.reply_count
    else:
        reply_count = 0

    # Text
    text = status.full_text

    post = SocialMediaPost(
        author=user,
        created_at=created_at,
        hashtags=hashtags,
        post_id=post_id,
        in_reply_to_user_id=in_reply_to_user_id,
        in_reply_to_post_id=in_reply_to_post_id,
        lang=lang,
        reply_count=reply_count,
        text=text,
        service='Twitter'
    )

    post.save()

    # User Mentions
    elapsed_time = 1
    for mention in status.entities['user_mentions']:

        # Pause as needed for rate limiting
        if elapsed_time < 1:
            time.sleep(1 - elapsed_time)

        # Start timer
        time_start = time.time()

        # Check if user exists
        try:
            user_mention = SocialMediaUser.objects.get(twitter_user_id=mention['id'])
        except:
            # Create new user
            user_mention = create_user_from_twitter_id(mention['id'])

        if user_mention:
            post.user_mentions.add(user_mention)

        elapsed_time = time.time() - time_start

    return post


def create_user_from_twitter_user(user):
    new_user = SocialMediaUser(name=user.name,
                               twitter_user_id=user.id,
                               twitter_screen_name=user.screen_name,
                               location=user.location,
                               is_influencer=False,
                               twitter_posts_count=user.statuses_count
                               )
    new_user.save()
    return new_user
