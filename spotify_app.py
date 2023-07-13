"""App to create Playlist on Spotify with OpenAI"""

import argparse
import datetime
import logging
import json
import os

import spotipy
import openai
from dotenv import load_dotenv


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """summary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """
    # Getting args pass on the script
    parser = argparse.ArgumentParser(description="Simple command line song")
    parser.add_argument(
        "-p",
        default="Will playlist",
        type=str,
        help="The prompt to describe the playlist",
    )
    parser.add_argument(
        "-n",
        default=15,
        type=int,
        help="Number of songs to add to the playlist",
    )
    # Adding API KEYS File from script
    parser.add_argument(
        "-envfile",
        default=".env",
        type=str,
        required=False,
        help="File with your env variables",
    )

    args = parser.parse_args()
    # Using dotenv try to load the API KEYS
    load_dotenv(args.envfile)
    if any(
        x not in os.environ
        for x in (
            "SPOTIFY_CLIENT_ID",
            "SPOTIFY_CLIENT_SECRET",
            "OPENAI_API_KEY",
        )
    ):
        raise ValueError(
            "Error missing environment variables. Check your env file"
        )
    if args.n not in range(1, 100):
        raise ValueError("Error: n should be between 1 and 100")
    openai.api_key = os.environ["OPENAI_API_KEY"]
    playlist_prompt = args.p
    count = args.n
    playlist = get_playlist(playlist_prompt, count)
    add_songs_to_spotify(playlist_prompt, playlist)


def get_playlist(prompt, count=15):
    """
    Purpose: Give example to ChatGPT of how we want the answer
    Return: Content with song and artist
    """
    example_json = """
        [
    {"song": "Happy", "artist": "Pharrell Williams"},
    {"song": "Can't Stop the Feeling!", "artist": "Justin Timberlake"},
    {"song": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars"},
    {"song": "Shut Up and Dance", "artist": "Walk The Moon"},
    {"song": "Don't Stop Me Now", "artist": "Queen"},
    {"song": "24K Magic", "artist": "Bruno Mars"},
    {"song": "Good Vibrations", "artist": "The Beach Boys"},
    {"song": "I Wanna Dance with Somebody", "artist": "Whitney Houston"},
    {"song": "Happy Together", "artist": "The Turtles"},
    {"song": "Dancing Queen", "artist": "ABBA"}
        ]
    """
    messages = [
        {
            "role": "system",
            "content": """ You are a helpful playlist generating assistant.
    You should generate a list off songs and their artists according to a text prompt
    You should return a JSON array, where each element follow this format:
    `{"song": <song_title>, "artist": <artist_name>}`
    """,
        },
        {
            "role": "user",
            "content": "Generate a playlist of 10 songs based on this prompt: super super hype happy songs",
        },
        {"role": "system", "content": example_json},
        {
            "role": "user",
            "content": f"Generate a playlist of {count} songs based on this prompt: {prompt}",
        },
    ]
    # This response is where we fill up with the example and message together,
    # model we want to use and how many tokens max
    response = openai.ChatCompletion.create(
        messages=messages, model="gpt-3.5-turbo", max_tokens=800
    )
    # return json.loads(response['choices'][0]['message']['content'])
    # print(response['choices'][0]['message']['content'])
    playlist = json.loads(response["choices"][0]["message"]["content"])
    return playlist


# end def


def add_songs_to_spotify(playlist_prompt, playlist):
    """
    Purpose: Add songs to spotify base on the prompt command we send and the
    playlist generate in get_playlist (song - artist)
    Return: Print of the name and url of the new playlist
    """
    # Sign up as a developer and register your app

    # Step 1. Create an App
    # Step 2. Copy your Client ID and Client Secret
    spotipy_client_id = os.environ["SPOTIFY_CLIENT_ID"]
    spotipy_client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

    # Step 3. Click 'Edit Settings'
    spotipy_redirect_url = "http://localhost:9999"
    # Step 4. Click `Users and Access Add your Spotify account
    # pylint: disable=invalid-name
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=spotipy_client_id,
            client_secret=spotipy_client_secret,
            redirect_uri=spotipy_redirect_url,
            scope="playlist-modify-playlist",
        )
    )
    current_user = sp.current_user()
    # Checking if the user is logging
    assert current_user is not None

    track_ids = []  # List that will be empty and adding later song and artist

    # For Loop to add each song with the artists in spotify
    for item in playlist:
        artist, song = item["artist"], item["song"]
        advance_query = f"artist:({artist}) track:({song}) "
        basic_query = f"{song} {artist}"
        for query in [advance_query, basic_query]:
            # pylint: disable=logging-fstring-interpolation
            log.debug(f"Searching for query: {query}")
            search_results = sp.search(
                q=query, type="track", limit=10
            )  # , market=market)
            if (
                not search_results["tracks"]["items"]
                or search_results["tracks"]["items"][0]["popularity"] < 20
            ):
                continue
            good_guess = search_results["tracks"]["items"][0]
            print([f"Found: {good_guess['name']} [{good_guess['id']}]"])
            track_ids.append(good_guess["id"])
            break
        else:
            print(
                f"Queries {advance_query} and {basic_query} returned no good results"
            )
    created_playlist = sp.user_playlist_create(
        current_user["id"],
        public=False,
        name=f"{playlist_prompt} ({datetime.datetime.now().strftime('%m/%Y')})",
    )
    sp.user_playlist_add_tracks(
        current_user["id"], created_playlist["id"], track_ids
    )
    print("\n")
    print(f"Created playlist: {created_playlist['name']}")
    print(created_playlist["external_urls"]["spotify"])


if __name__ == "__main__":
    main()
