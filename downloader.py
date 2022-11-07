#!/usr/bin/python3
import requests
import urllib.parse
import urllib.request
import youtube_dl
import html
import ffmpy
import os
import main as Main

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
    c = 0

    for url in url_list:

        r = requests.get(url)

        i1 = r.text.index("<title>")
        i2 = r.text.index("</title")
        description = html.unescape(r.text[i1+7:i2])

        song = {
            "title": description[:description.index(" - song by")],
            "artist": description[description.index("song by")+8:description.index(" | Spotify")]
        }

        query_encoded = urllib.parse.quote(song["title"]+" "+song["artist"])

        song["encoded_link"] = query_encoded
        song_list.append(song)

        if directory != None:
            song["directory"]=directory

        c+=1
        p = 100*c/int(len(url_list))
        print(str(p)+"%")

    return song_list

def yt_parser(video_links):

    video_list = []

    for video in video_links:

        r = requests.get("https://www.youtube.com/results?search_query=" + video["encoded_link"])
        response = r.text
        video_url = "https://www.youtube.com" + response[response.index("/watch?v="):response.index("/watch?v=")+20]
        video["video_url"] = video_url
        video_list.append(video)

    return video_list

def yt_playlist_parser(url):

    url_list = []

    r = urllib.request.urlopen(url)
    page = r.read().decode()

    i1 = page.index("<title>")
    i2 = page.index(" - YouTube</title>")
    title = page[i1+7:i2]

    i = page.find("/watch?v=")
    url_list = []

    while i != -1:

        url = page[i:i+20]
        url_list.append("https://www.youtube.com" + url)
        page=page[i+44:]
        i = page.find("/watch?v=")

    url_list = list(set(url_list))
    return url_list,title

def yt_getVideoInfo(video_links,directory=None):

    video_list = []

    for url in video_links :

        r = requests.get(url)

        page = html.unescape(r.text)

        i1 = page.index("<title>")
        i2 = page.index(" - YouTube</title>")
        title = page[i1+7:i2]

        channel = page[page.index("\"name\":")+9:]
        channel = channel[:channel.index("\"}}]}")]

        video = {
            "title":title,
            "artist":channel,
            "video_url":url
        }

        if directory != None:
            video["directory"]=directory

        video_list.append(video)

    return video_list

def yt_downloader(video_list):

    if "directory" in video_list[0]:
        directory = video_list[0]["directory"]
        directory = Main.clean_filename(directory)
        if os.path.exists( Main.MUSIC_FOLDER + directory):
            print("Directory %s already exist" % directory)
        else:
            print("Creating folder for playlist",directory)
            os.mkdir(Main.MUSIC_FOLDER + directory)

    for video in video_list :

        if video["title"].find(video["artist"]) != -1 or video["title"].find(" by ") != -1:
            filename = video["title"]+".mp3"
        else:
            filename = "{} by {}.mp3".format(video["title"],video["artist"])

        filename = Main.clean_filename(filename)

        if "directory" in video:
            filename = Main.MUSIC_FOLDER + video["directory"] + "/" + filename

        if os.path.exists(filename):
            print("%s already exist" % filename)

        else:
            options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl':"temp.mp3",
            }

            print("[Downloading",filename,"]")
            ydl = youtube_dl.YoutubeDL(options)
            ydl.download([video["video_url"]])

            ff = ffmpy.FFmpeg(
            inputs={'temp.mp3': None},
            outputs={filename: None}
            )
            ff.run()
            print("[Removing temporary file]")
            os.remove("temp.mp3")

