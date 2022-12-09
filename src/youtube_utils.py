import requests
import urllib.parse
import urllib.request
import youtube_dl
import html
import ffmpy
import os
import re

import main as Main

def run(link):
    if link.find("youtube") != -1 and link.find("playlist") != -1:
        print("youtube playlist detected")
        url_list, title = yt_playlist_parser(link)
        download_list = yt_getVideoInfo(url_list,title)

    elif link.find("youtube") != -1 and link.find("/watch?v=") != -1 :
        print("youtube video detected")
        download_list = yt_getVideoInfo([link])

    elif link.find("youtu.be") != -1:
        print("youtu.be video detected")
        download_list = yt_getVideoInfo([link])

    return download_list

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

    DIRECTORY = ""

    online_filenames = []

    if "directory" in video_list[0]:
        directory = video_list[0]["directory"]
        directory = clean_filename(directory)
        DIRECTORY = directory
        if os.path.exists(Main.MUSIC_FOLDER + directory):
            print("Directory %s already exist" % directory)
        else:
            print("Creating folder for playlist",directory)
            os.mkdir(Main.MUSIC_FOLDER + directory)

    for video in video_list :

        if video["title"].find(video["artist"]) != -1 or video["title"].find(" by ") != -1:
            filename = video["title"]+".mp3"
        else:
            filename = "{} by {}.mp3".format(video["title"],video["artist"])

        filename = clean_filename(filename)
        online_filenames.append(filename)

        if "directory" in video:
            filename = Main.MUSIC_FOLDER + directory + "/" + filename
        else:
            if not os.path.exists(Main.MUSIC_FOLDER + "/Downloader/"):
                os.mkdir(Main.MUSIC_FOLDER + "/Downloader/")
            filename = Main.MUSIC_FOLDER + "/Downloader/" + filename


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

    if DIRECTORY != "":
        local_filenames = os.listdir(Main.MUSIC_FOLDER + "/" + DIRECTORY + "/")
        for filename in local_filenames:
            if filename not in online_filenames:
                print(filename,"has been deleted online, removing it...")
                os.remove(Main.MUSIC_FOLDER+"/"+DIRECTORY+"/"+filename)


