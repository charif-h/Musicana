import os
import random

import Nexter_RandomWalk
from Nexter_RandomWalk import TrackFilter

# Every agent answers the same question: which track should follow `current`, given the recently
# played `history` (tracks to avoid)? next() returns (track, cause), where cause (album, artist,
# genre, date, random...) is what links the two tracks, and what the Commentator announces.
class RecommendationAgent():
    id = ""
    name = ""
    description = ""

    def next(self, tracks, current, history):
        raise NotImplementedError

class RandomWalk(RecommendationAgent):
    id = "random-walk"
    name = "Random walk"
    description = "Jumps to a track sharing something with the current one: album, artist, genre, year…"
    features = Nexter_RandomWalk.FEATURES

    def next(self, tracks, current, history):
        return Nexter_RandomWalk.next(tracks, current, history, self.features)

class Shuffle(RecommendationAgent):
    id = "shuffle"
    name = "Shuffle"
    description = "Any track that was not played recently, at random."

    def next(self, tracks, current, history):
        fresh = [t for t in tracks if t not in history]
        return random.choice(fresh or list(tracks)), "random"

# An album is its name in its folder: compilations stay whole, and same-named albums stay apart.
def albumKey(path, tags):
    return (tags["album"][0], os.path.dirname(path)) if "album" in tags else None

def number(tags, key):
    try:
        return int(tags.get(key, ["0"])[0])
    except ValueError:
        return 0

def albumOrder(tracks, path):
    tags = tracks[path]
    return (number(tags, "discnumber"), number(tags, "tracknumber"), tags["title"][0])

class AlbumJourney(RecommendationAgent):
    id = "album-journey"
    name = "Album journey"
    description = "Plays the current album through in track order, then moves to a related album (same artist, genre or year) from its first track."
    links = [TrackFilter("artist", weight=2), TrackFilter("genre", weight=2), TrackFilter("date")]

    def next(self, tracks, current, history):
        key = albumKey(current, tracks[current])
        if(key is not None):
            following = self.nextOnAlbum(tracks, current, key, history)
            if(following is not None):
                return following, "album"
        # Album finished (or untagged): walk to a track of another album, then start that album.
        others = {t: tags for t, tags in tracks.items() if albumKey(t, tags) != key or t == current}
        if(len(others) <= 1):
            return Shuffle().next(tracks, current, history)
        track, cause = Nexter_RandomWalk.next(others, current, history, self.links)
        if(track == current):
            track, cause = random.choice([t for t in others if t != current]), "random"
        return self.albumStart(tracks, track, history), cause

    def albumTracks(self, tracks, key):
        return sorted((t for t, tags in tracks.items() if albumKey(t, tags) == key), key=lambda t: albumOrder(tracks, t))

    # The next track in album order, skipping recent tracks and other copies of a track already heard
    # (same title, or same disc and track number: an album kept in two formats in one folder).
    def nextOnAlbum(self, tracks, current, key, history):
        heard = [h for h in list(history) + [current] if h in tracks and albumKey(h, tracks[h]) == key]
        titles = {tracks[h]["title"][0] for h in heard}
        positions = {albumOrder(tracks, h)[:2] for h in heard if number(tracks[h], "tracknumber") > 0}
        album = self.albumTracks(tracks, key)
        for t in album[album.index(current) + 1:]:
            if(t not in history and tracks[t]["title"][0] not in titles and albumOrder(tracks, t)[:2] not in positions):
                return t
        return None

    def albumStart(self, tracks, track, history):
        key = albumKey(track, tracks[track])
        if(key is None):
            return track
        fresh = [t for t in self.albumTracks(tracks, key) if t not in history]
        return fresh[0] if fresh else track

class GenreExplorer(RandomWalk):
    id = "genre-explorer"
    name = "Genre explorer"
    description = "Stays in the current genre, moving between its artists, albums and years; now and then drifts via the artist or the year."
    features = [TrackFilter("genre", weight=4),
                TrackFilter("genre", "artist", weight=3),
                TrackFilter("genre", "album", weight=2),
                TrackFilter("genre", "date", weight=2),
                TrackFilter("artist", weight=1),
                TrackFilter("date", weight=1)]

def decade(tags):
    year = tags.get("date", [""])[0][:4]
    return int(year) // 10 * 10 if year.isdigit() else None

class EraExplorer(RecommendationAgent):
    id = "era-explorer"
    name = "Era explorer"
    description = "Stays in the current decade (e.g. the 1970s), preferring another artist each time."
    otherArtistShare = 0.75

    def next(self, tracks, current, history):
        era = decade(tracks[current])
        if(era is None):
            return RandomWalk().next(tracks, current, history)
        sameEra = [t for t in tracks if t not in history and t != current and decade(tracks[t]) == era]
        artists = set(tracks[current].get("artist", []))
        otherArtist = [t for t in sameEra if not(artists & set(tracks[t].get("artist", [])))]
        pool = otherArtist if otherArtist and random.random() < self.otherArtistShare else sameEra
        if not(pool):
            return RandomWalk().next(tracks, current, history)
        return random.choice(pool), "date"

# Needs the audio vectors (AudioFeatures), which the window computes in the background while it is selected.
class SoundAlike(RecommendationAgent):
    id = "sound-alike"
    name = "Sound-alike"
    description = "Picks among the 10 tracks whose sound (timbre, harmony, tempo…) is closest to the current one. Each track's audio is analysed once, in the background."
    topN = 10
    needsAudioVectors = True

    def __init__(self):
        self.paths = []
        self.index = {}
        self.matrix = None

    def setVectors(self, vectors):
        import numpy
        vectors = {p: v for p, v in vectors.items() if v is not None}  # None: could not be analysed
        self.paths = list(vectors)
        self.index = {p: i for i, p in enumerate(self.paths)}
        if not(self.paths):
            self.matrix = None
            return
        m = numpy.array([vectors[p] for p in self.paths], dtype="float64")
        m = (m - m.mean(axis=0)) / (m.std(axis=0) + 1e-9)  # every feature weighs the same
        self.matrix = m / (numpy.linalg.norm(m, axis=1, keepdims=True) + 1e-9)  # rows . row = cosine similarity

    # The n analysed tracks most similar to `current`, skipping recent tracks and other copies of the same song.
    def similar(self, tracks, current, history, n):
        import numpy
        avoid = set(history) | {current}
        titles = {tracks[t]["title"][0] for t in avoid if t in tracks}
        scores = self.matrix @ self.matrix[self.index[current]]
        found = []
        for i in numpy.argsort(-scores):
            t = self.paths[i]
            if(t in tracks and t not in avoid and tracks[t]["title"][0] not in titles):
                found.append(t)
                if(len(found) == n):
                    break
        return found

    def next(self, tracks, current, history):
        if(self.matrix is None or current not in self.index):
            return RandomWalk().next(tracks, current, history)  # not analysed yet
        candidates = self.similar(tracks, current, history, self.topN)
        if not(candidates):
            return RandomWalk().next(tracks, current, history)
        return random.choice(candidates), "sound"

AGENTS = [RandomWalk(), Shuffle(), AlbumJourney(), GenreExplorer(), EraExplorer(), SoundAlike()]

def byId(agentId):
    return next((a for a in AGENTS if a.id == agentId), AGENTS[0])
