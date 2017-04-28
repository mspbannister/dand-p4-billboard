# coding: utf-8

"""
Script to enable collection of Spotify track information using spotipy
library, which is exported as a csv file.

Relevant help pages:
https://github.com/plamere/spotipy
https://developer.spotify.com/web-api/get-several-tracks/
https://developer.spotify.com/web-api/get-several-audio-features/

Requires Spotify developer access token 
(https://developer.spotify.com/web-api/authorization-guide/)

Written in Python 2.7.

Author: Mark Bannister (mspbannister@gmail.com)
"""

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import unicodecsv

user = 'user_here'
playlist_uri = 'playlist_uri_here'
client_id = 'client_id_here'
client_secret = 'client_secret_here'
redirect_uri = 'http://localhost:8888/callback'

# Create credentials manager and Spotify instances
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, 
                                                      client_secret=client_secret)
sp = Spotify(client_credentials_manager=client_credentials_manager)

# Get track information for chosen playlist (limited to 100 tracks per API call)
output = []
for offset in range(0,1100,100):
    playlist = sp.user_playlist_tracks(user, playlist_uri, limit=100, offset=offset)
    output += playlist['items']

# Create output dictionary with track information, including audio features
res = []
for item in output:
    row = {'artists':[]}
    for artist in item['track']['artists']:
        row['artists'].append(artist['name'])
    row['title'] = item['track']['name']
    row['explicit'] = item['track']['explicit']
    analysis = sp.audio_features([item['track']['uri']])[0]
    for key, value in analysis.items():
        row[key] = value
    res.append(row)

# Parse artist list into separate fields, clean titles
res_cleaned = []
for track in res:
    row = {}
    for key,value in track.items():
        if key == 'artists':
            row['num_artists'] = len(value)
            for i in range(0,len(value)):
                row['artist_{0}'.format(i+1)] = value[i]
        elif key == 'title':
            title = value
            if " - " in title:
                title = title[:title.find(" - ")]
            row['title'] = '"'+title+'"'
        else:
            row[key] = value
    res_cleaned.append(row)

# Prepare fields for csv export. 
# Note number of artist fields required will depend on chosen tracks/playlist
csv_fields = ['title', 'artist_1', 'artist_2', 'artist_3', 'artist_4', 'num_artists',
              'acousticness', 'danceability', 'duration_ms', 'energy',
              'explicit', 'instrumentalness', 'key', 'liveness', 'loudness',
              'mode', 'speechiness', 'tempo', 'time_signature',
              'valence', 'type', 'analysis_url', 'track_href', 'id', 'uri']

# Export csv
with open('billboard_analysis.csv', 'wb') as f:
    writer = unicodecsv.DictWriter(f, csv_fields)
    writer.writeheader()
    writer.writerows(res_cleaned)