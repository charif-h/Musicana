import os
import base64
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import Picture

# Formats pygame.mixer can play; m4a/wma wait for the VLC backend (M3).
AUDIO_EXTENSIONS = ('.mp3', '.flac', '.ogg', '.wav')

EasyID3.RegisterTextKey('comment', 'COMM')

def listAudioFiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.lower().endswith(AUDIO_EXTENSIONS):
                yield os.path.normpath(os.path.join(root, name))

def getAllTracks(path):
    tracks = {}
    files = list(listAudioFiles(path))
    Nb = len(files)
    print("Loading tracks :")
    percent = "00%"
    print(percent, end="")
    for i, f in enumerate(files):
        try:
            tracks[f] = getTrackInfo(f)
        except (mutagen.MutagenError, OSError) as e:
            print("\nSkipping unreadable file", f, ":", e)

        percent = str(int(100*i/Nb)) + "%"
        print("\b"*(1 + len(percent)), end="")
        print(percent, end="")

    print("\b"*(1 + len(percent)), "100%...LOADED ", len(tracks))
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

# Returns {tag: [lowercase values]} for any format mutagen reads, e.g.
# {"artist": ["queen", "david bowie"], "title": ["under pressure"]}.
def getTrackInfo(fileName):
    audio = mutagen.File(fileName, easy=True)
    if(audio is None):
        raise mutagen.MutagenError("unknown audio format")
    info = {}
    if(audio.tags is not None):
        symbols = ["/", ",", "&", " ;", "; "]
        for f in audio.tags.keys():
            values = audio.tags[f]
            if not(isinstance(values, list) and all(isinstance(v, str) for v in values)):
                continue  # raw frames (e.g. ID3 in WAV) have no easy text form
            txt = ";".join(values).lower()
            for s in symbols:
                txt = txt.replace(s, ";")
            parts = [p.strip() for p in txt.split(";") if p.strip()]
            if(parts):
                info[f.lower()] = parts
    if("title" not in info):
        info["title"] = [os.path.splitext(os.path.basename(fileName))[0].lower()]
    return info

def getArtwork(fileName):
    audio = mutagen.File(fileName)
    if(audio is None):
        return None
    if(getattr(audio, "pictures", None)):  # FLAC
        return audio.pictures[0].data
    tags = audio.tags
    if(tags is None):
        return None
    if(hasattr(tags, "getall")):  # ID3
        apic = tags.getall("APIC")
        return apic[0].data if apic else None
    if("covr" in tags):  # MP4
        return bytes(tags["covr"][0])
    if("metadata_block_picture" in tags):  # Ogg
        return Picture(base64.b64decode(tags["metadata_block_picture"][0])).data
    return None
