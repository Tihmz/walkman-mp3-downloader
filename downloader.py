#!/usr/bin/python3
import requests
import urllib.parse
import urllib.request
import youtube_dl
import sys
import html
import ffmpy
import os

def clean_filename(inp):
    l = [" ", "\"", "\'","|",":",",","/"]
    # todo, make a list and then "for i not in l" for a better filter
    filename = ""
    for i in inp:
        if i in l:
            filename+="_"
        else:
            filename+=i

    return filename

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
        directory = clean_filename(directory)
        if os.path.exists(directory):
            print("Directory % already exist" % directory)
        else:
            print("Creating folder for playlist",directory)
            os.mkdir(directory)

    for video in video_list :
        
        if video["title"].find(video["artist"]) != -1 or video["title"].find(" by ") != -1:
            s = video["title"]+".mp3"
        else:
            s = "{} by {}.mp3".format(video["title"],video["artist"])

        filename=clean_filename(s)

        if "directory" in video:
            filename = video["directory"] + "/" + filename

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

    # for i in download_list:
    #     print(i)
    yt_downloader(download_list)

if __name__ == "__main__":
    try:    
        main()
    except KeyboardInterrupt:
        print("aborting")
