import random
from collections import deque

import FileSystem
import Nexter_RandomWalk

class PlayerSession():
    def __init__(self, tracks, commentator=None, historySize=20):
        self.tracks = tracks
        self.history = deque(maxlen=historySize)  # recently played, excluded from next()
        self.current = None
        self.commentator = commentator

    # Returns None, keeping the current track, when nothing matches the filter.
    def start(self, filter=""):
        filteredTracks = FileSystem.filterTracks(self.tracks, filter)
        if(len(filteredTracks) == 0):
            return None
        self.setCurrent(random.choice(list(filteredTracks)))
        return self.current

    def next(self):
        if(self.current is None):
            return self.start()
        track, cause = Nexter_RandomWalk.next(self.tracks, self.current, self.history)
        return self.moveTo(track, cause)

    def random(self):
        if(len(self.tracks) == 0):
            return None
        track, cause = Nexter_RandomWalk.nextIsRandom(self.tracks)
        return self.moveTo(track, cause)

    def moveTo(self, track, cause):
        previous = self.current
        self.setCurrent(track)
        if(self.commentator is not None and previous is not None):
            self.commentator.transition(self.tracks[previous], self.tracks[track], cause)
        return track

    def setCurrent(self, track):
        self.current = track
        self.history.append(track)
