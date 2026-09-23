from mutagen.mp3 import MP3
import queue
import pygame
import time
import math
import random
import FileSystem
import Comentateur
import Nexter_RandomWalk
import mutagen.mp3


def printime(l):
    m = math.floor(l/60)
    s = math.floor(l%60)
    return str(m).zfill(2)  + ":" + str(s).zfill(2)

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
path = 'C:\\Users\\chari\\Documents\\D\\Music/'
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
    previous = track
    track, cause = Nexter_RandomWalk.next(tracks, track, list(noHistory.queue))
    Nadia.transition(tracks[previous], tracks[track], cause)