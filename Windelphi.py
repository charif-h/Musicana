from tkinter import *  # for UI
from mutagen import File
from PIL import ImageTk, Image
from dotenv import load_dotenv
import os

import ImageColorExtract
import Nexter_RandomWalk
import Player
import FileSystem
import Comentateur
import random
import queue
#from tkinter.ttk import *

def intToTimeText(i):
    if(i < 60):
        return str(i)
    else:
        return str(int(i/60)) + ":" + ("0" + str(i%60))[-2:]

class Application(Frame):

    def __init__(self):
        self.root = Tk() # creates an Empty window
        self.root.title("Musicana - Smart Music Player")
        self.root.minsize(800, 600)
        self.root.configure(bg='#f0f0f0')
        self.commentateur = Comentateur.Commentator()

        load_dotenv()
        music_path = os.getenv("MUSICANA_MUSIC_PATH", "C:/Users/chari/Documents/D/Music/")
        self.tracks = FileSystem.getAllMp3(music_path)
        self.player = Player.Player()
        self.commentateur.say("Hello, Any filter to start from? : ")
        self.titles = self.getTracksKeys(self.tracks)
        self.track = random.choice(list(self.tracks))
        self.banned = queue.Queue(maxsize=20)
        self.bgColor = "#f0f0f0"
        self.fgColor = "#333333"
        self.user_pause = False

        self.interface()
        self.findTrack()
        self.root.mainloop()

    def interface(self):
        # Search bar section
        frm_search_bar = Frame(self.root, bg='#f0f0f0')
        frm_search_bar.pack(side='top', fill='x', padx=20, pady=15)
        
        Lbl_find = Label(frm_search_bar, text="Search:", font=("Arial", 12), bg='#f0f0f0', fg='#333333')
        Lbl_find.pack(side=LEFT, padx=(0, 10))
        
        self.inp_find = Entry(frm_search_bar, bd=2, width=50, font=("Arial", 11), relief='solid')
        self.inp_find.pack(side=LEFT, fill='x', expand=True, ipady=5)
        self.inp_find.bind('<Return>', self.findTrackKey)
        
        btn_find = Button(frm_search_bar, text='Filter', command=self.findTrack, 
                         font=("Arial", 10, "bold"), bg='#4CAF50', fg='white', 
                         relief='flat', padx=20, pady=5, cursor='hand2')
        btn_find.pack(side=RIGHT, padx=(10, 0))

        # Player controls section
        frm_player = Frame(self.root, bg='#f0f0f0')
        frm_player.pack(side='top', fill='x', padx=20, pady=10)
        
        # Control buttons frame
        frm_buttons = Frame(frm_player, bg='#f0f0f0')
        frm_buttons.pack(side='top', pady=(0, 10))
        
        self.btn_play = Button(frm_buttons, text='▶ Play', command=self.play,
                              font=("Arial", 10, "bold"), bg='#2196F3', fg='white',
                              relief='flat', padx=20, pady=8, cursor='hand2', width=10)
        self.btn_play.pack(side='left', padx=5)

        btn_next = Button(frm_buttons, text='⏭ Next', command=self.next,
                         font=("Arial", 10, "bold"), bg='#2196F3', fg='white',
                         relief='flat', padx=20, pady=8, cursor='hand2', width=10)
        btn_next.pack(side='left', padx=5)

        btn_random = Button(frm_buttons, text='🎲 Random', command=self.randomTrack,
                           font=("Arial", 10, "bold"), bg='#2196F3', fg='white',
                           relief='flat', padx=20, pady=8, cursor='hand2', width=10)
        btn_random.pack(side='left', padx=5)
        
        # Time slider section
        frm_time = Frame(frm_player, bg='#f0f0f0')
        frm_time.pack(side='top', fill='x', pady=(0, 10))
        
        Label(frm_time, text="Time:", font=("Arial", 9), bg='#f0f0f0', fg='#333333').pack(side=LEFT, padx=(0, 10))
        
        self.scl_time = Scale(frm_time, from_=0, to=342, orient=HORIZONTAL, 
                             showvalue=0, relief='flat', bg='#e0e0e0', 
                             troughcolor='#2196F3', highlightthickness=0)
        self.scl_time.bind("<ButtonRelease-1>", self.setPos)
        self.scl_time.pack(side=LEFT, fill='x', expand=True, padx=5)
        
        self.lbl_trackLength = Label(frm_time, text="00:00", font=("Arial", 9, "bold"), 
                                     bg='#f0f0f0', fg='#333333', width=6)
        self.lbl_trackLength.pack(side=LEFT, padx=(10, 0))
        
        # Volume control section
        frm_volume = Frame(frm_player, bg='#f0f0f0')
        frm_volume.pack(side='top', fill='x')
        
        Label(frm_volume, text="Volume:", font=("Arial", 9), bg='#f0f0f0', fg='#333333').pack(side=LEFT, padx=(0, 10))
        
        self.scl_son = Scale(frm_volume, from_=0, to=100, orient=HORIZONTAL, 
                           command=self.setVolume, showvalue=1, relief='flat',
                           bg='#e0e0e0', troughcolor='#4CAF50', highlightthickness=0)
        self.scl_son.pack(side=LEFT, fill='x', expand=True, padx=5)

        # Track info section
        self.frm_track = Frame(self.root, bg='#f0f0f0')
        self.frm_track.pack(side=TOP, fill='both', expand=True, padx=20, pady=10)

        self.frm_image = Frame(self.frm_track, width=350, height=350, bg='#ffffff', relief='solid', bd=1)
        self.frm_image.pack(side=LEFT, padx=(0, 20))

        self.frm_track_info = Frame(self.frm_track, bg='#f0f0f0')
        self.frm_track_info.pack(side=RIGHT, fill='both', expand=True)

        # Status bar
        self.statusbar = Label(self.root, text="Ready to play...", bd=1, relief=SUNKEN, 
                              anchor=W, bg='#e0e0e0', fg='#333333', font=("Arial", 9), 
                              padx=10, pady=5)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.commentateur.display = self.statusbar
        # table
        '''frm_table = Frame(self.root, width=300, height=50, bg='grey')
        frm_table.pack(side='bottom', fill='both', padx=10, pady=5, expand=True)
        height = len(self.tracks) + 1
        width = len(self.titles)
        for i in range(height):  # Rows
            for j in range(width):  # Columns
                txt = ""
                if(i == 0):
                    txt = self.titles[j]
                else:
                    txt = self.tracks[i - 1]
                b = Label(frm_table, text=txt)
                b.grid(row=i, column=j)'''

    def getTracksKeys(self, tracks):
        keys = []
        for track in tracks.values():
            for k in track.keys():
                if not(k in keys):
                    keys.append(k)
        return keys

    def findTrack(self):
        filtered_tracks = FileSystem.filterTracks(self.tracks, self.inp_find.get()).keys()
        self.track = random.choice(list(filtered_tracks))
        self.player.playing = None
        self.play()

    def findTrackKey(self, event):
        self.findTrack()

    def play(self):
        self.add2queue(self.track)
        if(self.player.playing is None):
            self.btn_play["text"] = "⏸ Pause"
            self.scl_time.set(value=0)
            self.scl_son.set(value=self.player.getVolume())
            info = self.player.play(self.track)
            self.displayTrackInfo(info)
            self.scl_time.configure(to=self.player.mp3Length)
            self.lbl_trackLength.configure(text= intToTimeText(int(self.player.mp3Length)))
            self.user_pause = False
        elif(self.player.playing):
            self.btn_play["text"] = "▶ Play"
            self.player.pause()
            self.user_pause = True
        else:
            self.btn_play["text"] = "⏸ Pause"
            self.player.resume()
            self.user_pause = False
        self.update_clock()

    def displayTrackInfo(self, info):
        class InfoLabel:
            def __init__(self, id, name, font):
                self.id = id
                self.name = name
                self.font = font
        self.frm_track.destroy()
        self.frm_track = Frame(self.root, bg='#f0f0f0')
        self.frm_track.pack(side=TOP, fill='both', expand=True, padx=20, pady=10)
        self.getImage(self.track)
        self.frm_track.configure(bg = self.bgColor)
        self.frm_track_info.destroy()
        self.frm_track_info = Frame(self.frm_track, bg=self.bgColor, relief='solid', bd=1, padx=20, pady=20)
        self.frm_track_info.pack(side=RIGHT, fill='both', expand=True)
        
        dict = {"title":InfoLabel(1, "title", "Arial 18 bold"),
                "album":InfoLabel(2, "album", "Arial 14 bold"),
                "artist":InfoLabel(3, "artist", "Arial 14 bold"),
                "genre":InfoLabel(4, "genre", "Arial 12"),
                "date":InfoLabel(5, "title", "Arial 11")}
        i = 6
        font = "Arial 10"
        for k in info.keys():
            kname = str(k.capitalize() + ":")
            ink = Label(self.frm_track_info, text= kname, bg=self.bgColor, fg=self.fgColor, 
                       font="Arial 10 bold", anchor='w', padx=5, pady=8)
            if(k in dict.keys()):
                ink.grid(row=dict.get(k).id, column=0, sticky='w', padx=(0, 10))
                inv = Label(self.frm_track_info, text=self.mkString(info[k]), font=dict.get(k).font, 
                          bg=self.bgColor, fg=self.fgColor, anchor='w', padx=5, pady=8)
                inv.grid(row=dict.get(k).id, column=1, sticky='w')
            else:
                ink.grid(row=i, column=0, sticky='w', padx=(0, 10))
                inv = Label(self.frm_track_info, text=self.mkString(info[k]), font=font, 
                          bg=self.bgColor, fg=self.fgColor, anchor='w', padx=5, pady=8)
                inv.grid(row=i, column=1, sticky='w')
            i += 1

    def getImage(self, track):
        self.frm_image.destroy()
        self.frm_image = Frame(self.frm_track, width=350, height=350, bg='#ffffff', relief='solid', bd=1)
        self.frm_image.pack(side=LEFT, padx=(0, 20))

        file = File(track)
        if('APIC:' in file.tags.keys()):
            artwork = file.tags['APIC:'].data  # access APIC frame and grab the image
            with open('image.jpg', 'wb') as img:
                img.write(artwork)
            img.close()
            self.original = Image.open("image.jpg")
            resample = getattr(Image, "Resampling", Image).LANCZOS  # PIL>=10 removed ANTIALIAS
            self.fitted = self.original.resize((350, 350), resample)
            self.imge = ImageTk.PhotoImage(self.fitted)  # PhotoImage(file="image.jpg")
            #image1 = PhotoImage(file="image.jpg")
            panel = Label(self.frm_image, image = self.imge, width=350, height=350, bg='#ffffff')
            panel.pack(side = "bottom", fill = "both", expand = "yes")

            rgb_im = self.fitted.convert('RGB')
            sum = 0
            R = 0
            G = 0
            B = 0
            for i in range(min(350, self.fitted.width)):
                for j in range(min(350, self.fitted.height)):
                    r, g, b = rgb_im.getpixel((i, j))
                    R += r
                    G += g
                    B += b
                    sum += 1

            self.bgColor = '#%02x%02x%02x' % (R//sum, G//sum, B//sum)
            # Calculate complementary color for better contrast
            brightness = (R//sum + G//sum + B//sum) / 3
            if brightness > 127:
                self.fgColor = '#333333'  # Dark text for light backgrounds
            else:
                self.fgColor = '#f0f0f0'  # Light text for dark backgrounds
            '''dict = ImageColorExtract.image_histogram(self.fitted)
            print(dict)
            self.bgColor = list(dict.keys())[0]
            self.fgColor = list(dict.keys())[1]
            print(self.bgColor + " " + self.fgColor)'''



        #canvas.create_image(20, 20, anchor=NW, image=imge)
        #image = Label(self.frm_track_info, image = img)
        #image.grid(row=0, column=0)


    def update_clock(self):
        if self.user_pause:
            return
        if(self.player.playing):
            #val = int(self.scl_time.get()) + 1
            #self.scl_time.set(value=val)
            self.scl_time.set(value=self.player.getPos())
            self.root.after(1000, self.update_clock)
        if(self.player.isTrackEnded()):
            self.statusbar =  ""
            print("song ended")
            self.next()

    def setPos(self, event):
        #if(self.player.getPos() != int(self.scl_time.get())*1000):
        self.player.setPos(int(self.scl_time.get()))


    def setVolume(self, event):
        self.player.setVolume(int(self.scl_son.get())/100)

    def add2queue(self, track):
        if (self.banned.full()):
            self.banned.get()
        self.banned.put(track)

    def mkString(self, List, sep=" / "):
        s = ""
        for l in List:
            s += l + sep
        return s[:-3]

    def randomTrack(self):
        self.track = Nexter_RandomWalk.nextIsRandom(self.tracks)
        self.player.playing = None
        self.play()

    def next(self):
        self.track = Nexter_RandomWalk.next(self.tracks, self.track, self.banned)
        self.player.playing = None
        self.play()