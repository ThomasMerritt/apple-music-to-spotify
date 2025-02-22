from bs4 import BeautifulSoup
# from auth import SpotifyAuth
# from difflib import SequenceMatcher
import requests, re, json, config

def search_spotify(artist, title):
    query = f"{title} {artist}"
    search_results = config.sp.search(q=query, type='track', limit=1)
    
    if search_results['tracks']['items']:
        return search_results['tracks']['items'][0]['uri']
    else:
        return None

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


def main():
    playlist_url = 'https://music.apple.com/us/playlist/%E4%B8%A8%E7%88%AA-%E5%8D%84%E4%B8%A8%EA%AE%86%E5%8D%84/pl.u-zPyLmq6uZ563dNA'

    response = requests.get(playlist_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    song_meta_data_tags = soup.find_all('meta', property=re.compile(r"music:song:preview_url:secure_url"))
    song_urls = [tag["content"] for tag in song_meta_data_tags]

    song_data = [get_song_metadata(url) for url in song_urls]

    results = []
    for i in range(5):
        try:
            results.append(search_spotify(song_data[i]['artists'], song_data[i]['title']))
        except:
            print(f"⚠️ Error searching for {song_data[i]['title']} by {song_data[i]['artists']}")
            pass
            
    print(results)
    # with open('apple_music_songs.json', 'w') as f:
    #     json.dump(song_data, f, indent=2)

    # print('\n  Json data saved to apple_music_songs.json')



if __name__ == "__main__":
    main()