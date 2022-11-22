#!/usr/bin/python3

import spotify_utils
import youtube_utils

import os
import sys

MUSIC_FOLDER = "/home/tihmz/Music/"

def main():
    if len(sys.argv) > 2:
        print("Error, too much argument")
        sys.exit(1)

    elif len(sys.argv) <= 1:
        link = input("Please enter a song/playlist link : ")

    else:
        link = str(sys.argv[1])

    if link.find("spotify") != -1:
        download_list = spotify_utils.run(link)
    elif link.find("youtube") != -1:
        download_list = youtube_utils.run(link)
    else:
        print("nothing detected, check your url")

    youtube_utils.yt_downloader(download_list)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\naborting, cleaning temporay files...")
        if os.path.exists("temp.mp3.part"):
            os.remove("temp.mp3.part")
        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")
        if os.path.exists("temp.html"):
            os.remove("temp.html")
