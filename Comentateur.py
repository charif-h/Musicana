import queue
import threading

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

SVSF_ASYNC = 1
SVSF_PURGE = 2
VOICE = "Zira"
RATE = 2  # SAPI's -10..10 scale; about 150 words per minute

# Speaks through Windows SAPI on its own thread so the UI never waits: say() returns at once and
# onDone() is called (from the speech thread) once the text is spoken, cut by cancel(), or could not be spoken.
class Commentator:
    def __init__(self):
        self.display = None
        self.enabled = True  # when False, say() is silent and finishes at once
        self.requests = queue.Queue()
        self.generation = 0  # bumped by cancel(): older requests are dropped or cut short
        self.thread = threading.Thread(target=self.speakLoop, name="Commentator", daemon=True)
        self.thread.start()

    def speakLoop(self):
        voice = None
        try:
            import comtypes
            import comtypes.client
            comtypes.CoInitialize()  # SAPI is COM: the voice must be created and used on this thread
            voice = comtypes.client.CreateObject("SAPI.SpVoice")
            tokens = voice.GetVoices()
            for i in range(tokens.Count):
                if(VOICE in tokens.Item(i).GetDescription()):
                    voice.Voice = tokens.Item(i)
            voice.Rate = RATE
        except Exception as e:
            print("Text-to-speech unavailable, continuing silently:", e)
        while True:
            txt, generation, onDone = self.requests.get()
            if(txt is None):
                return
            if(voice is not None and generation == self.generation):
                try:
                    voice.Speak(safe(txt), SVSF_ASYNC)
                    purged = False
                    while not(voice.WaitUntilDone(50)):
                        if(generation != self.generation and not purged):
                            voice.Speak("", SVSF_ASYNC | SVSF_PURGE)  # stops the current sentence
                            purged = True
                except Exception as e:
                    print("Text-to-speech failed:", e)
            if(onDone is not None):
                onDone()

    def setEnabled(self, enabled):
        self.enabled = enabled
        if not(enabled):
            self.cancel()  # cuts short what is being said

    def cancel(self):
        self.generation += 1

    def transition(self, t1, t2, cause, onDone=None):
        say = lambda txt: self.say(txt, onDone)
        if(cause == "album"):
            say("We leave you with the title " + first(t2, 'title') + " from the same album " + first(t1, 'album'))
        elif(cause == "artist"):
            say("We keep going with the same artist " + first(t1, 'artist') + ", we listen to the title " + first(t2, 'title'))
        elif (cause == "genre"):
            if(first(t1, 'album') == first(t2, 'album')):
                say("Within the same ambience of the music " + first(t1, 'genre') + ", we invite you to admire the title " + first(t2, 'title'))
            elif(first(t1, 'artist') == first(t2, 'artist')):
                say("Within the same ambience of the artist " + first(t2, 'artist') + ", and his music " + first(t1, 'genre') + " we propose to you the title " + first(t2, 'title'))
            else:
                say("We continue with the same pace of music " + first(t2, 'genre') + " we present for you the artist " + first(t2, 'artist') + ", through his title " + first(t2, 'title'))
        elif (cause == "date"):
            if (first(t1, 'album') == first(t2, 'album')):
                say("Another title from the same albume " + first(t2, 'album') + ", of the year " + first(t2, 'date') + ", we listen to the title " + first(t2, 'title'))
            elif (first(t1, 'artist') == first(t2, 'artist')):
                say(first(t2, 'date') + " was a rech year for the artist " + first(t2, 'artist') + ", so listen with us to his title " + first(t2, 'title') + " from the same year.")
            else:
                say("We will stay in the ambience of the year " + first(t2, 'date') + ", but with anothe artist, so allow us to present to you " + first(t2, 'title') + " of " + first(t2, 'artist'))
        elif (cause == "sound"):
            say("Here is something that sounds alike: " + first(t2, 'title') + " by " + first(t2, 'artist'))
        else:
            say("It is time to change, listen with use to " + first(t2, 'title'))

    def say(self, txt, onDone=None):
        if not(self.enabled):
            if(onDone is not None):
                onDone()
            return
        self.Display(txt)
        self.requests.put((txt, self.generation, onDone))

    def shutdown(self):
        self.cancel()
        self.requests.put((None, None, None))
        self.thread.join(timeout=2)

    def welcome(self, title = "", filter = ""):
        filtext = ""
        if (len(filter) * len(title) > 0):
            filtext = "according to your demand " + filter
        self.say("welcome, " + filtext + " we will start our program with the track " + title)

    def Display(self, txt):
        if callable(self.display):
            self.display(txt)
        else:
            print(txt)