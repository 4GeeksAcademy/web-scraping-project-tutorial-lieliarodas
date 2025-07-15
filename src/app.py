import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io


URL = "https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify"
response = requests.get(URL)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

tables = io.StringIO(response.text)

df = pd.read_html(tables, header=0)[0]

df = df[df[df.columns[0]].astype(str).str.contains(r"^\d+(?:\.\d+)?$", na=False)].copy()

df['Streams (billions)'] = df['Streams (billions)'].astype(float)
df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')
df['Artist(s)'] = df['Artist(s)'].astype(str)
df['Song'] = df['Song'].astype(str)
df['Rank'] = df['Rank'].astype(float)


conn = sqlite3.connect('spotify_songs.db')
cursor = conn.cursor()

df.to_sql('most_streaming_songs', conn, if_exists='replace', index=False)

cursor.execute("SELECT COUNT(*) FROM most_streaming_songs")
print("Rows inserted:", cursor.fetchone()[0])

conn.commit()
conn.close()




top_10_songs = df.nlargest(10, 'Streams (billions)')

plt.figure(figsize=(12, 6))
plt.style.use('dark_background')
sns.barplot(x='Streams (billions)', hue='Song', data=top_10_songs, palette='Greens', legend=True)
plt.title('Top 10 Most Streamed Songs on Spotify')
plt.xlabel('Streams (billions)')
plt.ylabel('Song')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('top_10_streamed_songs.png')
plt.show()



top_5_streamed_artists = df.groupby('Artist(s)')['Streams (billions)'].sum().nlargest(5).reset_index()

plt.figure(figsize=(10, 5))
sns.barplot(x='Streams (billions)', y='Artist(s)', hue = 'Artist(s)', data=top_5_streamed_artists, palette='Greens', legend=False)
plt.title('Top 5 Most Streamed Artists on Spotify')
plt.xlabel('Total Streams (billions)')
plt.ylabel('Artist')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('top_5_streamed_artists.png')
plt.show()


top_10_songs_by_year = df.groupby('Year')['Streams (billions)'].sum().nlargest(10).reset_index()

plt.figure(figsize=(12, 6))
sns.barplot(x='Year', y='Streams (billions)', hue='Streams (billions)', data=top_10_songs_by_year, palette='Greens', legend=False)
plt.title('Top 10 Most Streamed Songs by Year')
plt.xlabel('Year')
plt.ylabel('Total Streams (billions)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('top_10_streamed_songs_by_year.png')
plt.show()
