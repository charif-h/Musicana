from PySide6.QtCore import QByteArray, QItemSelectionModel, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSlider, QApplication, QFrame, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QMainWindow, QPushButton, QSlider, QStyle, QTableView,
                               QVBoxLayout, QWidget)

import FileSystem
import Settings
import Theme
from TrackTableModel import PATH_ROLE, TrackFilterProxy, TrackTableModel

ART_SIZE = 200
MAIN_TAGS = ("title", "artist", "album", "genre", "date")

def formatTime(seconds):
    seconds = int(seconds)
    return str(seconds // 60) + ":" + str(seconds % 60).zfill(2)

def mkString(values, sep=" / "):
    return sep.join(values)

class MainWindow(QMainWindow):
    def __init__(self, session, player, commentator, settings):
        super().__init__()
        self.session = session
        self.player = player
        self.commentator = commentator
        self.settings = settings
        self.setWindowTitle("Musicana")
        self.resize(960, 720)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # search bar
        searchBar = QHBoxLayout()
        self.inp_find = QLineEdit()
        self.inp_find.setPlaceholderText("Search title, artist, album, genre…")
        self.inp_find.setClearButtonEnabled(True)
        self.btn_find = QPushButton("Filter")
        searchBar.addWidget(self.inp_find)
        searchBar.addWidget(self.btn_find)
        layout.addLayout(searchBar)

        # player controls
        controls = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_next = QPushButton("Next")
        self.btn_random = QPushButton("Random")
        self.lbl_pos = QLabel(formatTime(0))
        self.sld_time = QSlider(Qt.Horizontal)
        self.sld_time.setPageStep(10)
        self.lbl_length = QLabel(formatTime(0))
        self.lbl_volume = QLabel()
        self.sld_volume = QSlider(Qt.Horizontal)
        self.sld_volume.setRange(0, 100)
        self.sld_volume.setFixedWidth(120)
        for w in (self.btn_play, self.btn_next, self.btn_random, self.lbl_pos):
            controls.addWidget(w)
        controls.addWidget(self.sld_time, 1)
        for w in (self.lbl_length, self.lbl_volume, self.sld_volume):
            controls.addWidget(w)
        layout.addLayout(controls)

        # now playing
        self.frm_nowPlaying = QFrame()
        self.frm_nowPlaying.setObjectName("nowPlaying")
        nowPlaying = QHBoxLayout(self.frm_nowPlaying)
        self.lbl_art = QLabel()
        self.lbl_art.setObjectName("art")
        self.lbl_art.setFixedSize(ART_SIZE, ART_SIZE)
        self.lbl_art.setAlignment(Qt.AlignCenter)
        nowPlaying.addWidget(self.lbl_art)
        info = QVBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("title")
        self.lbl_artistAlbum = QLabel()
        self.lbl_artistAlbum.setObjectName("subtitle")
        self.lbl_genreDate = QLabel()
        self.lbl_otherTags = QLabel()
        self.lbl_otherTags.setObjectName("extra")
        for w in (self.lbl_title, self.lbl_artistAlbum, self.lbl_genreDate, self.lbl_otherTags):
            w.setWordWrap(True)
            w.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info.addWidget(w)
        info.addStretch()
        nowPlaying.addLayout(info, 1)
        layout.addWidget(self.frm_nowPlaying)

        # library
        self.trackModel = TrackTableModel(self.session.tracks, self)
        self.trackProxy = TrackFilterProxy(self)
        self.trackProxy.setSourceModel(self.trackModel)
        self.tbl_tracks = QTableView()
        self.tbl_tracks.setModel(self.trackProxy)
        self.tbl_tracks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_tracks.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_tracks.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_tracks.setAlternatingRowColors(True)
        self.tbl_tracks.setWordWrap(False)
        self.tbl_tracks.verticalHeader().hide()
        self.tbl_tracks.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        header = self.tbl_tracks.horizontalHeader()
        header.setHighlightSections(False)
        for column, width in enumerate((280, 180, 200, 120)):
            header.resizeSection(column, width)
        header.setStretchLastSection(True)
        header.setSortIndicator(1, Qt.AscendingOrder)
        if(settings["tableHeader"]):  # column widths and sort column/order
            header.restoreState(QByteArray.fromBase64(settings["tableHeader"].encode()))
        self.tbl_tracks.setSortingEnabled(True)  # sorts once, by the restored indicator
        layout.addWidget(self.tbl_tracks, 1)

        self.lbl_count = QLabel()
        self.statusBar().addPermanentWidget(self.lbl_count)
        self.statusBar().showMessage("on the way…")
        self.updateCount()

        # Polled rather than using VLC events: those fire on a VLC thread, and Qt widgets are not thread-safe.
        self.clock = QTimer(self)
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.updateClock)
        self.seeking = False

        self.commentator.display = self.showStatus
        self.inp_find.returnPressed.connect(self.findTrack)
        self.inp_find.textChanged.connect(self.filterTable)
        self.tbl_tracks.activated.connect(self.playRow)
        self.btn_find.clicked.connect(self.findTrack)
        self.btn_play.clicked.connect(self.play)
        self.btn_next.clicked.connect(self.next)
        self.btn_random.clicked.connect(self.randomTrack)
        self.sld_time.sliderPressed.connect(self.startSeek)
        self.sld_time.sliderMoved.connect(lambda v: self.lbl_pos.setText(formatTime(v)))
        self.sld_time.sliderReleased.connect(self.seek)
        self.sld_time.actionTriggered.connect(self.timeSliderAction)
        self.player.setVolume(settings["volume"])
        self.sld_volume.setValue(self.player.getVolume())
        if(settings["windowGeometry"]):
            self.restoreGeometry(QByteArray.fromBase64(settings["windowGeometry"].encode()))
        self.sld_volume.valueChanged.connect(self.player.setVolume)
        QGuiApplication.styleHints().colorSchemeChanged.connect(self.colorSchemeChanged)
        self.artImage = None
        self.frm_nowPlaying.setStyleSheet(Theme.nowPlayingStyle())
        self.refreshIcons()

    # Standard icons tinted with the theme's text color: Fusion's own are dark, even in dark mode.
    def icon(self, standardPixmap):
        pixmap = self.style().standardIcon(standardPixmap).pixmap(32, 32)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), self.palette().color(QPalette.ButtonText))
        painter.end()
        return QIcon(pixmap)

    def refreshIcons(self):
        playing = bool(self.player.playing)
        self.btn_play.setIcon(self.icon(QStyle.SP_MediaPause if playing else QStyle.SP_MediaPlay))
        self.btn_play.setText("Pause" if playing else "Play")
        self.btn_next.setIcon(self.icon(QStyle.SP_MediaSkipForward))
        self.btn_random.setIcon(self.icon(QStyle.SP_BrowserReload))
        self.lbl_volume.setPixmap(self.icon(QStyle.SP_MediaVolume).pixmap(16, 16))

    # Shown before the Commentator starts speaking, which blocks the UI until it is done.
    def showStatus(self, txt):
        self.statusBar().showMessage(txt)
        self.statusBar().repaint()

    def findTrack(self):
        filter = self.inp_find.text()
        if(self.session.start(filter) is None):
            self.showStatus("No track matches '" + filter + "'")
            return
        self.playCurrent()

    def filterTable(self, text):
        self.trackProxy.setFilterText(text)
        self.updateCount()

    def updateCount(self):
        shown, total = self.trackProxy.rowCount(), self.trackModel.rowCount()
        self.lbl_count.setText(str(total) + " tracks" if shown == total else str(shown) + " of " + str(total) + " tracks")

    def playRow(self, index):
        self.session.select(index.data(PATH_ROLE))
        self.playCurrent()

    # Selects the playing track's row and scrolls to it, centered, unless it is already on screen
    # (or hidden by the current search).
    def revealCurrent(self):
        row = self.trackModel.rows.get(self.session.current)
        if(row is None):
            return
        index = self.trackProxy.mapFromSource(self.trackModel.index(row, 0))
        if not(index.isValid()):
            return
        self.tbl_tracks.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        if not(self.tbl_tracks.viewport().rect().contains(self.tbl_tracks.visualRect(index))):
            self.tbl_tracks.scrollTo(index, QAbstractItemView.PositionAtCenter)

    def playCurrent(self):
        self.player.playing = None
        self.play()

    def play(self):
        if(self.session.current is None):
            self.showStatus("No audio files found in the music folder")
            return
        if(self.player.playing is None):
            self.player.play(self.session.current)
            self.showTrack(self.session.current)
            self.trackModel.setCurrent(self.session.current)
            self.revealCurrent()
            self.sld_time.setValue(0)
        elif(self.player.playing):
            self.player.pause()
        else:
            self.player.resume()
        if(self.player.playing):
            self.clock.start()
        else:
            self.clock.stop()
        self.refreshIcons()
        self.updateClock()

    def next(self):
        self.session.next()
        self.playCurrent()

    def randomTrack(self):
        self.session.random()
        self.playCurrent()

    def showTrack(self, track):
        tags = self.session.tracks[track]
        get = lambda k: mkString(tags.get(k, []))
        self.lbl_title.setText(get("title"))
        self.lbl_artistAlbum.setText(" — ".join(v for v in (get("artist"), get("album")) if v))
        self.lbl_genreDate.setText(" · ".join(v for v in (get("genre"), get("date")) if v))
        self.lbl_otherTags.setText("   ".join(k + ": " + get(k) for k in sorted(tags) if k not in MAIN_TAGS))
        pixmap = QPixmap()
        artwork = FileSystem.getArtwork(track)
        if(artwork is not None and pixmap.loadFromData(artwork)):
            self.lbl_art.setPixmap(pixmap.scaled(ART_SIZE, ART_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.artImage = pixmap.toImage()
        else:
            self.lbl_art.setPixmap(QPixmap())
            self.lbl_art.setText("♪")
            self.artImage = None
        self.frm_nowPlaying.setStyleSheet(Theme.nowPlayingStyle(self.artImage))

    def colorSchemeChanged(self, scheme):
        Theme.apply(QApplication.instance())
        self.refreshIcons()
        self.frm_nowPlaying.setStyleSheet(Theme.nowPlayingStyle(self.artImage))

    def updateClock(self):
        if(self.player.playing):
            self.player.refresh()
            length = int(self.player.trackLength)
            if(self.sld_time.maximum() != length):
                self.sld_time.setMaximum(length)
                self.lbl_length.setText(formatTime(length))
            if not(self.seeking):
                self.sld_time.setValue(int(self.player.getPos()))
                self.lbl_pos.setText(formatTime(self.player.getPos()))
        if(self.player.isTrackEnded()):
            print("song ended")
            self.next()

    def startSeek(self):
        self.seeking = True

    def seek(self):
        self.seeking = False
        self.player.setPos(self.sld_time.value())
        self.lbl_pos.setText(formatTime(self.sld_time.value()))

    # Clicks on the groove and arrow keys move the slider without press/release: seek once the value is applied.
    def timeSliderAction(self, action):
        if(action not in (QAbstractSlider.SliderMove, QAbstractSlider.SliderNoAction)):
            QTimer.singleShot(0, self.seek)

    def closeEvent(self, event):
        self.clock.stop()
        self.player.stop()
        self.settings["volume"] = self.player.getVolume()
        self.settings["windowGeometry"] = self.saveGeometry().toBase64().data().decode()
        self.settings["tableHeader"] = self.tbl_tracks.horizontalHeader().saveState().toBase64().data().decode()
        Settings.save(self.settings)
        super().closeEvent(event)
