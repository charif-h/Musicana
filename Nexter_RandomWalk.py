import random
# Random
# Year
# Decade
# Album

# Artist
# Artist --group by--> Album

#genre
# genre --group by--> Album
# genre --group by--> Artist
# genre --group by--> Year
# genre --group by--> Decade

class TrackFilter():
    def __init__(self, feature, groupBy="", weight=1):
        self.feature = feature
        self.groupBy = groupBy
        self.weight = weight

    def filter(self, tracks, feature, featureVal, history=()):
        filteredTracks = {}
        for t in tracks:
            if (t not in history):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                if (len(intersection(c, featureVal)) > 0):
                    filteredTracks[t] = tracks[t]
        return filteredTracks

    # Returns (next track, cause): cause is the shared feature, or "random" on fallback.
    def getNext(self, tracks, track, history):
        if (self.feature in tracks[track].keys()):
            val = tracks[track][self.feature]
            filteredTracks = self.filter(tracks, self.feature, val, history)

            if(len(filteredTracks) > 0):
                if(self.groupBy != ""):
                    groupedSet = set()
                    for t in filteredTracks:
                        if(self.groupBy in filteredTracks[t].keys()):
                            groupedSet |= set(filteredTracks[t][self.groupBy])
                    print(groupedSet)
                    if(len(groupedSet) > 0):
                        choice = [random.choice(list(groupedSet))]
                        groupedfilteredTracks = self.filter(filteredTracks, self.groupBy, choice)
                        return random.choice(list(groupedfilteredTracks.keys())), self.feature
                    else:
                        return random.choice(list(filteredTracks.keys())), self.feature
                else:
                    return random.choice(list(filteredTracks.keys())), self.feature
            else:
                return nextIsRandom(tracks)
        else:
            return nextIsRandom(tracks)

    def __str__(self):
        return self.feature + "." + self.groupBy

# The feature linking two tracks is drawn with these weights (album used to be listed twice).
FEATURES = [TrackFilter("date"),
            TrackFilter("album", weight=2),
            TrackFilter("artist"), TrackFilter("composer"),
            TrackFilter("artist", "album"),
            TrackFilter("artist", "date"),
            TrackFilter("genre"),
            TrackFilter("genre", "album"),
            TrackFilter("genre", "artist"),
            TrackFilter("genre", "date"),
]

def next(tracks, track, history, features=FEATURES):
    feature = random.choices(features, weights=[f.weight for f in features])[0]
    print(feature, end=" ")
    if(track is None):
        print(feature, "is none")
        return nextIsRandom(tracks)
    else:
        return feature.getNext(tracks, track, history)

def nextIsRandom(tracks):
    print("random")
    return random.choice(list(tracks.keys())), "random"

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))
