"""
Musicana - Intelligent Music Player with GUI

Main graphical user interface for the Musicana music player.
Provides album artwork display, playback controls, search/filtering,
and dynamic color theming based on album art.
"""

from tkinter import *
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


def intToTimeText(i):
    """
    Convert seconds to time display format.
    
    Args:
        i (int): Time in seconds
        
    Returns:
        str: Formatted time string (M:SS or just seconds if < 60)
    """
    if i < 60:
        return str(i)
    else:
        return str(int(i / 60)) + ":" + ("0" + str(i % 60))[-2:]

class Application(Frame):
    """
    Main application window for Musicana music player.
    
    Provides a modern UI with:
    - Search/filter functionality
    - Album artwork display with color theming
    - Playback controls (play/pause, next, shuffle)
    - Volume and time sliders
    - Track information display
    """
    
    # UI Constants
    ALBUM_ART_SIZE = 350
    
    def __init__(self):
        """Initialize the application window and load music library."""
        self.root = Tk()
        self.root.title("Musicana - Music Player")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.root.configure(bg='#1e1e1e')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.commentateur = Comentateur.Commentator()

        # Load music library path from environment
        load_dotenv()
        music_path = os.getenv("MUSICANA_MUSIC_PATH", "C:/Users/chari/Documents/D/Music/")
        self.tracks = FileSystem.getAllMp3(music_path)
        self.player = Player.Player()
        self.commentateur.say("Hello, Any filter to start from? : ")
        self.titles = self.getTracksKeys(self.tracks)
        self.track = random.choice(list(self.tracks))
        self.banned = queue.Queue(maxsize=20)
        self.bgColor = "#2d2d2d"
        self.fgColor = "#ffffff"
        self.user_pause = False

        self.interface()
        self.findTrack()
        self.root.mainloop()

    def interface(self):
        """Build the user interface layout."""
        # Main container with padding
        main_container = Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Search/Filter Section
        frm_search_bar = Frame(main_container, bg='#2d2d2d', relief=RIDGE, bd=2)
        frm_search_bar.pack(fill='x', pady=(0, 15))
        
        Lbl_find = Label(frm_search_bar, text="🔍 Search:", font=("Segoe UI", 10), 
                        bg='#2d2d2d', fg='#ffffff', padx=10, pady=10)
        Lbl_find.pack(side=LEFT)
        
        self.inp_find = Entry(frm_search_bar, font=("Segoe UI", 10), bd=0, 
                             relief=FLAT, bg='#3d3d3d', fg='#ffffff', 
                             insertbackground='#ffffff', width=40)
        self.inp_find.pack(side=LEFT, fill='x', expand=True, padx=(0, 10), pady=10)
        self.inp_find.bind('<Return>', self.findTrackKey)
        
        btn_find = Button(frm_search_bar, text='FILTER', font=("Segoe UI", 9, "bold"),
                         command=self.findTrack, bg='#007acc', fg='white', 
                         bd=0, padx=20, pady=8, cursor='hand2', relief=FLAT)
        btn_find.pack(side=RIGHT, padx=10, pady=10)

        # Track Display Area
        self.frm_track = Frame(main_container, bg='#1e1e1e')
        self.frm_track.pack(fill=BOTH, expand=True, pady=(0, 15))

        self.frm_image = Frame(self.frm_track, width=300, height=300, bg='#2d2d2d')
        self.frm_image.pack(side=LEFT, padx=(0, 20))

        self.frm_track_info = Frame(self.frm_track, bg='#1e1e1e')
        self.frm_track_info.pack(side=LEFT, fill=BOTH, expand=True)

        # Player Controls Section
        frm_controls = Frame(main_container, bg='#2d2d2d', relief=RIDGE, bd=2)
        frm_controls.pack(fill='x', pady=(0, 10))
        
        # Button container
        frm_buttons = Frame(frm_controls, bg='#2d2d2d')
        frm_buttons.pack(pady=15)
        
        # Play/Pause button with larger size
        self.btn_play = Button(frm_buttons, text='▶ PLAY', font=("Segoe UI", 10, "bold"),
                              command=self.play, bg='#00a86b', fg='white', 
                              bd=0, padx=25, pady=12, cursor='hand2', relief=FLAT)
        self.btn_play.pack(side=LEFT, padx=5)

        btn_next = Button(frm_buttons, text='⏭ NEXT', font=("Segoe UI", 10, "bold"),
                         command=self.next, bg='#4a4a4a', fg='white', 
                         bd=0, padx=20, pady=12, cursor='hand2', relief=FLAT)
        btn_next.pack(side=LEFT, padx=5)

        btn_random = Button(frm_buttons, text='🔀 SHUFFLE', font=("Segoe UI", 10, "bold"),
                           command=self.randomTrack, bg='#4a4a4a', fg='white', 
                           bd=0, padx=20, pady=12, cursor='hand2', relief=FLAT)
        btn_random.pack(side=LEFT, padx=5)
        
        # Progress bar container
        frm_progress = Frame(frm_controls, bg='#2d2d2d')
        frm_progress.pack(fill='x', padx=20, pady=(0, 10))
        
        Label(frm_progress, text="0:00", font=("Segoe UI", 9), 
              bg='#2d2d2d', fg='#999999').pack(side=LEFT, padx=(0, 10))
        
        self.scl_time = Scale(frm_progress, from_=0, to=342, orient=HORIZONTAL,
                             bg='#2d2d2d', fg='#ffffff', troughcolor='#1e1e1e',
                             highlightthickness=0, bd=0, sliderrelief=FLAT,
                             font=("Segoe UI", 8))
        self.scl_time.bind("<ButtonRelease-1>", self.setPos)
        self.scl_time.pack(side=LEFT, fill='x', expand=True)
        
        self.lbl_trackLength = Label(frm_progress, text="0:00", font=("Segoe UI", 9),
                                     bg='#2d2d2d', fg='#999999', padx=10)
        self.lbl_trackLength.pack(side=LEFT)
        
        # Volume control
        frm_volume = Frame(frm_controls, bg='#2d2d2d')
        frm_volume.pack(fill='x', padx=20, pady=(0, 15))
        
        Label(frm_volume, text="🔊 Volume:", font=("Segoe UI", 9), 
              bg='#2d2d2d', fg='#ffffff').pack(side=LEFT, padx=(0, 10))
        
        self.scl_son = Scale(frm_volume, from_=0, to=100, orient=HORIZONTAL,
                            command=self.setVolume, bg='#2d2d2d', fg='#ffffff',
                            troughcolor='#1e1e1e', highlightthickness=0, bd=0,
                            sliderrelief=FLAT, font=("Segoe UI", 8), length=200)
        self.scl_son.pack(side=LEFT)

        # Status bar
        self.statusbar = Label(self.root, text="Ready to play music…", 
                              font=("Segoe UI", 9), bd=1, relief=SUNKEN, anchor=W,
                              bg='#2d2d2d', fg='#cccccc', padx=10, pady=5)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.commentateur.display = self.statusbar

    def getTracksKeys(self, tracks):
        """
        Extract all unique metadata field names from tracks.
        
        Args:
            tracks (dict): Dictionary of tracks with metadata
            
        Returns:
            list: List of unique metadata field names
        """
        keys = []
        for track in tracks.values():
            for k in track.keys():
                if not (k in keys):
                    keys.append(k)
        return keys

    def findTrack(self):
        """Apply search filter and play a random matching track."""
        filtered_tracks = FileSystem.filterTracks(self.tracks, self.inp_find.get()).keys()
        self.track = random.choice(list(filtered_tracks))
        self.player.playing = None
        self.play()

    def findTrackKey(self, event):
        """Handle Enter key press in search box."""
        self.findTrack()

    def play(self):
        """
        Toggle play/pause or start playing the current track.
        
        Handles three states:
        - No track playing: Start playback
        - Track playing: Pause
        - Track paused: Resume
        """
        self.add2queue(self.track)
        
        if self.player.playing is None:
            # Start new track
            self.btn_play["text"] = "⏸ PAUSE"
            self.btn_play["bg"] = "#ff6b6b"
            self.scl_time.set(value=0)
            self.scl_son.set(value=self.player.getVolume())
            info = self.player.play(self.track)
            self.displayTrackInfo(info)
            self.scl_time.configure(to=self.player.mp3Length)
            self.lbl_trackLength.configure(text=intToTimeText(int(self.player.mp3Length)))
            self.user_pause = False
        elif self.player.playing:
            # Pause current track
            self.btn_play["text"] = "▶ PLAY"
            self.btn_play["bg"] = "#00a86b"
            self.player.pause()
            self.user_pause = True
        else:
            # Resume paused track
            self.btn_play["text"] = "⏸ PAUSE"
            self.btn_play["bg"] = "#ff6b6b"
            self.player.resume()
            self.user_pause = False
        
        self.update_clock()

    def displayTrackInfo(self, info):
        """
        Display track metadata in the UI.
        
        Creates labels for track information with priority styling for
        important fields (title, album, artist, genre, date).
        
        Args:
            info (dict): Track metadata from ID3 tags
        """
        class InfoLabel:
            """Helper class for metadata field display configuration."""
            def __init__(self, id, name, font):
                self.id = id
                self.name = name
                self.font = font
        
        # Rebuild track display area
        self.frm_track.destroy()
        self.frm_track = Frame(self.root.children['!frame'], bg='#1e1e1e')
        self.frm_track.pack(fill=BOTH, expand=True, pady=(0, 15))
        self.getImage(self.track)
        self.frm_track.configure(bg=self.bgColor)
        self.frm_track_info.destroy()
        self.frm_track_info = Frame(self.frm_track, bg=self.bgColor)
        self.frm_track_info.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Priority fields with custom styling
        dict = {
            "title": InfoLabel(1, "title", ("Segoe UI", 16, "bold")),
            "album": InfoLabel(2, "album", ("Segoe UI", 13)),
            "artist": InfoLabel(3, "artist", ("Segoe UI", 13, "bold")),
            "genre": InfoLabel(4, "genre", ("Segoe UI", 11)),
            "date": InfoLabel(5, "date", ("Segoe UI", 10))
        }
        
        i = 6
        font = ("Segoe UI", 9)
        
        # Display metadata fields
        for k in info.keys():
            if k in dict.keys():
                # Priority field with special styling
                label_text = self.mkString(info[k])
                lbl = Label(self.frm_track_info, text=label_text, 
                          font=dict.get(k).font, bg=self.bgColor, 
                          fg=self.fgColor, anchor=W, padx=15, pady=8)
                lbl.grid(row=dict.get(k).id, column=0, sticky=W, columnspan=2)
            else:
                # Other fields with standard styling
                kname = str(k.title() + ": ")
                ink = Label(self.frm_track_info, text=kname, bg=self.bgColor, 
                          fg='#999999', padx=15, pady=5, font=("Segoe UI", 9), anchor=W)
                ink.grid(row=i, column=0, sticky=W)
                inv = Label(self.frm_track_info, text=self.mkString(info[k]), 
                          font=font, bg=self.bgColor, fg=self.fgColor, 
                          padx=5, pady=5, anchor=W)
                inv.grid(row=i, column=1, sticky=W)
                i += 1

    def getImage(self, track):
        """
        Extract and display album artwork, calculate theme colors.
        
        Extracts album artwork from MP3 file, displays it, and calculates
        average color for dynamic UI theming.
        
        Args:
            track (str): Path to the MP3 file
        """
        from io import BytesIO
        
        self.frm_image.destroy()
        self.frm_image = Frame(self.frm_track, width=300, height=300, bg='#2d2d2d', relief=RIDGE, bd=2)
        self.frm_image.pack(side=LEFT, padx=(0, 20))

        file = File(track)
        if 'APIC:' in file.tags.keys():
            # Extract and save album artwork
            artwork = file.tags['APIC:'].data
            with open('image.jpg', 'wb') as img:
                img.write(artwork)
            img.close()
            
            # Resize and display artwork
            self.original = Image.open("image.jpg")
            resample = getattr(Image, "Resampling", Image).LANCZOS
            self.fitted = self.original.resize((300, 300), resample)
            self.imge = ImageTk.PhotoImage(self.fitted)
            panel = Label(self.frm_image, image=self.imge, width=300, height=300, bd=0)
            panel.pack(fill=BOTH, expand=YES)

            # Calculate average color for theming (sample every 10th pixel for performance)
            rgb_im = self.fitted.convert('RGB')
            sum = 0
            R = 0
            G = 0
            B = 0
            step = 10  # Sample every 10th pixel
            
            for i in range(0, min(self.ALBUM_ART_SIZE, self.fitted.width), step):
                for j in range(0, min(self.ALBUM_ART_SIZE, self.fitted.height), step):
                    r, g, b = rgb_im.getpixel((i, j))
                    R += r
                    G += g
                    B += b
                    sum += 1

            avg_r, avg_g, avg_b = R // sum, G // sum, B // sum
            
            # Create darker background based on album art
            self.bgColor = '#%02x%02x%02x' % (max(0, avg_r - 40), max(0, avg_g - 40), max(0, avg_b - 40))
            
            # Better contrast for text
            brightness = (avg_r + avg_g + avg_b) / 3
            self.fgColor = '#ffffff' if brightness < 128 else '#000000'
        else:
            # No album art - show placeholder
            placeholder = Label(self.frm_image, text="♪\nNo Album Art", 
                              font="Segoe UI 14", bg='#2d2d2d', 
                              fg='#666666', width=300, height=300)
            placeholder.pack(fill=BOTH, expand=YES)
    def update_clock(self):
        """
        Update playback position slider.
        
        Called periodically to update the time slider position.
        Also checks if track has ended and triggers next track.
        """
        if self.user_pause:
            return
        
        if self.player.playing:
            self.scl_time.set(value=self.player.getPos())
            self.root.after(1000, self.update_clock)
        
        if self.player.isTrackEnded():
            self.statusbar = ""
            print("song ended")
            self.next()

    def setPos(self, event):
        """
        Handle time slider position change (seeking).
        
        Args:
            event: Tkinter event from slider release
            
        Note:
            Seeking is currently not fully implemented in Player class
        """
        self.player.setPos(int(self.scl_time.get()))

    def setVolume(self, event):
        """
        Handle volume slider change.
        
        Args:
            event: Tkinter event from slider movement
        """
        self.player.setVolume(int(self.scl_son.get()) / 100)

    def on_closing(self):
        """Handle window close button - cleanup and exit."""
        self.player.stop()
        self.root.destroy()

    def add2queue(self, track):
        """
        Add track to history queue to avoid immediate repetition.
        
        Args:
            track (str): Track path to add to history
        """
        if self.banned.full():
            self.banned.get()
        self.banned.put(track)

    def mkString(self, List, sep=" / "):
        """
        Convert a list to a separator-delimited string.
        
        Args:
            List (list): List of strings to join
            sep (str): Separator string (default: " / ")
            
        Returns:
            str: Joined string
        """
        s = ""
        for l in List:
            s += l + sep
        return s[:-3]

    def randomTrack(self):
        """Select and play a completely random track."""
        self.track = Nexter_RandomWalk.nextIsRandom(self.tracks)
        self.player.playing = None
        self.play()

    def next(self):
        """Select and play the next track using smart recommendation."""
        self.track = Nexter_RandomWalk.next(self.tracks, self.track, self.banned)
        self.player.playing = None
        self.play()