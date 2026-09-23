from tkinter import *  # for UI
from mutagen import File
from PIL import ImageTk, Image
from io import BytesIO

import Player
import FileSystem
import Comentateur
import Session

def intToTimeText(i):
    if(i < 60):
        return str(i)
    else:
        return str(int(i/60)) + ":" + ("0" + str(i%60))[-2:]

class Application(Frame):

    def __init__(self, musicPath):
        self.root = Tk() # creates an Empty window
        self.commentateur = Comentateur.Commentator()

        self.session = Session.PlayerSession(FileSystem.getAllMp3(musicPath), self.commentateur)
        self.player = Player.Player()
        self.commentateur.say("Hello, Any filter to start from? : ")
        self.session.start()
        self.bgColor = "white"
        self.fgColor = "black"

        self.interface()

    def interface(self):
        # filter
        frm_search_bar = Frame(self.root)
        frm_search_bar.pack(side='top', fill='x', padx=2, pady=1, expand=True)
        Lbl_find = Label(frm_search_bar, text="find", padx=2, pady=5)
        Lbl_find.pack(side=LEFT)
        self.inp_find = Entry(frm_search_bar, bd=2, width=50)
        self.inp_find.pack(side=LEFT, fill='x')
        self.inp_find.bind('<Return>', self.findTrackKey)
        btn_find = Button(frm_search_bar, text='filter', command=self.findTrack)
        btn_find.pack(side=RIGHT)

        # playser
        frm_player = Frame(self.root)
        frm_player.pack(side='top', fill='x', padx=2, pady=1, expand=True)

        self.btn_play = Button(frm_player, text='play', command=self.play)
        self.btn_play.pack(side='left')

        btn_next = Button(frm_player, text='next', command=self.next)
        btn_next.pack(side='left')

        btn_random = Button(frm_player, text='rndm', command=self.randomTrack)
        btn_random.pack(side='left')

        self.scl_time = Scale(frm_player, from_=0, to=342, orient=HORIZONTAL)
        self.scl_time.bind("<ButtonRelease-1>", self.setPos)
        self.scl_time.pack(side=LEFT)
        self.lbl_trackLength = Label(frm_player, text="00", padx=1, pady=5)
        self.lbl_trackLength.pack(side=LEFT)

        self.scl_son = Scale(frm_player, from_=0, to=100, orient=HORIZONTAL, command=self.setVolume)
        self.scl_son.pack(side=RIGHT)

        # Track

        self.frm_track = Frame(self.root)
        self.frm_track.pack(side=TOP, fill='x')

        self.frm_image = Frame(self.frm_track, width=300, height=300)
        self.frm_image.pack(side=LEFT)

        self.frm_track_info = Frame(self.frm_track)
        self.frm_track_info.pack(side=RIGHT, fill='x')

        # Status bar
        self.statusbar = Label(self.root, text="on the way…", bd=1, relief=SUNKEN, anchor=W)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.commentateur.display = self.statusbar

    def run(self):
        self.root.mainloop()

    def findTrack(self):
        self.session.start(self.inp_find.get())
        self.playCurrent()

    def findTrackKey(self, event):
        self.findTrack()

    def playCurrent(self):
        self.player.playing = None
        self.play()

    def play(self):
        if(self.player.playing is None):
            self.btn_play["text"] = "stop"
            self.scl_time.set(value=0)
            self.scl_son.set(value=self.player.getVolume())
            info = self.player.play(self.session.current)
            self.displayTrackInfo(info)
            self.scl_time.configure(to=self.player.mp3Length)
            self.lbl_trackLength.configure(text= intToTimeText(int(self.player.mp3Length)))
        elif(self.player.playing):
            self.btn_play["text"] = "play"
            self.player.pause()
        else:
            self.btn_play["text"] = "stop"
            self.player.resume()
        self.update_clock()

    def displayTrackInfo(self, info):
        class InfoLabel:
            def __init__(self, id, name, font):
                self.id = id
                self.name = name
                self.font = font
        self.frm_track.destroy()
        self.frm_track = Frame(self.root, height=300)
        self.frm_track.pack(side=TOP, fill='x')
        self.getImage(self.session.current)
        self.frm_track.configure(bg = self.bgColor)
        self.frm_track_info.destroy()
        self.frm_track_info = Frame(self.frm_track, height=300, bg=self.bgColor)
        self.frm_track_info.pack(side=RIGHT, fill='x')
        dict = {"title":InfoLabel(1, "title", "Tahoma 20 bold"),
                "album":InfoLabel(2, "album", "Tahoma 18 bold"),
                "artist":InfoLabel(3, "artist", "Tahoma 18 bold"),
                "genre":InfoLabel(4, "genre", "Tahoma 18"),
                "date":InfoLabel(5, "title", "Tahoma 16")}
        i = 6
        font = "Tahoma 10"
        for k in info.keys():
            kname = str(k + ": ")
            ink = Label(self.frm_track_info, text= kname, bg=self.bgColor, fg =self.fgColor, padx=2, pady=5)
            if(k in dict.keys()):
                ink.grid(row=dict.get(k).id, column=0)
                inv = Label(self.frm_track_info, text=self.mkString(info[k]), font=dict.get(k).font, bg=self.bgColor, fg =self.fgColor, padx=2, pady=5)
                inv.grid(row=dict.get(k).id, column=1)
            else:
                ink.grid(row=i, column=0)
                inv = Label(self.frm_track_info, text=self.mkString(info[k]), font=font, bg=self.bgColor, fg =self.fgColor, padx=2, pady=5)
                inv.grid(row=i, column=1)
            i += 1

    def getImage(self, track):
        self.frm_image.destroy()
        self.frm_image = Frame(self.frm_track, width=300, height=300)
        self.frm_image.pack(side=LEFT)

        file = File(track)
        if('APIC:' in file.tags.keys()):
            artwork = file.tags['APIC:'].data  # access APIC frame and grab the image
            self.original = Image.open(BytesIO(artwork))
            self.fitted = self.original.resize((300, 300),Image.LANCZOS)
            self.imge = ImageTk.PhotoImage(self.fitted)
            panel = Label(self.frm_image, image = self.imge, width=300, height=300)
            panel.pack(side = "bottom", fill = "both", expand = "yes")

            rgb_im = self.fitted.convert('RGB')
            sum = 0
            R = 0
            G = 0
            B = 0
            for i in range(300):
                for j in range(300):
                    r, g, b = rgb_im.getpixel((i, j))
                    R += r
                    G += g
                    B += b
                    sum += 1

            self.bgColor = '#%02x%02x%02x' % (R//sum, G//sum, B//sum)
            self.fgColor = '#%02x%02x%02x' % (((R // sum) + 127)%255, ((G // sum) + 127)%255, ((B // sum) + 127)%255)

    def update_clock(self):
        if(self.player.playing):
            self.scl_time.set(value=self.player.getPos())
            self.root.after(1000, self.update_clock)
        if(self.player.isTrackEnded()):
            self.statusbar =  ""
            print("song ended")
            self.next()

    def setPos(self, event):
        self.player.setPos(int(self.scl_time.get()))

    def setVolume(self, event):
        self.player.setVolume(int(self.scl_son.get())/100)

    def mkString(self, List, sep=" / "):
        s = ""
        for l in List:
            s += l + sep
        return s[:-3]

    def randomTrack(self):
        self.session.random()
        self.playCurrent()

    def next(self):
        self.session.next()
        self.playCurrent()