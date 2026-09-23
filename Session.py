import random
from collections import deque

import Agents
import FileSystem
import Nexter_RandomWalk

class PlayerSession():
    def __init__(self, tracks, commentator=None, historySize=20, agent=None):
        self.tracks = tracks
        self.history = deque(maxlen=historySize)  # recently played, excluded from next()
        self.current = None
        self.commentator = commentator
        self.agent = agent or Agents.AGENTS[0]  # the recommendation agent that picks the next track

    # Returns None, keeping the current track, when nothing matches the filter.
    def start(self, filter=""):
        filteredTracks = FileSystem.filterTracks(self.tracks, filter)
        if(len(filteredTracks) == 0):
            return None
        self.setCurrent(random.choice(list(filteredTracks)))
        return self.current

    # next(), random() and moveTo() call onDone() exactly once, when the transition has been announced.
    def next(self, onDone=None):
        if(self.current is None):
            track = self.start()
            if(onDone is not None):
                onDone()
            return track
        track, cause = self.agent.next(self.tracks, self.current, self.history)
        return self.moveTo(track, cause, onDone)

    def random(self, onDone=None):
        if(len(self.tracks) == 0):
            if(onDone is not None):
                onDone()
            return None
        track, cause = Nexter_RandomWalk.nextIsRandom(self.tracks)
        return self.moveTo(track, cause, onDone)

    # A track the user picked: no transition to announce.
    def select(self, track):
        self.setCurrent(track)
        return track

    def moveTo(self, track, cause, onDone=None):
        previous = self.current
        self.setCurrent(track)
        if(self.commentator is not None and previous is not None):
            self.commentator.transition(self.tracks[previous], self.tracks[track], cause, onDone)
        elif(onDone is not None):
            onDone()
        return track

    def setCurrent(self, track):
        self.current = track
        self.history.append(track)
