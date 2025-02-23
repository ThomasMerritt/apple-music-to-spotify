from bs4 import BeautifulSoup
import json, config, requests
import time

def add_to_failed_list(title, artist):
    with open('failed.txt', 'a') as f:
        f.write(f"{title} - {artist}\n")
        
def search_spotify(artist, title):
    query = f"{title} {artist}"
    attempts = 5
    delay = 2

    for attempt in range(attempts):
        try:
            search_results = config.sp.search(q=query, type='track', limit=1)
            return search_results['tracks']['items'][0]['uri']
        except Exception as e:
            if '429' in str(e):
                print(f"⚠️ Rate limit exceeded, waiting {delay} seconds before retrying...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"⚠️ Spotify API error: {e}")
                return None
    
def add_to_spotify(uri):
    attempts = 5
    delay = 2

    for attempt in range(attempts):
        try:
            config.sp.current_user_saved_tracks_add(tracks=[uri])
        except Exception as e:
            if '429' in str(e):
                print(f"⚠️ Rate limit exceeded, waiting {delay} seconds before retrying...")
                time.sleep(delay)
            else:
                print(f"❌ Error adding {uri} to Spotify: {e}")
                return
        

def get_song_metadata(song_url):
    print(f"Fetching: {song_url}")
    
    try:
        response = requests.get(song_url)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch {song_url}, Status Code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", {"type": "application/json", "id": "serialized-server-data"})
        if not script_tag:
            print(f"⚠️ No JSON metadata found for {song_url}")
            return None
        
        # Parse JSON
        json_data = json.loads(script_tag.string)

        # Extract relevant metadata
        song_title = json_data[0]["data"]["sections"][0]["items"][0]["title"]
        artists = json_data[0]["data"]["sections"][0]["items"][0]["artists"]

        print(f"✅ Extracted: {song_title} by {artists}")

        return {
            "title": song_title,
            "artists": artists,
            "url": song_url
        }

    except Exception as e:
        print(f"❌ Error processing {song_url}: {e}")
        return None