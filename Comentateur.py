import tkinter

import pyttsx3

def safe(a):
    if (a is None):
        return ""
    else:
        rep = {"ا":"a", "أ":"a", "إ":"a", "آ":"a", "ى":"a", "ء":"a",
               "ب":"b", "ت":"t", "ث":"th",
               "ج":"j", "ح":"h", "خ":"kh",
               "د":"d", "ذ":"z", "ر":"r", "ز":"z",
               "س":"ss", "ش":"sh", "ص":"s", "ض":"dh",
               "ط":"t", "ظ":"z", "ع":"a", "غ":"gh",
               "ف":"f", "ق":"qu", "ك":"k", "ل":"l",
               "م":"m", "ن":"n", "ه":"h", "و":"ou", "ي":"y", "ة":"a", "ئ":"i"}

        for k in rep.keys():
            a = str(a).replace(k, rep[k])
        return a

def first(track, key):
    return safe(track[key][0]) if key in track else ""

class Commentator:
    def __init__(self):
        en_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        self.engine = pyttsx3.init(driverName='sapi5')
        self.display = None
        self.engine.setProperty('voice', en_voice_id)
        self.engine.setProperty('rate', 150)

    def transition(self, t1, t2, cause):
        if(cause == "album"):
            self.say("We leave you with the title " + first(t2, 'title') + " from the same album " + first(t1, 'album'))
        elif(cause == "artist"):
            self.say("We keep going with the same artist " + first(t1, 'artist') + ", we listen to the title " + first(t2, 'title'))
        elif (cause == "genre"):
            if(first(t1, 'album') == first(t2, 'album')):
                self.say("Within the same ambience of the music " + first(t1, 'genre') + ", we invite you to admire the title " + first(t2, 'title'))
            elif(first(t1, 'artist') == first(t2, 'artist')):
                self.say("Within the same ambience of the artist " + first(t2, 'artist') + ", and his music " + first(t1, 'genre') + " we propose to you the title " + first(t2, 'title'))
            else:
                self.say("We continue with the same pace of music " + first(t2, 'genre') + " we present for you the artist " + first(t2, 'artist') + ", through his title " + first(t2, 'title'))
        elif (cause == "date"):
            if (first(t1, 'album') == first(t2, 'album')):
                self.say("Another title from the same albume " + first(t2, 'album') + ", of the year " + first(t2, 'date') + ", we listen to the title " + first(t2, 'title'))
            elif (first(t1, 'artist') == first(t2, 'artist')):
                self.say(first(t2, 'date') + " was a rech year for the artist " + first(t2, 'artist') + ", so listen with us to his title " + first(t2, 'title') + " from the same year.")
            else:
                self.say("We will stay in the ambience of the year " + first(t2, 'date') + ", but with anothe artist, so allow us to present to you " + first(t2, 'title') + " of " + first(t2, 'artist'))
        else:
            self.say("It is time to change, listen with use to " + first(t2, 'title'))

    def say(self, txt):
        self.Display(txt)
        self.engine.say(safe(txt))
        self.engine.runAndWait()

    def welcome(self, title = "", filter = ""):
        filtext = ""
        if (len(filter) * len(title) > 0):
            filtext = "according to your demand " + filter
        self.say("welcome, " + filtext + " we will start our program with the track " + title)

    def Display(self, txt):
        if callable(self.display):
            self.display(txt)
        elif isinstance(self.display, tkinter.Label):
            self.display.configure(text=txt)
        else:
            print(txt)