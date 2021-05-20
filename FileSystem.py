import glob
from mutagen.easyid3 import EasyID3
#from mutagen.id3 import ID3
#from mutagen.mp3 import MP3
import chardet
from collections import defaultdict

def def_value():
    return [""]

EasyID3.RegisterTextKey('comment', 'COMM')
print("comment added")
def getAllMp3(path, v = None):
    tracks = defaultdict(def_value)
    Nb = len(list(glob.iglob(path + '**/*.mp3', recursive=True)))
    print("Loading tracks :")
    i = 0
    percent = "00%"
    print(percent, end="")
    for filename in glob.iglob(path + '**/*.mp3', recursive=True):
        #encoding = chardet.detect(str.encode(filename)).get("encoding")
        fn = filename.encode("utf-8", "ignore").decode("utf-8")
        for f in glob.glob(fn):
            #mp3info = EasyID3(f)
            mp3info = getMp3Info(f)
            tracks[fn] = mp3info

            percent = str(int(100*i/Nb)) + "%"
            if(v is None):
                print("\b"*(1 + len(percent)), end="")
                print(percent, end="")
            else:
                v = percent
            i += 1

    if(v is None):
        print("\b"*(1 + len(percent)), "100%...LOADED ", len(tracks))
    else:
        v = "\b"*(1 + len(percent)) + "100%...LOADED " + len(tracks)
    return tracks

def filterTracks(tracks, v):
    newDict = dict()
    for (key, value) in tracks.items():
        if str(value).lower().find(str(v).lower()) >= 0:
            newDict[key] = value
    if(len(newDict) > 0):
        print(len(newDict), " tracks compatilbe with the filter ", v)
        return newDict
    else:
        print("No compatilbe tracks with the filter ", v)
        return tracks

def getMp3Info(mp3FileName):
    mp3info = EasyID3(mp3FileName)
    symbols = ["/", ",", "&", " ;", "; "]
    for f in mp3info.keys():
        txt = mp3info[f][0].lower()
        for s in symbols:
            txt = txt.replace(s, ";")
        mp3info[f] = txt.split(";")
    return mp3info