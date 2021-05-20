from mutagen.mp3 import MP3
import queue
import pygame
import time
import math
import random
import FileSystem
import Comentateur
import mutagen.mp3


def printime(l):
    m = math.floor(l/60)
    s = math.floor(l%60)
    return str(m).zfill(2)  + ":" + str(s).zfill(2)

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def next(track, noHistory):
    #features = ['random', 'date', 'album', 'album', 'artist', 'artist', 'artist', 'genre', 'genre', "genre"]
    features = ['date', 'album', 'album', 'artist', 'artist', 'artist', 'genre', 'genre', "genre", "comment"]
    feature = random.choice(features)
    print(feature, end="")
    if(feature == 'random'):
        print()
        return nextIsRandom(tracks)
    else:
        val = ""
        if(feature in tracks[track].keys()):
            val = tracks[track][feature]
        else:
            return nextIsRandom(tracks, track)
        print(": ", val)
        '''txt = "Nous restons avec le même " + feature
        for v in val:
            txt += " " + v
        engine.say(txt)
        engine.runAndWait()'''
        paths = []
        for t in tracks:
            if(t not in list(noHistory.queue)):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                if(len(intersection(c, val)) > 0):
                    paths.append(t)
        if(len(paths) == 0):
            return nextIsRandom(tracks, track)

        ret = random.choice(paths)

        Nadia.transition(tracks[track], tracks[ret], feature)
        return ret

def nextIsRandom(tracks, track):
    print("random")
    ret = random.choice(list(tracks.keys()))
    Nadia.transition(tracks[track], tracks[ret], "random")
    return ret

def printrack(track, trackleng = 0.0):
    print('title:\t', track['title'][0], "\t[", printime(trackleng), ']')
    F = ["album", "artist", "composer", "albumartist", "genre", "date", "comment"]
    for f in track.keys():
        if(f in track.keys()):
            print(f, ": ", track[f])

def play(track):
    song = MP3(track)

    print("---------------------------------")
    if (noHistory.full()):
        noHistory.get()
    noHistory.put(track)
    printrack(tracks[track], song.info.length)
    print(track)
    print("---------------------------------")

    # speed
    mp3 = mutagen.mp3.MP3(track)
    pygame.mixer.init(frequency=mp3.info.sample_rate)
    pygame.mixer.music.load(track)
    pygame.mixer.music.play()

#=======================================================================================================================
#root = Tk() # creates an Empty window
#root.minsize(300,300) # set size as 300 x 300 wide, Change this accordingly

from Windelphi import Application as App


Nadia = Comentateur.Commentator()
app = App()

noHistory = queue.Queue(maxsize=20)
path = 'D:/Music/'
tracks = FileSystem.getAllMp3(path)
pygame.mixer.init()


#track = random.choice(list(tracks.keys()))
Nadia.say("Hello, Any filter to start from? : ")
filter = input("")
filtered_tracks = FileSystem.filterTracks(tracks, filter).keys()
track = random.choice(list(filtered_tracks))
Nadia.welcome(tracks[track]['title'][0], filter)

for i in range(300):

    song = MP3(track)

    print("---------------------------------")
    if (noHistory.full()):
        noHistory.get()
    noHistory.put(track)
    printrack(tracks[track], song.info.length)
    print(track)
    print("---------------------------------")

    #speed
    mp3 = mutagen.mp3.MP3(track)
    pygame.mixer.init(frequency=mp3.info.sample_rate)

    pygame.mixer.music.load(track)
    #v = StringVar()
    #songlabel = Label(root, textvariable=v, width=35)
    #v.set(tracks[track]['title'][0])
    pygame.mixer.music.play()
    #songlabel.pack()
    #root.mainloop()

    prog = 0
    print(printime(song.info.length - prog), "|", end="")
    while pygame.mixer.music.get_busy():
        time.sleep(1)
        #if(prog % 10 == 0):
        print("\b\b\b\b\b\b\b", end="")
        print(printime(song.info.length - prog), "|", end="")
        prog += 1
    print("*"*i)
    print(i, ") ", end="")
    track = next(track, noHistory)