import tweepy
import os
import pandas as pd
from background_services.config import *
import time
from tqdm import tqdm
from django.db import transaction
from django.conf import settings
from django.utils.timezone import make_aware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMI_Service.settings")
import django
django.setup()
from socialmediauser.models import SocialMediaUser
from socialmediapost.models import SocialMediaPost, Hashtag
from webarticles.models import Url

auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=60)


# Creates or updates users from the provided ids. Adds the influencer to the list of follows for each record.
def update_create_user_data_from_ids_of_followers(id_list, influencer):
    users_return = []

    # If no ids exit
    if len(id_list) <= 0:
        return users_return

    # First check to see if the ids are already in the database
    # Try and add a way to update all users at once!
    ids_to_get = []
    users = SocialMediaUser.objects.filter(twitter_user_id__in=id_list)
    with transaction.atomic():
        for user in tqdm(users, total=len(users)):
            user.twitter_follows.add(influencer)
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
# Helper function when creating influcers from the excel files
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


# Updates the twitter followers and follows for the provided user key
def update_twitter_followers_single(is_initial, pk):
    elapsed_time = 60
    # Save the ids to the user
    user = SocialMediaUser.objects.get(pk=pk)
    if user is None:
        return

    # First see how many followers the user has already
    followers = user.get_follower_count()

    # Now determine what page to start on based on 5000 limit
    page = int(followers / 5000)

    # Get the follower ids
    try:
        while True:
            # Pause as needed for rate limiting
            if elapsed_time < 60:
                time.sleep(60 - elapsed_time)

            follower_ids = api.followers_ids(page=page, user_id=user.twitter_user_id)

            # Start timer
            time_start = time.time()

            if follower_ids:
                # Now get the user info for all the followers
                new_followers = update_create_user_data_from_ids_of_followers(follower_ids, user)

                # Update users followers
                user.twitter_followers.add(*new_followers)
            else:
                break

            page += 1

            elapsed_time = time.time() - time_start

    except tweepy.error.RateLimitError as e:
        print(e, ' pk: ', pk)


# Updates the users twitter followers and follows for a list of records
def update_twitter_followers_multi(pks):
    pass


# Updates the followers and follows for all records
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


# Main entry to determine which twitter update function to run
def update_twitter_followers(is_initial, pk=-1):
    if isinstance(pk, list):
        update_twitter_followers_multi(pk)
        return

    if pk == -1:  # all
        update_twitter_followers_all(is_initial)
    else:
        update_twitter_followers_single(is_initial, pk)


# Updates the twitter users follows field
# Not being used currently
def update_twitter_following():
    pass


# creates a new user from the provided user object from tweepy
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


# Creates a new twitter user record in db based on the twitter id
# Goes to twitter api and gets the info
def create_user_from_twitter_id(twitter_id):
    # Get the user object from twitter
    try:
        twitter_user = api.get_user(user_id=twitter_id)
        return create_user_from_twitter_user(twitter_user)
    except Exception as e:
        print(e)
        return None


# Main entry into getting previous tweets for all or single user
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


# Get the past tweets from the provided user key. Used to pre-populate the db
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


# Processes the re tweet and stores in db
def process_restatus(status, user):
    # Find the original message
    try:
        post = SocialMediaPost.objects.get(post_id=status.retweeted_status.id)
        post.reposted_by.add(user)
    except Exception as e:
        # See if the original author is in the db
        if SocialMediaUser.objects.filter(twitter_user_id=status.retweeted_status.author.id).exists():
            original_user = SocialMediaUser.objects.get(twitter_user_id=status.retweeted_status.author.id)
            new_post = process_status(status.retweeted_status, original_user)
            new_post.reposted_by.add(user)
        else:
            # Need to crete the new user
            new_user = create_user_from_twitter_user(status.retweeted_status.author)
            new_post = process_status(status.retweeted_status, new_user)
            new_post.reposted_by.add(user)


# Process the twitter status and saves to db
def process_status(status, user):
    # First check to see if post is already in db
    if SocialMediaPost.objects.filter(post_id=status.id).exists():
        return

    # Datetime
    settings.TIME_ZONE  # 'UTC'

    # Created At
    created_at = make_aware(status.created_at)

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

    # Hashtags
    for tag in status.entities['hashtags']:
        # See if the tag exists
        try:
            tag_obj = Hashtag.objects.get(text=tag['text'])
        except:
            # Create new user
            tag_obj = Hashtag(text=tag['text'])
            tag_obj.save()
        tag_obj.posts.add(post)

    # Urls
    for url in status.entities['urls']:
        try:
            url_obj = Url.objects.get(expanded=url['expanded_url'])
        except:
            # Create new user
            url_obj = Url(raw=url['url'], expanded=url['expanded_url'])
            url_obj.save()
        url_obj.posts.add(post)

    return post



