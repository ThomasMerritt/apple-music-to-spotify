from bs4 import BeautifulSoup
import requests, re
import functions

def main():
    playlist_url = 'https://music.apple.com/us/playlist/%E4%B8%A8%E7%88%AA-%E5%8D%84%E4%B8%A8%EA%AE%86%E5%8D%84/pl.u-zPyLmq6uZ563dNA'

    response = requests.get(playlist_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    song_meta_data_tags = soup.find_all('meta', property=re.compile(r"music:song:preview_url:secure_url"))
    song_urls = [tag["content"] for tag in song_meta_data_tags]

    song_data = [functions.get_song_metadata(url) for url in song_urls]

    results = []
    for i in range(len(song_data)):
        try:
            results.append(functions.search_spotify(song_data[i]['artists'], song_data[i]['title']))
        except:
            print(f"⚠️ Error searching for {song_data[i]['title']} by {song_data[i]['artists']}")
            functions.add_to_failed_list(song_data[i]['title'], song_data[i]['artists'])
            pass
    
    print('\n  Adding songs to playlist')
            
    for result in results:
        try:
            functions.add_to_spotify(result)
        except:
            print(f"⚠️ Error adding {result['title']} by {result['artists']} to playlist")
            functions.add_to_failed_list(song_data[results.index(result)]['title'], song_data[results.index(result)]['artists'])
            pass

    print('\n  Songs added to playlist')

if __name__ == "__main__":
    main()