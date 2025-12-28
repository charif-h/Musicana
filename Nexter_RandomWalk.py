"""
Smart track recommendation algorithm using metadata-based random walk.

This module implements an intelligent "next track" selection algorithm that
chooses tracks based on metadata similarity (artist, album, genre, date, etc.)
while avoiding recently played tracks.
"""

import random
import queue


class TrackFilter():
    """
    A filter for selecting tracks based on metadata features.
    
    This class encapsulates a recommendation strategy that selects tracks
    sharing specific metadata attributes, optionally grouped by another attribute.
    """
    
    def __init__(self, feature, groupBy="", weight=1):
        """
        Initialize a track filter.
        
        Args:
            feature (str): Primary metadata field to match (e.g., 'artist', 'genre', 'album')
            groupBy (str): Optional secondary field to group results by
            weight (int): Weight for this filter in selection (currently unused)
        """
        self.feature = feature
        self.groupBy = groupBy
        self.weight = weight

    def filter(self, tracks, feature, featureVal, noHistory=queue.Queue(maxsize=20)):
        """
        Filter tracks by a specific metadata feature value.
        
        Args:
            tracks (dict): All available tracks
            feature (str): Metadata field to filter on
            featureVal (list): Values to match
            noHistory (Queue): Recently played tracks to exclude
            
        Returns:
            dict: Filtered tracks matching the criteria
        """
        filteredTracks = {}
        
        for t in tracks:
            # Skip recently played tracks
            if t not in list(noHistory.queue):
                c = tracks[t][feature] if feature in tracks[t].keys() else []
                
                # Check if there's any overlap between track's values and target values
                if len(intersection(c, featureVal)) > 0:
                    filteredTracks[t] = tracks[t]
        
        return filteredTracks

    def getNext(self, tracks, track, noHistory):
        """
        Get the next track using this filter's strategy.
        
        Args:
            tracks (dict): All available tracks
            track (str): Current track path
            noHistory (Queue): Recently played tracks to exclude
            
        Returns:
            str: Path to the selected next track
        """
        if self.feature in tracks[track].keys():
            val = tracks[track][self.feature]
            filteredTracks = self.filter(tracks, self.feature, val, noHistory)

            if len(filteredTracks) > 0:
                # If groupBy is specified, further filter by a random group value
                if self.groupBy != "":
                    groupedSet = set()
                    
                    # Collect all unique values of the groupBy field
                    for t in filteredTracks:
                        if self.groupBy in filteredTracks[t].keys():
                            groupedSet |= set(filteredTracks[t][self.groupBy])
                    
                    if len(groupedSet) > 0:
                        # Pick a random group value and filter to that group
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
        """String representation showing the filter strategy."""
        return self.feature + "." + self.groupBy


def next(tracks, track, noHistory):
    """
    Select the next track using a randomly chosen recommendation strategy.
    
    The function picks from multiple strategies with different metadata-based
    approaches to create varied and interesting track transitions.
    
    Strategies include:
    - Same date/year
    - Same album
    - Same artist
    - Same artist, different album
    - Same artist, different date
    - Same composer
    - Same genre
    - Same genre, different album/artist/date
    
    Args:
        tracks (dict): All available tracks
        track (str): Current track path
        noHistory (Queue): Recently played tracks to avoid
        
    Returns:
        str: Path to the next track to play
    """
    # Define weighted collection of recommendation strategies
    features = [
        TrackFilter("date"),
        TrackFilter("album"), TrackFilter("album"),  # Higher weight for album continuity
        TrackFilter("artist"), TrackFilter("composer"),
        TrackFilter("artist", "album"),  # Same artist, different album
        TrackFilter("artist", "date"),   # Same artist, different era
        TrackFilter("genre"),
        TrackFilter("genre", "album"),   # Same genre, different album
        TrackFilter("genre", "artist"),  # Same genre, different artist
        TrackFilter("genre", "date"),    # Same genre, different time period
    ]
    
    # Randomly select a recommendation strategy
    feature = random.choice(features)
    print(feature, end=" ")
    
    if feature == 'random':
        print()
        return nextIsRandom(tracks)
    elif track is None:
        print(feature, "is none")
        return nextIsRandom(tracks)
    else:
        return feature.getNext(tracks, track, noHistory)


def nextIsRandom(tracks):
    """
    Select a completely random track.
    
    Used as a fallback when no metadata-based match can be found.
    
    Args:
        tracks (dict): All available tracks
        
    Returns:
        str: Path to a randomly selected track
    """
    print("random")
    ret = random.choice(list(tracks.keys()))
    return ret


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