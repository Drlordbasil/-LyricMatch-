import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


class LyricMatcher:
    def __init__(self):
        self.lyrics_websites = [
            "https://www.metrolyrics.com",
            "https://genius.com",
            "https://www.lyrics.com",
        ]

    def search_lyrics(self, search_query):
        search_results = []
        for website in self.lyrics_websites:
            try:
                url = f"{website}/search/{search_query.replace(' ', '+')}"
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    results = soup.find_all("div", class_="content")
                    for result in results:
                        title_element = result.find("a", class_="title")
                        if title_element:
                            title = title_element.text.strip()
                            artist_element = result.find("a", class_="artist")
                            artist = (
                                artist_element.text.strip() if artist_element else None
                            )
                            link = website + title_element["href"]
                            search_results.append(
                                {"title": title, "artist": artist, "link": link}
                            )
            except requests.exceptions.RequestException:
                pass
        return search_results

    def calculate_similarity(self, input_lyrics, song_lyrics):
        return SequenceMatcher(None, input_lyrics, song_lyrics).ratio()

    def find_song(self, input_lyrics):
        songs = []
        for website in self.lyrics_websites:
            try:
                url = f"{website}/random"
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    song_lyrics = soup.find("div", class_="lyrics-body")
                    if song_lyrics:
                        song_lyrics = song_lyrics.text.strip()
                        song_title = soup.find("h1").text.strip()
                        artist_name = soup.find("h2").text.strip()

                        similarity = self.calculate_similarity(
                            input_lyrics, song_lyrics
                        )

                        songs.append(
                            {
                                "title": song_title,
                                "artist": artist_name,
                                "lyrics": song_lyrics,
                                "similarity": similarity,
                                "website": website,
                            }
                        )
            except requests.exceptions.RequestException:
                pass
        songs.sort(key=lambda x: x["similarity"], reverse=True)
        matched_songs = songs[:5]
        return matched_songs


if __name__ == "__main__":
    matcher = LyricMatcher()

    # Input your desired lyrics to search
    input_lyrics = "I want to hold your hand"
    search_results = matcher.search_lyrics(input_lyrics)

    if search_results:
        print("Search Results:")
        for result in search_results:
            print(f"Title: {result['title']}")
            print(f"Artist: {result['artist']}")
            print(f"Link: {result['link']}")
            print()
        selected_song_link = search_results[0]["link"]
        print("Selected Song Link:", selected_song_link)
        print()

        matched_songs = matcher.find_song(input_lyrics)

        if matched_songs:
            print("Matched Songs:")
            for song in matched_songs:
                print(f"Title: {song['title']}")
                print(f"Artist: {song['artist']}")
                if len(song["lyrics"]) > 200:
                    print(f"Lyrics:\n{song['lyrics'][:200]}...")
                else:
                    print(f"Lyrics:\n{song['lyrics']}")
                print(f"Similarity: {song['similarity']}")
                print(f"Website: {song['website']}")
                print()
        else:
            print("No matched songs found.")
    else:
        print("No search results found.")
