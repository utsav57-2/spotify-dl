from bs4 import BeautifulSoup
import urllib2
import urllib
import json

# res = urllib2.urlopen("http://open.spotify.com/user/spotify/playlist/5yolys8XG4q7YfjYGl5Lff")   #rap caviar
# res = urllib2.urlopen("http://open.spotify.com/user/spotify/playlist/2qTeRwnwFquJUKrAFWnolb")   #viral hits
res = urllib2.urlopen("http://open.spotify.com/user/billboard.com/playlist/6UeSakyzhiEt4NB3UAd6NQ")   #billboard
html = res.read()

soup = BeautifulSoup(html,"lxml")

sc = soup.find_all("script")
sc = sc[4].string
sc.replace("\n","")

sc = sc[sc.find("=")+1:]
sc = sc[sc.find("=")+1:]
sc = sc.strip()
sc = sc[:-1]

obj = json.loads(sc)

urllib.urlretrieve(obj["images"][0]["url"],"spotify_album_art.jpg")

with open(obj["name"],"w") as fp:
    line1 = "Description : "+obj["description"] +"\n"
    fp.write(line1.encode("utf-8"))
    fp.write("Followers : "+str(obj["followers"]["total"]) +"\n" +"\n")

    lst = obj["tracks"]["items"]
    for song in lst:
        album=song["track"]["album"]["name"]
        artists=""
        for artist in song["track"]["artists"]:
            artists = artists + artist["name"] + ","
        artists = artists[:-1]
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
        image_name = artists + " - " + album + ".jpg"
        # urllib.urlretrieve(song["track"]["album"]["images"][0]["url"],image_name.encode("utf-8"))
        out_str = artists + " - " + name + " - " + album + " - " + str(duration)
        fp.write(out_str.encode("utf-8")+"\n")
