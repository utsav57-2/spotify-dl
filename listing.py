from bs4 import BeautifulSoup
import urllib2
import urllib
import json
import sys
from urllib import quote_plus as qp

ALBUM_ART = False
DEBUG = False

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
        artists=[artist["name"] for artist in song["track"]["artists"]]
        # for artist in song["track"]["artists"]:
        #     artists.append(artist["name"])

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
        # image_name = artists + " - " + album + ".jpg"
        # urllib.urlretrieve(song["track"]["album"]["images"][0]["url"],image_name.encode("utf-8"))
        # out_str = artists + " - " + name + " - " + album + " - " + str(duration)
        playlist.append( { "artists":artists,"song_name":name,"album":album } )

    return playlist

def get_youtube_links(pl):
    base_url = "https://www.youtube.com/results?search_query="
    yt_links = []

    for i in pl:
        query = '' + qp(i["song_name"])

        artist_arr = [qp(j) for j in i["artists"]]
        artists = artist_arr[0]
        for j in artist_arr[1:]:
            artists = artists + '+' + j

        query += '+'+artists
        req_url = base_url + query

        if DEBUG:
            for i in req_url:
                print i

        result = urllib2.urlopen(req_url)
        html = result.read()
        soup = BeautifulSoup(html,"lxml")

        links = soup.find_all('h3',class_='yt-lockup-title')
        # TODO
        links_texts = [i.a.string for i in links]
        links_arr = [i.a['href'] for i in links]
        yt_links.append(links_arr[0])

    return yt_links





def main():
    album_url = sys.argv[1]

    if ALBUM_ART:
        urllib.urlretrieve(obj["images"][0]["url"],"spotify_album_art.jpg")

    pl = get_playlist(album_url)

    yt_links = get_youtube_links(pl)

    if DEBUG:
        for i in yt_links:
            print 'https://www.youtube.com'+i



if __name__ == "__main__":
    main()
