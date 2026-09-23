import os
import base64
import mutagen
from mutagen.asf import ASF
from mutagen.easyid3 import EasyID3
from mutagen.flac import Picture

import TrackCache

AUDIO_EXTENSIONS = ('.mp3', '.flac', '.ogg', '.wav', '.m4a', '.wma')

# WMA has no easy tag mode: map its attribute names to the easy ones.
ASF_KEYS = {"Title": "title", "Author": "artist", "WM/AlbumTitle": "album", "WM/AlbumArtist": "albumartist",
            "WM/Genre": "genre", "WM/Year": "date", "WM/Composer": "composer", "WM/TrackNumber": "tracknumber"}

EasyID3.RegisterTextKey('comment', 'COMM')

def listAudioFiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.lower().endswith(AUDIO_EXTENSIONS):
                yield os.path.normpath(os.path.join(root, name))

# Tags are only re-read for files that are new or changed since the cached scan.
# progress(done, total), if given, is called after each file read instead of printing to the console.
def getAllTracks(path, cachePath=None, progress=None):
    cachePath = cachePath or TrackCache.defaultPath()
    cache = TrackCache.load(cachePath)
    root = os.path.normpath(path) + os.sep
    entries = {k: v for k, v in cache.items() if not k.startswith(root)}  # other libraries
    tracks = {}
    toRead = []
    for f in listAudioFiles(path):
        try:
            stat = os.stat(f)
        except OSError as e:
            print("Skipping unreadable file", f, ":", e)
            continue
        entry = cache.get(f)
        if(TrackCache.isFresh(entry, stat)):
            entries[f] = entry
            tracks[f] = entry["tags"]
        else:
            toRead.append((f, stat))

    Nb = len(toRead)
    print("Loading tracks :", len(tracks), "cached,", Nb, "to read")
    percent = "00%"
    print(percent, end="")
    for i, (f, stat) in enumerate(toRead):
        try:
            tracks[f] = getTrackInfo(f)
            entries[f] = TrackCache.makeEntry(stat, tracks[f])
        except (mutagen.MutagenError, OSError) as e:
            print("\nSkipping unreadable file", f, ":", e)

        if(progress is not None):
            progress(i + 1, Nb)
            continue
        percent = str(int(100*i/Nb)) + "%"
        print("\b"*(1 + len(percent)), end="")
        print(percent, end="")

    print("\b"*(1 + len(percent)), "100%...LOADED ", len(tracks))
    if(entries != cache):
        try:
            TrackCache.save(cachePath, entries)
        except OSError as e:
            print("Could not save metadata cache", cachePath, ":", e)
    return tracks

def matches(tags, v):
    return str(tags).lower().find(str(v).lower()) >= 0

def filterTracks(tracks, v):
    newDict = dict()
    for (key, value) in tracks.items():
        if matches(value, v):
            newDict[key] = value
    print(len(newDict), " tracks compatilbe with the filter ", v)
    return newDict

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
            if(isinstance(audio, ASF)):
                if(f not in ASF_KEYS):
                    continue
                values = [str(v) for v in values]
                f = ASF_KEYS[f]
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
    if(isinstance(audio, ASF)):
        pics = tags.get("WM/Picture")
        return asfPictureData(pics[0].value) if pics else None
    if("covr" in tags):  # MP4
        return bytes(tags["covr"][0])
    if("metadata_block_picture" in tags):  # Ogg
        return Picture(base64.b64decode(tags["metadata_block_picture"][0])).data
    return None

# WM/Picture: type byte, data length (4), mime and description as UTF-16 zero-terminated, then data.
def asfPictureData(value):
    pos = 5
    for _ in range(2):
        end = pos
        while value[end:end + 2] != b"\x00\x00":
            end += 2
        pos = end + 2
    return value[pos:]
