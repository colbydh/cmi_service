import datetime
import json

import tweepy
from tqdm import tqdm
import time
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMI_Service.settings")
import pandas as pd
from background_services.config import *
from background_services.twitter_services import get_missing_twitter_ids, update_twitter_followers, get_past_tweets
from background_services.location_finder import get_coords



# Django imports so you can delete and add your Databricks imports
from django.conf import settings
from django.utils.timezone import make_aware
# end Django imports


# More django imports needs to be lower than background services to not add redundancies
# Can also remove as needed since you will be using databricks

import django
from socialmediauser.models import SocialMediaUser

django.setup()



# End more django imports and setup


# Extract the twitter information for a single influencer
def process_twitter_influencer(row):
    if pd.notna(row['Twitter']):
        if row['Twitter'] != 'none identified':
            twitter_screen_name = row['Twitter']
        else:
            twitter_screen_name = None
    else:
        twitter_screen_name = None
    return_list = []
    if twitter_screen_name is not None:
        if twitter_screen_name == '':
            return None
        twitter_screen_name_list = []
        if ';' in twitter_screen_name:
            twitter_screen_name_list = twitter_screen_name.split(';')
        else:
            twitter_screen_name_list.append(twitter_screen_name)

        for name in twitter_screen_name_list:
            tmp_name = name.replace(' ', '')
            tmp_name = tmp_name.replace('https://twitter.com/', '')
            tmp_name = tmp_name.replace('http://twitter.com/', '')
            tmp_name = tmp_name.replace('https://www.twitter.com/', '')
            tmp_name = tmp_name.replace('http://www.twitter.com/', '')
            tmp_name = tmp_name.replace('?lang=en', '')
            tmp_name = tmp_name.replace('?lang=sv', '')
            tmp_name = tmp_name.replace('?lang=pl', '')
            tmp_name = tmp_name.replace('?lang=tr', '')
            tmp_name = tmp_name.replace('?s=08', '')
            tmp_name = tmp_name.replace('?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor', '')
            tmp_name = tmp_name.replace('www.twitter.com/', '')
            tmp_name = tmp_name.replace('twitter.com/', '')
            tmp_name = tmp_name.replace('/', '')
            tmp_name = tmp_name.replace('#!', '')
            return_list.append(tmp_name)

        return return_list
    else:
        return None


# Process a single influencer
def process_influence_row(row):
    twitter_screen_name = process_twitter_influencer(row)
    if twitter_screen_name:
        influencers = []
        for name in twitter_screen_name:
            tmp_influencer = dict(
                name=row['Organization'],
                twitter_screen_name=name,
                location=row['Country']
            )
            influencers.append(tmp_influencer)
        return influencers
    else:
        return None


# Process a single influencer excel file
def process_key_influencer_file(filepath):
    influencers = []
    new_influencers = []
    xl = pd.ExcelFile(filepath)

    # first sheet
    for sheet in xl.sheet_names:
        try:
            df = xl.parse(sheet)
            for y, row in df.iterrows():
                new_influencers = process_influence_row(row)
                if new_influencers:
                    influencers = influencers + new_influencers
        except Exception as e:
            print('Exception in process_key_influencer_file: ', e, ' File: ', filepath, ' Sheet: ', sheet,
                  ' Influencers: ', new_influencers)
            pass

    try:
        for influencer in influencers:
            get_influencer = SocialMediaUser.objects.filter(
                twitter_screen_name__iexact=influencer['twitter_screen_name']).exists()

            if not get_influencer:
                # create the model
                tmp_influencer = SocialMediaUser(name=influencer['name'],
                                                 twitter_screen_name=influencer['twitter_screen_name'],
                                                 location=influencer['location'],
                                                 is_influencer=True)
                tmp_influencer.save()

    except Exception as e:
        print('Exception in saving user in process_key_influencer_file: ', e, '. File: ', filepath)
        pass


# Loop through the excel files in data and parse the key influencers
def process_key_influencers_excel_files():
    directory = '../data'
    for filename in tqdm(os.listdir(directory), total=len(os.listdir(directory))):
        if filename.endswith(".xlsx"):
            process_key_influencer_file(os.path.join(directory, filename))
            continue
        else:
            continue

    print('Done!')


# Get the lat lon for users
def get_lat_lon_for_influencers():
    users = SocialMediaUser.objects.filter(location__isnull=False, lat__isnull=True, lon__isnull=True).count()

    # Loop through users
    elapsed_time = 30
    for i in tqdm(range(users), total=users):
        try:
            user = SocialMediaUser.objects.filter(location__isnull=False, lat__isnull=True, lon__isnull=True)[:1].get()
        except:
            return

        if user.lat and user.lon:
            continue

        # Get coords
        start = datetime.datetime.now()
        lat, lon = get_coords(user.location, elapsed_time)
        if lon == 'No Geocode':
            user.location = None
            user.save()
            continue
        else:
            user.lat = lat
            user.lon = lon
            user.save()

        # Now loop through users again to see if any match the location
        SocialMediaUser.objects.select_related().filter(location__icontains=user.location, lat__isnull=True,
                                                        lon__isnull=True).update(lat=lat, lon=lon)

        end = datetime.datetime.now()
        elapsed_time = (end - start).seconds


# Find the various graph depths for users
def get_graph_network():
    # Grab all users with followers
    pass


def temp_populate_db():
    with open('../db.json', encoding="utf8") as f:
        systems = json.load(f)

    for row in tqdm(systems, total=len(systems)):
        if row['model'] == 'common.socialmediauser':
            tmp_user = SocialMediaUser(
                name=row['fields']['name'],
                is_influencer=row['fields']['is_influencer'],
                twitter_screen_name=row['fields']['twitter_screen_name'],
                twitter_user_id=row['fields']['twitter_user_id'],
                facebook_screen_name=row['fields']['facebook_screen_name'],
                location=row['fields']['location'],
                lat=row['fields']['lat'],
                lon=row['fields']['lon'],
                twitter_follows=eval(row['fields']['twitter_follows']),
                twitter_followers=eval(row['fields']['twitter_followers']),
                twitter_posts_count=row['fields']['twitter_posts_count'],
            )
            tmp_user.save()


def temp_clear_followers_follows(pk):
    if pk == -1:
        users = SocialMediaUser.objects.all()
        for user in tqdm(users, total=len(users)):
            user.twitter_followers.clear()
            user.twitter_follows.clear()
            user.save()
    else:
        SocialMediaUser.objects.get(pk=pk).twitter_followers.clear()
        SocialMediaUser.objects.get(pk=pk).twitter_follows.clear()


# Start
if __name__ == '__main__':
    # Process the excell files
    # process_key_influencers_excel_files()

    # Now find the missing ids for twitter
    # get_missing_twitter_ids()

    # Update followers
    start = 2
    for i in range(start, SocialMediaUser.objects.filter(is_influencer=True).count()):
        #update_twitter_followers(is_initial=True, pk=i) # 123
        print('### Getting Tweets for User pk: ', i)
        get_past_tweets(i) # 8

    #get_past_tweets(2058)

    # get lat lons
    # get_lat_lon_for_influencers()

    # switch_to_many_to_many()

    # temp_clear_followers_follows(1)
