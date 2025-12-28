"""
Text-to-speech commentator for track transitions.

This module provides voice announcements for track changes and transitions,
similar to a radio DJ introducing songs. It includes transliteration of
Arabic characters for better text-to-speech pronunciation.
"""

import tkinter
import pyttsx3


def safe(a):
    """
    Transliterate Arabic characters to Latin alphabet.
    
    This ensures better pronunciation by the text-to-speech engine.
    
    Args:
        a (str or None): Text that may contain Arabic characters
        
    Returns:
        str: Transliterated text or empty string if input is None
    """
    if a is None:
        return ""
    else:
        # Arabic to Latin transliteration map
        rep = {
            "ا": "a", "أ": "a", "إ": "a", "آ": "a", "ى": "a", "ء": "a",
            "ب": "b", "ت": "t", "ث": "th",
            "ج": "j", "ح": "h", "خ": "kh",
            "د": "d", "ذ": "z", "ر": "r", "ز": "z",
            "س": "ss", "ش": "sh", "ص": "s", "ض": "dh",
            "ط": "t", "ظ": "z", "ع": "a", "غ": "gh",
            "ف": "f", "ق": "qu", "ك": "k", "ل": "l",
            "م": "m", "ن": "n", "ه": "h", "و": "ou", "ي": "y", "ة": "a", "ئ": "i"
        }

        for k in rep.keys():
            a = str(a).replace(k, rep[k])
        return a


class Commentator:
    """
    Voice commentator for announcing track transitions.
    
    Uses pyttsx3 (Windows SAPI) to provide spoken announcements about
    tracks being played and the reasoning behind track selection.
    """
    
    def __init__(self):
        """Initialize the text-to-speech engine with English voice."""
        en_voice_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
        self.engine = pyttsx3.init(driverName='sapi5')
        self.display = None  # Optional label widget for text display
        self.engine.setProperty('voice', en_voice_id)
        self.engine.setProperty('rate', 150)

    def transition(self, t1, t2, cause):
        """
        Announce transition between two tracks.
        
        Creates contextual announcements based on the reason for the transition
        (same album, artist, genre, date, or random).
        
        Args:
            t1 (dict): Metadata of the previous track
            t2 (dict): Metadata of the next track
            cause (str): Reason for transition ('album', 'artist', 'genre', 'date', or 'random')
        """
        if cause == "album":
            self.say("We leave you with the title " + safe(t2['title'][0]) + 
                    " from the same album " + safe(t1['album'][0]))
        elif cause == "artist":
            self.say("We keep going with the same artist " + safe(t1['artist'][0]) + 
                    ", we listen to the title " + safe(t2['title'][0]))
        elif cause == "genre":
            if safe(t1['album'][0]) == safe(t2['album'][0]):
                self.say("Within the same ambience of the music " + str(safe(t1['genre'])) + 
                        ", we invite you to admire the title " + safe(t2['title'][0]))
            elif safe(t1['artist'][0]) == safe(t2['artist'][0]):
                self.say("Within the same ambience of the artist " + safe(t2['artist'][0]) + 
                        ", and his music " + str(safe(t1['genre'])) + 
                        " we propose to you the title " + safe(t2['title'][0]))
            else:
                self.say("We continue with the same pace of music " + str(safe(t2['genre'])) + 
                        " we present for you the artist " + safe(t2['artist'][0]) + 
                        ", through his title " + safe(t2['title'][0]))
        elif cause == "date":
            if safe(t1['album'][0]) == safe(t2['album'][0]):
                self.say("Another title from the same album " + safe(t2['album'][0]) + 
                        ", of the year " + safe(t2['date'][0]) + 
                        ", we listen to the title " + safe(t2['title'][0]))
            elif safe(t1['artist'][0]) == safe(t2['artist'][0]):
                self.say(safe(t2['date'][0]) + " was a rich year for the artist " + 
                        safe(t2['artist'][0]) + 
                        ", so listen with us to his title " + safe(t2['title'][0]) + 
                        " from the same year.")
            else:
                self.say("We will stay in the ambience of the year " + safe(t2['date'][0]) + 
                        ", but with another artist, so allow us to present to you " + 
                        safe(t2['title'][0]) + " of " + safe(t2['artist'][0]))
        else:
            self.say("It is time to change, listen with us to " + safe(t2['title'][0]))

    def say(self, txt):
        """
        Speak the given text and optionally display it.
        
        Args:
            txt (str): Text to speak
        """
        self.Display(txt)
        self.engine.say(safe(txt))
        self.engine.runAndWait()

    def welcome(self, title="", filter=""):
        """
        Announce welcome message when starting playback.
        
        Args:
            title (str): Title of the first track
            filter (str): Optional filter criteria used
        """
        filtext = ""
        if len(filter) * len(title) > 0:
            filtext = "according to your demand " + filter
        self.say("welcome, " + filtext + " we will start our program with the track " + title)

    def Display(self, txt):
        """
        Display text in the UI if a display widget is set.
        
        Args:
            txt (str): Text to display
        """
        if isinstance(self.display, tkinter.Label):
            self.display.text = txt
        else:
            print(txt)