import requests
import urllib.parse
import urllib.request
import youtube_dl
import sys
import html

url_dl ="https://www.youtube.com/watch?v="

def spotify_song_parser(url_list):

    encoded_links = []

    for url in url_list:

        r = requests.get(url)

        i1 = r.text.index("<title>")
        i2 = r.text.index("</title")
        title = r.text[i1+7:i2]

        i1 = r.text.index(",\"description\":\"Listen to")
        i2 = r.text.index(",\"datePublished\"")
        result = r.text[i1+26:i2-1]

        song = {
            "title": result[:result.index(" on Spotify")],
            "artist": title[title.index("song by")+8:title.index(" | Spotify")]
        }

        query_encoded = urllib.parse.quote(song["title"]+" "+song["artist"])
        encoded_links.append(query_encoded)

    return encoded_links

def yt_parser(video_links):
    
    video_list = []

    for encoded_link in video_links:

        r = requests.get("https://www.youtube.com/results?search_query=" + encoded_link)
        response = r.text
        video_url = url_dl + response[response.index("/watch?v=")+9:response.index("/watch?v=")+20]
        video_list.append(video_url)

    return video_list 

def yt_getVideoInfo(video_links):
    
    video_list = []

    for i in video_links :
        print(i)

def yt_downloader(video_list):

    for video in video_list :
        filename = "{} by {}.mp3".format(video["title"],video["artist"])
        options={
            'format':'bestaudio/best',
            'keepvideo':False,
            'outtmpl':filename,
        }
        print(song["video_url"])
        ydl = youtube_dl.YoutubeDL(options)
        ydl.download([video["video_url"]])

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
            url_list = spotify_playlist_parser(link)
            video_list = spotify_song_parser(url_list)

        elif link.find("track") != -1:
            print("spotify track detected")
            video_links = spotify_song_parser([link])

    elif link.find("youtube") != -1:
            print("youtube")

    video_links = yt_parser(video_links)
    video_list = yt_getVideoInfo(video_links) 
    # yt_downloader(video_list)

if __name__ == "__main__":
    try:    
        main()
    except KeyboardInterrupt:
        func.debug("KeyboardInterrupt")








