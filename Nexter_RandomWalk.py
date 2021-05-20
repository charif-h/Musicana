import random
import queue
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

    def filter(self, tracks, feature, featureVal, noHistory = queue.Queue(maxsize=20)):
        filteredTracks = {}
        for t in tracks:
            if (t not in list(noHistory.queue)):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                if (len(intersection(c, featureVal)) > 0):
                    filteredTracks[t] = tracks[t]
        #print(filteredTracks)
        return filteredTracks

    def getNext(self, tracks, track, noHistory):
        if (self.feature in tracks[track].keys()):
            val = tracks[track][self.feature]
            filteredTracks = self.filter(tracks, self.feature, val, noHistory)

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
                        return random.choice(list(groupedfilteredTracks.keys()))
                    else:
                        return random.choice(list(filteredTracks.keys()))
                else:
                    return random.choice(list(filteredTracks.keys()))
            else:
                return nextIsRandom(tracks)
        else:
            return nextIsRandom(tracks)

    def __str__(self):
        return self.feature + "." + self.groupBy

def next(tracks, track, noHistory):
    features = [ TrackFilter("date"),
          TrackFilter("album"), TrackFilter("album"),
          TrackFilter("artist"), TrackFilter("composer"),
          TrackFilter("artist", "album"),
          TrackFilter("artist", "date"),
          TrackFilter("genre"),
          TrackFilter("genre", "album"),
          TrackFilter("genre", "artist"),
          TrackFilter("genre", "date"),
    ]
    #features = ['date', 'album', 'album', 'album', 'artist', 'artist', 'artist', 'genre', 'genre', "genre", "comment"]
    feature = random.choice(features)
    print(feature, end=" ")
    if(feature == 'random'):
        print()
        return nextIsRandom(tracks)
    elif(track is None):
        print(feature, "is none")
        return nextIsRandom(tracks)
    else:
        return feature.getNext(tracks, track, noHistory)
        '''val = ""
        if(feature in tracks[track].keys()):
            val = tracks[track][feature]
        else:
            return nextIsRandom(tracks)
        print(": ", val)
        paths = []
        for t in tracks:
            if(t not in list(noHistory.queue)):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                if(len(intersection(c, val)) > 0):
                    paths.append(t)
        if(len(paths) == 0):
            return nextIsRandom(tracks)

        ret = random.choice(paths)

        #Nadia.transition(tracks[track], tracks[ret], feature)
        return ret'''

def nextIsRandom(tracks):
    print("random")
    ret = random.choice(list(tracks.keys()))
    #Nadia.transition(tracks[track], tracks[ret], "random")
    return ret

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))