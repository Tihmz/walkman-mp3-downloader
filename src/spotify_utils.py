import requests
import html
import urllib.parse
import youtube_utils

def run(link):
    if link.find("playlist") != -1:
        print("spotify playlist detected")
        url_list, title = spotify_playlist_parser(link)
        video_list = spotify_song_parser(url_list,title)

    elif link.find("track") != -1:
        print("spotify track detected")
        video_list = spotify_song_parser([link])

    download_list = youtube_utils.yt_parser(video_list)
    return download_list


def spotify_playlist_parser(url):

    r = requests.get(url)
    page = html.unescape(r.text)

    i1 = page.index("<title>")
    i2 = page.index("Spotify</title>")
    title = page[i1+7:i2]
    title = title[:title.index(" - playlist by")]

    i = page.find("https://open.spotify.com/track/")

    url_list = []

    while i != -1:

        url = page[i:i+53]
        url_list.append(url)
        page=page[i+53:]
        i = page.find("https://open.spotify.com/track/")

    url_list = list(set(url_list))
    return url_list, title

def spotify_song_parser(url_list,directory=None):

    song_list = []

    for url in url_list:

        r = requests.get(url)

        i1 = r.text.index("<title>")
        i2 = r.text.index("</title")
        description = html.unescape(r.text[i1+7:i2])

        song = {
            "title": description[:description.index(" - song and lyrics by")],
            "artist": description[description.index("- song and lyrics by")+21:description.index(" | Spotify")]
        }

        query_encoded = urllib.parse.quote(song["title"]+" "+song["artist"])

        song["encoded_link"] = query_encoded
        song_list.append(song)

        if directory != None:
            song["directory"]=directory

    return song_list


