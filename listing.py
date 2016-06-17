from bs4 import BeautifulSoup
import urllib2
import urllib
import json
import sys

ALBUM_ART = False

def get_playlist_json(album_url):
    result = urllib2.urlopen(album_url)
    html = result.read()

    soup = BeautifulSoup(html,"lxml")

    sc = soup.find_all("script")
    sc = sc[4].string

    sc = sc[sc.find("=")+1:]
    sc = sc[sc.find("=")+1:]
    sc = sc.strip()
    sc = sc[:-1]

    return json.loads(sc)

def get_playlist(album_url):

    # METADATA
    #
    # if obj["description"]:
    #     line1 = "Description : "+obj["description"] +"\n"
    # else:
    #     line1 = "Description : " + "\n"
    # fp.write(line1.encode("utf-8"))
    # fp.write("Followers : "+str(obj["followers"]["total"]) +"\n" +"\n")

    obj = get_playlist_json(album_url)
    lst = obj["tracks"]["items"]
    playlist = []
    for song in lst:
        album=song["track"]["album"]["name"]
        artists=""
        for artist in song["track"]["artists"]:
            artists = artists + artist["name"] + ","
        artists = artists[:-1]

        # Duration info
        #
        # duration = song["track"]["duration_ms"]
        # duration = duration/(1000*1.0)
        # duration = int(round(duration))
        # mins = duration/60
        # secs = duration - mins*60
        # if secs < 10:
        #     duration = str(mins) + ":0" + str(secs)
        # else:
        #     duration = str(mins) + ":" + str(secs)

        name = song["track"]["name"]
        image_name = artists + " - " + album + ".jpg"
        # urllib.urlretrieve(song["track"]["album"]["images"][0]["url"],image_name.encode("utf-8"))
        # out_str = artists + " - " + name + " - " + album + " - " + str(duration)
        playlist.append( [ artists,name,album ] )

    return playlist

def get_youtube_links(pl):
    pass

def main():
    album_url = sys.argv[1]

    if ALBUM_ART:
        urllib.urlretrieve(obj["images"][0]["url"],"spotify_album_art.jpg")

    pl = get_playlist(album_url)

    yt_links = get_youtube_links(pl)




if __name__ == "__main__":
    main()
