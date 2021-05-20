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

class Commentator:
    def __init__(self):
        en_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        self.engine = pyttsx3.init(driverName='sapi5')
        self.display = None
        self.engine.setProperty('voice', en_voice_id)
        self.engine.setProperty('rate', 150)

    def transition(self, t1, t2, cause):
        if(cause == "album"):
            self.say("We leave you with the title " + safe(t2['title'][0]) + " from the same album " + safe(t1['album'][0]))
        elif(cause == "artist"):
            self.say("We keep going with the same artist " + safe(t1['artist'][0]) + ", we listen to the title " + safe(t2['title'][0]))
        elif (cause == "genre"):
            if(safe(t1['album'][0]) == safe(t2['album'][0])):
                self.say("Within the same ambience of the music " + str(safe(t1['genre'])) + ", we invite you to admire the title " + safe(t2['title'][0]))
            elif(safe(t1['artist'][0]) == safe(t2['artist'][0])):
                self.say("Within the same ambience of the artist " + safe(t2['artist'][0]) + ", and his music " + str(safe(t1['genre'])) + " we propose to you the title " + safe(t2['title'][0]))
            else:
                self.say("We continue with the same pace of music " + str(safe(t2['genre'])) + " we present for you the artist " + safe(t2['artist'][0]) + ", through his title " + safe(t2['title'][0]))
        elif (cause == "date"):
            if (safe(t1['album'][0]) == safe(t2['album'][0])):
                self.say("Another title from the same albume " + safe(t2['album'][0]) + ", of the year " + safe(t2['date'][0]) + ", we listen to the title " + safe(t2['title'][0]))
            elif (safe(t1['artist'][0]) == safe(t2['artist'][0])):
                self.say(safe(t2['date'][0]) + " was a rech year for the artist " + safe(t2['artist'][0]) + ", so listen with us to his title " + safe(t2['title'][0]) + " from the same year.")
            else:
                self.say("We will stay in the ambience of the year " + safe(t2['date'][0]) + ", but with anothe artist, so allow us to present to you " + safe(t2['title'][0]) + " of " + safe(t2['artist'][0]))
        else:
            self.say("It is time to change, listen with use to " + safe(t2['title'][0]))

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
        if isinstance(self.display, tkinter.Label):
            self.display.text = txt
        else:
            print(txt)