"""
Command-line music player with intelligent track selection.

This is a CLI version of Musicana that plays tracks using metadata-based
recommendations and provides text-to-speech commentary.
"""

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
    """
    Convert seconds to MM:SS time format.
    
    Args:
        l (float): Time in seconds
        
    Returns:
        str: Formatted time string (MM:SS)
    """
    m = math.floor(l / 60)
    s = math.floor(l % 60)
    return str(m).zfill(2) + ":" + str(s).zfill(2)


def intersection(lst1, lst2):
    """
    Find common elements between two lists.
    
    Args:
        lst1 (list): First list
        lst2 (list): Second list
        
    Returns:
        list: Elements present in both lists
    """
    return list(set(lst1) & set(lst2))


def next(track, noHistory):
    """
    Select next track based on metadata similarity.
    
    Args:
        track (str): Current track path
        noHistory (Queue): Recently played tracks to avoid
        
    Returns:
        str: Path to next track
    """
    features = ['date', 'album', 'album', 'artist', 'artist', 'artist', 'genre', 'genre', "genre", "comment"]
    feature = random.choice(features)
    print(feature, end="")
    
    if feature == 'random':
        print()
        return nextIsRandom(tracks)
    else:
        val = ""
        if feature in tracks[track].keys():
            val = tracks[track][feature]
        else:
            return nextIsRandom(tracks, track)
        print(": ", val)
        
        # Find tracks with matching feature values
        paths = []
        for t in tracks:
            if t not in list(noHistory.queue):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                if len(intersection(c, val)) > 0:
                    paths.append(t)
        
        if len(paths) == 0:
            return nextIsRandom(tracks, track)

        ret = random.choice(paths)
        Nadia.transition(tracks[track], tracks[ret], feature)
        return ret


def nextIsRandom(tracks, track):
    """
    Select a random track.
    
    Args:
        tracks (dict): All available tracks
        track (str): Current track path
        
    Returns:
        str: Path to randomly selected track
    """
    print("random")
    ret = random.choice(list(tracks.keys()))
    Nadia.transition(tracks[track], tracks[ret], "random")
    return ret


def printrack(track, trackleng=0.0):
    """
    Print track information to console.
    
    Args:
        track (dict): Track metadata
        trackleng (float): Track length in seconds
    """
    print('title:\t', track['title'][0], "\t[", printime(trackleng), ']')
    
    for f in track.keys():
        print(f, ": ", track[f])


def play(track):
    """
    Play a track (setup and display info).
    
    Args:
        track (str): Path to the track to play
    """
    song = MP3(track)

    print("---------------------------------")
    
    # Add to history queue
    if noHistory.full():
        noHistory.get()
    noHistory.put(track)
    
    printrack(tracks[track], song.info.length)
    print(track)
    print("---------------------------------")

    # Initialize mixer with correct sample rate
    mp3 = mutagen.mp3.MP3(track)
    pygame.mixer.init(frequency=mp3.info.sample_rate)
    pygame.mixer.music.load(track)
    pygame.mixer.music.play()


# =======================================================================================================================
# Main execution
# =======================================================================================================================

from Windelphi import Application as App

# Initialize components
Nadia = Comentateur.Commentator()
app = App()

noHistory = queue.Queue(maxsize=20)
path = 'C:/Music'
tracks = FileSystem.getAllMp3(path)
pygame.mixer.init()

# Get initial filter from user
Nadia.say("Hello, Any filter to start from? : ")
filter = input("")
filtered_tracks = FileSystem.filterTracks(tracks, filter).keys()
track = random.choice(list(filtered_tracks))
Nadia.welcome(tracks[track]['title'][0], filter)

# Play loop
for i in range(300):
    song = MP3(track)

    print("---------------------------------")
    
    # Update history
    if noHistory.full():
        noHistory.get()
    noHistory.put(track)
    
    printrack(tracks[track], song.info.length)
    print(track)
    print("---------------------------------")

    # Initialize and play with correct sample rate
    mp3 = mutagen.mp3.MP3(track)
    pygame.mixer.init(frequency=mp3.info.sample_rate)
    pygame.mixer.music.load(track)
    pygame.mixer.music.play()

    # Progress display
    prog = 0
    print(printime(song.info.length - prog), "|", end="")
    
    while pygame.mixer.music.get_busy():
        time.sleep(1)
        print("\b\b\b\b\b\b\b", end="")
        print(printime(song.info.length - prog), "|", end="")
        prog += 1
    
    print("*" * i)
    print(i, ") ", end="")
    track = next(track, noHistory)