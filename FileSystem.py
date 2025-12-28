"""
File system utilities for scanning and filtering MP3 music libraries.

This module handles loading MP3 files from a directory tree, extracting
their metadata (ID3 tags), and filtering tracks based on search criteria.
"""

import glob
from mutagen.easyid3 import EasyID3
from collections import defaultdict


def def_value():
    """Default value factory for defaultdict to return empty string list."""
    return [""]


# Register 'comment' as a valid ID3 text key for EasyID3
EasyID3.RegisterTextKey('comment', 'COMM')
def getAllMp3(path, v=None):
    """
    Scan a directory tree for MP3 files and extract their metadata.
    
    Args:
        path (str): Root directory path to scan for MP3 files
        v (optional): Variable for progress updates (currently unused in implementation)
        
    Returns:
        defaultdict: Dictionary mapping file paths to their ID3 metadata
    """
    tracks = defaultdict(def_value)
    
    # Count total files for progress tracking
    Nb = len(list(glob.iglob(path + '**/*.mp3', recursive=True)))
    print("Loading tracks :")
    
    i = 0
    percent = "00%"
    print(percent, end="")
    
    # Recursively find all MP3 files
    for filename in glob.iglob(path + '**/*.mp3', recursive=True):
        # Ensure UTF-8 encoding for filenames
        fn = filename.encode("utf-8", "ignore").decode("utf-8")
        
        for f in glob.glob(fn):
            mp3info = getMp3Info(f)
            tracks[fn] = mp3info

            # Update progress percentage
            percent = str(int(100 * i / Nb)) + "%"
            if v is None:
                print("\b" * (1 + len(percent)), end="")
                print(percent, end="")
            else:
                v = percent
            i += 1

    if v is None:
        print("\b" * (1 + len(percent)), "100%...LOADED ", len(tracks))
    else:
        v = "\b" * (1 + len(percent)) + "100%...LOADED " + len(tracks)
    
    return tracks

def filterTracks(tracks, v):
    """
    Filter tracks based on a search string.
    
    Searches for the filter string in all metadata fields of each track.
    Case-insensitive search.
    
    Args:
        tracks (dict): Dictionary of tracks to filter
        v (str): Search/filter string
        
    Returns:
        dict: Filtered tracks matching the search criteria, or all tracks if no matches
    """
    newDict = dict()
    
    # Search for filter string in track metadata
    for (key, value) in tracks.items():
        if str(value).lower().find(str(v).lower()) >= 0:
            newDict[key] = value
    
    if len(newDict) > 0:
        print(len(newDict), " tracks compatible with the filter ", v)
        return newDict
    else:
        print("No compatible tracks with the filter ", v)
        return tracks

def getMp3Info(mp3FileName):
    """
    Extract and normalize ID3 metadata from an MP3 file.
    
    Converts tag values to lowercase and splits them on common separator
    characters to create lists. This allows for multi-value tags like
    multiple artists or genres.
    
    Args:
        mp3FileName (str): Path to the MP3 file
        
    Returns:
        EasyID3: Normalized metadata with tag values as lists
    """
    mp3info = EasyID3(mp3FileName)
    
    # Common separators used in ID3 tags
    symbols = ["/", ",", "&", " ;", "; "]
    
    # Normalize each tag: lowercase and split on separators
    for f in mp3info.keys():
        txt = mp3info[f][0].lower()
        
        # Replace all separators with semicolon
        for s in symbols:
            txt = txt.replace(s, ";")
        
        # Split into list of values
        mp3info[f] = txt.split(";")
    
    return mp3info