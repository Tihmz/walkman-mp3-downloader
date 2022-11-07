from downloader import *
import sys
import re

MUSIC_FOLDER = "/home/tihmz/Music/"
def clean_filename(inp):
    regex = re.compile("[#<>%*&{}/\\\\$ +!`\"\'|=@]")
    filename = ""
    long_empty = False
    for i in inp:
        if not regex.findall(i):
            filename += i
            long_empty = False
        else:
            if not long_empty:
                filename += "_"
                long_empty = True
            else:
                pass

    return filename


def main():

    if len(sys.argv) > 2:
        print("Error, too much argument")
        sys.exit(1)

    elif len(sys.argv) <= 1:
        link = input("Please enter a song/playlist link : ")

    else:
        link = str(sys.argv[1])

    if link.find("spotify") != -1:

        if link.find("playlist") != -1:
            print("spotify playlist detected")
            url_list, title = spotify_playlist_parser(link)
            video_list = spotify_song_parser(url_list,title)

        elif link.find("track") != -1:
            print("spotify track detected")
            video_list = spotify_song_parser([link])

        download_list = yt_parser(video_list)

    elif link.find("youtube") != -1:
            if link.find("playlist") != -1:
                print("youtube playlist detected")
                url_list, title = yt_playlist_parser(link)
                download_list = yt_getVideoInfo(url_list,title)

            elif link.find("/watch?v=") != -1 :
                print("youtube video detected")
                download_list = yt_getVideoInfo([link])

    elif link.find("youtu.be") != -1:
        print("youtu.be video detected")
        download_list = yt_getVideoInfo([link])

    else:
        print("nothing detected")

    yt_downloader(download_list)

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
