# coding: utf-8

"""
Script to enable compiling of Billboard Hot 100 data from Spotify and Wikipedia 
into a single data set, using outputs from 'Spotify_API.py' and 
'Wikipedia_scraping.py' scripts. Song titles and artists are matched using
fuzzywuzzy library.

Written in Python 2.7.

Author: Mark Bannister (mspbannister@gmail.com)
"""

import pandas as pd
from fuzzywuzzy import fuzz

# Import data
spotify_df = pd.read_csv('billboard_analysis.csv')
wiki_df = pd.read_csv('billboard_wiki.csv')

# Create mapping of known artist inconsistencies in Spotify data
artist_mapping = {"Kidz Bop Kids": "Taylor Swift",
                 "The Karaoke Channel": "Marky Mark and the Funky Bunch",
                 "Various Artists": "Rick Dees",
                 "Roq Star Karaoke": "The Young Rascals",
                 "Mega Tracks Karaoke Band": "Johnny Rivers",
                 "ProSource Karaoke": "Maureen McGovern",
                 "Done Again": "Bob Segar"}

def clean_artists(name):
    """Clean artist values based on mapping.
    Args: name (str): raw artist value
    Rtns: name (str): cleaned artist value
    """
    if name in artist_mapping:
        name = artist_mapping[name]
    return name

# Clean artist values
spotify_df['artist_1'] = spotify_df['artist_1'].apply(clean_artists)

# Create mapping of known title inconsistencies in Spotify data
title_mapping = {'Billy Don\xe2\x80\x99t Be A Hero': 
                    ['"Billy Don\'t Be A Hero"', 
                     "Bo Donaldson and The Heywoods"]}

# Match Spotify titles with Wikipedia titles
title_res, artist_res = [], []
for s in spotify_df.itertuples():
    max_score = 0
    title = s[1]
    artist = s[2]
    if title in title_mapping:
        artist = title_mapping[title][1]
        title = title_mapping[title][0]
    test = [s[1],s[2]]
    for w in wiki_df.itertuples():
        score_title = fuzz.partial_ratio(str(title).lower(), 
                                         str(w[1]).lower())
        score_artist = fuzz.partial_ratio(str(artist).lower(), 
                                          str(w[2]).lower())
        score = score_title + score_artist
        if score > max_score:
            title_match = w[1]
            artist_match = w[2]
            max_score = score
    title_res.append(title_match)
    artist_res.append(artist_match)

# Add match keys to Spotify data
title_res_df = pd.Series(title_res, name="match_title")
artist_res_df = pd.Series(artist_res, name="match_artist")
master_df = pd.concat([spotify_df,title_res_df], axis=1)
master_df = pd.concat([master_df,artist_res_df], axis=1)

# Merge datasets on match keys
merged_master = pd.merge(master_df, wiki_df, 
                         left_on=['match_title', 'match_artist'], 
                         right_on=['title', 'artists'], how="left")

# Clean titles
cleaned_titles = []
for i in range(0,len(merged_master)):
    if len(merged_master['title_x'][i]) < len(merged_master['title_y'][i]):
        cleaned_titles.append(merged_master['title_x'][i])
    else:
        cleaned_titles.append(merged_master['title_y'][i])
cleaned_titles = pd.Series(cleaned_titles, name="title")        
merged_master = pd.concat([merged_master,cleaned_titles], axis=1)

# Map key names and modality
key_mapping = {0: 'C', 1: 'C♯/Db', 2: 'D', 3: 'D♯/Eb', 4: 'E', 
               5: 'F', 6: 'F♯/Gb', 7: 'G', 8: 'G♯/Ab', 9: 'A',
               10: 'A♯/Bb', 11: 'B'}
merged_master['key'] = merged_master['key'].map(key_mapping)
merged_master['mode'] = merged_master['mode'].map({0: 'Minor', 1: 'Major'})

# Export to csv
header = ['title', 'artist_1', 'artist_2', 'artist_3', 'artist_4',
          'num_artists', 'entry_1', 'entry_2', 'entry_3', 'weeks_1', 
          'weeks_2', 'weeks_3', 'acousticness', 'danceability', 
          'duration_ms', 'energy', 'explicit', 'instrumentalness', 
          'key', 'liveness', 'loudness', 'mode', 'speechiness', 
          'tempo', 'time_signature','valence', 'analysis_url', 
          'track_href', 'id', 'uri']
merged_master.to_csv('billboard_data.csv', columns=header, index=False, 
                     encoding="utf-8")