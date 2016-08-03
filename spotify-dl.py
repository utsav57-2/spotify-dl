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
DEBUG = True
playlist_name =""

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
    global playlist_name
    obj = get_playlist_json(album_url)
    lst = obj["tracks"]["items"]
    playlist_name = obj["name"]
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
        album_art_url = song["track"]["album"]["images"][0]["url"]
        song_id = song["track"]["id"]
        # out_str = artists + " - " + name + " - " + album + " - " + str(duration)
        playlist.append( { "artists":artists,"song_name":name,"album":album,"album_art":album_art_url, "song_id":song_id.encode('utf-8') } )

    return playlist

def print_playlist(pl):
    print "\nPLAYLIST:\n"
    for track in pl:
        for j in track:
            print j,": ",track[j]
        print

    print


def get_youtube_links(pl):
    base_url = "https://www.youtube.com/results?search_query="

    for i in pl:
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
    pl = get_playlist(album_url)
    if DEBUG:
        print_playlist(pl)

    print "Creating folder..."
    path = playlist_name
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)

    try:
        with open(".id_file","r") as fp:
            id_dic = [i[:-1] for i in fp.readlines()]

    except IOError:
        id_dic =[]


    if DEBUG:
        print id_dic

    # for song in pl:
    #     if song["song_id"] not in id_dic:
    #         pl_new.append

    pl = [song for song in pl if song["song_id"] not in id_dic]

    if DEBUG:
        print pl

    print "Fetching Youtube links..."
    get_youtube_links(pl)
    if DEBUG:
        print_playlist(pl)


    if DEBUG:
        print_playlist(pl)

    print "Fetching download links..."
    sel.get_dl_list(pl,'www.youtube.com')

    if DEBUG:
        print_playlist(pl)

    # download_songs(dl_list)





    print "Downloading songs.."

    for song in pl:
        file_name = song['artists'][0] + ' - ' + song['song_name'] + ".mp3"
        Download_from_playlist(song['dl_link'],file_name)
        id3_tags(file_name,song)
        id_dic.append(song["song_id"])
        # else:
            # print "Skipping %s ..already exist" % (file_name)
    with open(".id_file","w") as fp:
        fp.write("\n".join(id_dic) + "\n")



if __name__ == "__main__":
    main()
