from bs4 import BeautifulSoup
import urllib2
import urllib
import json
import sys
from urllib import quote_plus as qp
import sel
import os
import eyed3

ALBUM_ART = False
DEBUG = False
# playlist_name =""

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

    # get playlist json
    obj = get_playlist_json(album_url)

    # PLAYLIST METADATA
    if obj["description"]:
        desc = "Description : "+obj["description"] +"\n"
    else:
        desc = "Description : " + "\n"
    description = desc.encode("utf-8")
    followers = str(obj["followers"]["total"]) +"\n" +"\n"


    lst = obj["tracks"]["items"]
    playlist_name = obj["name"]

    # list of tracks with their info
    playlist = []
    for song in lst:
        album=song["track"]["album"]["name"]
        artists=[artist["name"] for artist in song["track"]["artists"]]

        # Duration info
        duration = song["track"]["duration_ms"]
        duration = duration/(1000*1.0)
        duration = int(round(duration))
        mins = duration/60
        secs = duration - mins*60
        if secs < 10:
            duration = str(mins) + ":0" + str(secs)
        else:
            duration = str(mins) + ":" + str(secs)

        name = song["track"]["name"]
        album_art_url = song["track"]["album"]["images"][0]["url"]
        song_id = song["track"]["id"]
        if DEBUG:
            print ",".join(artists) + " - " + name + " - " + album + " - " + str(duration)
        playlist.append( { "full_identifier": ",".join(artists) + " - " + name, "artists":artists,"song_name":name,"album":album,"album_art":album_art_url, "song_id":song_id.encode('utf-8'), "duration":duration } )

    return {"tracks":playlist, "playlist_name":playlist_name, "description":description, "followers":followers, "no_of_tracks":len(playlist)}

def get_youtube_links(playlist):
    base_url = "https://www.youtube.com/results?search_query="

    for i in playlist:
        query = '' + qp(i["song_name"])

        artist_arr = [qp(j) for j in i["artists"]]
        artists = artist_arr[0]
        for j in artist_arr[1:]:
            artists = artists + '+' + j

        query += '+'+artists
        req_url = base_url + query

        if DEBUG:
            print 'Search Query: ' + req_url

        result = urllib2.urlopen(req_url)
        html = result.read()
        soup = BeautifulSoup(html,"lxml")

        links = soup.find_all('h3',class_='yt-lockup-title')
        # TODO scrape title
        title_texts = [link.a.string for link in links]

        if DEBUG:
            print "\nLINK TITLES\n"
            for title in title_texts:
                print title,type(title)

        links_arr = [link.a['href'] for link in links]

        if DEBUG:
            print "\nLINKS\n"
            for link in links_arr:
                print link,type(link)

        i['yt_link'] = links_arr[0]

    # return yt_links

#adding id3 tags to downloaded file
def id3_tags(file_name,song):
    mp3_file = eyed3.load(file_name)
    mp3_file.tag.artist = song['artists'][0]
    mp3_file.tag.album = song['album']
    mp3_file.tag.title = song['song_name']
    urllib.urlretrieve(song['album_art'],"image.jpeg")
    imagefile = open("image.jpeg","rb").read()
    mp3_file.tag.images.set(3,imagefile,"image/jpeg")
    mp3_file.tag.save()
    os.remove("image.jpeg")

    #
def Download_from_playlist(d_link,file_name):
    if DEBUG:
        print d_link
    u = urllib2.urlopen(d_link)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s MBytes: %3.2f" % (file_name, file_size/(1024.0 ** 2))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    print

    f.close()



def main():
    album_url = sys.argv[1]

    if ALBUM_ART:
        urllib.urlretrieve(obj["images"][0]["url"],"spotify_album_art.jpg")

    print "Getting playlist..."
    playlist = get_playlist(album_url)
    if DEBUG:
        print playlist

    print "Fetched " + str(playlist["no_of_tracks"]) + " tracks from playlist " + playlist["playlist_name"]

    path = playlist["playlist_name"]
    if not os.path.isdir(path):
        print "Creating folder " + path
        os.mkdir(path)
    os.chdir(path)

    try:
        with open(".playlist_info","r") as fp:
            id_dic = [i[:-1] for i in fp.readlines()]

    except IOError:
        id_dic =[]


    if DEBUG:
        print id_dic

    # for song in playlist:
    #     if song["song_id"] not in id_dic:
    #         pl_new.append

    reduced_playlist = []
    for track in playlist["tracks"]:
        if track["song_id"] in id_dic:
            print "Skipping track " + track["full_identifier"] + " - Already exists"
        else:
            reduced_playlist.append(track)

    # playlist = [song for song in playlist if song["song_id"] not in id_dic]
    if playlist["no_of_tracks"] != len(reduced_playlist):
        print "Skipped " + str(playlist["no_of_tracks"] - len(reduced_playlist)) + " tracks"
        playlist["tracks"] = reduced_playlist
        playlist["no_of_tracks"] = len(reduced_playlist)

    if DEBUG:
        print playlist

    if playlist["no_of_tracks"] == 0:
        print "Done"
        return

    print "Fetching Youtube links..."
    get_youtube_links(playlist["tracks"])
    if DEBUG:
        print playlist

    print "Fetching download links..."
    sel.get_dl_list(playlist["tracks"],'www.youtube.com')

    if DEBUG:
        print playlist

    # download_songs(dl_list)





    print "Downloading songs.."

    for song in playlist["tracks"]:
        file_name = song['artists'][0] + ' - ' + song['song_name'] + ".mp3"
        Download_from_playlist(song['dl_link'],file_name)
        id3_tags(file_name,song)
        id_dic.append(song["song_id"])
        # else:
            # print "Skipping %s ..already exist" % (file_name)
    with open(".playlist_info","w") as fp:
        fp.write("\n".join(id_dic) + "\n")

    print "Done"



if __name__ == "__main__":
    main()
