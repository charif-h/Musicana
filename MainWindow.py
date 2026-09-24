import os

from PySide6.QtCore import QByteArray, QItemSelectionModel, Qt, QTimer, Signal
from PySide6.QtGui import QActionGroup, QGuiApplication, QIcon, QKeySequence, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSlider, QApplication, QFileDialog, QFrame, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton, QSlider,
                               QStyle, QTableView, QVBoxLayout, QWidget)

import Agents
import AudioFeatures
import FileSystem
import Session
import Settings
import Theme
from AudioAnalyzer import AudioAnalyzer
from LibraryScanner import LibraryScanner
from TrackTableModel import PATH_ROLE, TrackFilterProxy, TrackTableModel

ART_SIZE = 200
MUSIC_PATH_VARIABLE = "MUSICANA_MUSIC_PATH"
MAIN_TAGS = ("title", "artist", "album", "genre", "date")

def formatTime(seconds):
    seconds = int(seconds)
    return str(seconds // 60) + ":" + str(seconds % 60).zfill(2)

def mkString(values, sep=" / "):
    return sep.join(values)

class MainWindow(QMainWindow):
    announced = Signal(int)  # emitted from the Commentator's thread; delivered on the UI thread

    def __init__(self, player, commentator, settings):
        super().__init__()
        self.transition = 0  # id of the latest transition: an older announcement finishing is ignored
        self.agent = Agents.byId(settings["agent"])
        self.session = Session.PlayerSession({}, commentator, agent=self.agent)  # until loadLibrary()/setLibrary()
        self.scanner = None
        self.analyzer = None
        self.vectors = {}  # audio vectors of the library's tracks, for agents that need them
        self.player = player
        self.commentator = commentator
        self.settings = settings
        self.setWindowTitle("Musicana")
        self.resize(960, 720)
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Change &music folder…", QKeySequence.Open, self.changeMusicFolder)
        fileMenu.addSeparator()
        fileMenu.addAction("&Quit", QKeySequence("Ctrl+Q"), self.close)
        commentatorMenu = self.menuBar().addMenu("&Commentator")
        self.act_commentator = commentatorMenu.addAction("&Enable commentator")
        self.act_commentator.setCheckable(True)
        self.act_commentator.setChecked(bool(settings["commentator"]))
        self.act_commentator.toggled.connect(self.setCommentatorEnabled)
        agentMenu = self.menuBar().addMenu("&Agent")
        agentMenu.setToolTipsVisible(True)
        agentGroup = QActionGroup(self)
        for agent in Agents.AGENTS:
            action = agentMenu.addAction(agent.name, lambda agent=agent: self.setAgent(agent))
            action.setCheckable(True)
            action.setChecked(agent is self.agent)
            action.setToolTip(agent.description)
            agentGroup.addAction(action)

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
        self.trackModel = TrackTableModel({}, self)
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

        self.prg_scan = QProgressBar()
        self.prg_scan.setMaximumWidth(220)
        self.prg_scan.setFormat("Reading tags %v / %m")
        self.prg_scan.hide()
        self.statusBar().addPermanentWidget(self.prg_scan)
        self.prg_audio = QProgressBar()
        self.prg_audio.setMaximumWidth(240)
        self.prg_audio.setFormat("Analysing audio %v / %m")
        self.prg_audio.hide()
        self.statusBar().addPermanentWidget(self.prg_audio)
        self.lbl_agent = QLabel()
        self.statusBar().addPermanentWidget(self.lbl_agent)
        self.lbl_count = QLabel()
        self.statusBar().addPermanentWidget(self.lbl_count)
        self.showAgent()
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
        self.announced.connect(self.playAnnounced)

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

    def showStatus(self, txt):
        self.statusBar().showMessage(txt)

    # MUSICANA_MUSIC_PATH (environment or .env), else the folder saved in the settings, else ask once.
    def initialMusicFolder(self):
        fromEnvironment = os.environ.get(MUSIC_PATH_VARIABLE)
        if(fromEnvironment):
            if(os.path.isdir(fromEnvironment)):
                return fromEnvironment
            print(MUSIC_PATH_VARIABLE, "is not a folder:", fromEnvironment)
        if(self.settings["musicPath"] and os.path.isdir(self.settings["musicPath"])):
            return self.settings["musicPath"]
        return self.chooseMusicFolder()

    # Returns the chosen folder (remembered in the settings), or None if the dialog was cancelled.
    def chooseMusicFolder(self):
        start = self.settings["musicPath"] or os.path.join(os.path.expanduser("~"), "Music")
        path = QFileDialog.getExistingDirectory(self, "Choose your music folder", start)
        if not(path):
            return None
        self.settings["musicPath"] = path
        Settings.save(self.settings)
        return path

    def changeMusicFolder(self):
        path = self.chooseMusicFolder()
        if(path is None):
            return
        self.loadLibrary(path)
        if(os.environ.get(MUSIC_PATH_VARIABLE)):
            self.showStatus("Note: " + MUSIC_PATH_VARIABLE + " is set and will be used again at the next start")

    # The window stays usable while the scan runs on a background thread.
    def loadLibrary(self, path):
        self.stopAnalysis()
        self.clock.stop()
        self.player.stop()
        self.refreshIcons()
        self.setLibraryControlsEnabled(False)
        self.prg_scan.setRange(0, 0)  # busy until the scan knows how many files it must read
        self.prg_scan.show()
        self.showStatus("Scanning " + path + "…")
        self.scanner = LibraryScanner(path, self)
        self.scanner.progress.connect(self.scanProgress)
        self.scanner.loaded.connect(self.setLibrary)
        self.scanner.start()

    def scanProgress(self, done, total):
        self.prg_scan.setRange(0, total)
        self.prg_scan.setValue(done)

    def setLibrary(self, tracks, vectors=None):
        self.prg_scan.hide()
        self.session = Session.PlayerSession(tracks, self.commentator, agent=self.agent)
        self.session.start()
        previousModel = self.trackModel
        self.trackModel = TrackTableModel(tracks, self)
        header = self.tbl_tracks.horizontalHeader()
        self.trackModel.sort(header.sortIndicatorSection(), header.sortIndicatorOrder())
        self.trackProxy.setSourceModel(self.trackModel)
        previousModel.deleteLater()
        self.updateCount()
        self.setLibraryControlsEnabled(True)
        self.showStatus(str(len(tracks)) + " tracks loaded" if tracks else "No audio files found in the music folder")
        self.vectors = vectors if vectors is not None else AudioFeatures.loadVectors(tracks)
        self.shareVectors()
        self.startAnalysisIfNeeded()

    def shareVectors(self):
        for agent in Agents.AGENTS:
            if(getattr(agent, "needsAudioVectors", False)):
                agent.setVectors(self.vectors)

    # Analyses the tracks that have no audio vector yet, only while an agent that needs them is selected.
    def startAnalysisIfNeeded(self):
        if not(getattr(self.agent, "needsAudioVectors", False)):
            return
        if(self.analyzer is not None and self.analyzer.isRunning()):
            return
        todo = [p for p in self.session.tracks if p not in self.vectors]
        if not(todo):
            return
        self.prg_audio.setRange(0, len(todo))
        self.prg_audio.setValue(0)
        self.prg_audio.show()
        self.showStatus("Analysing the sound of " + str(len(todo)) + " tracks in the background…")
        self.analyzer = AudioAnalyzer(todo, self)
        self.analyzer.progress.connect(lambda done, total: self.prg_audio.setValue(done))
        self.analyzer.analysed.connect(self.vectorsAnalysed)
        self.analyzer.finished.connect(self.analysisFinished)
        self.analyzer.start()

    def vectorsAnalysed(self, batch):
        self.vectors.update(batch)
        self.shareVectors()

    def analysisFinished(self):
        self.prg_audio.hide()
        if(self.session.tracks and all(p in self.vectors for p in self.session.tracks)):
            skipped = sum(1 for v in self.vectors.values() if v is None)
            self.showStatus("Audio analysis complete: " + str(len(self.vectors) - skipped) + " tracks"
                            + (" (" + str(skipped) + " could not be decoded)" if skipped else ""))

    def stopAnalysis(self):
        if(self.analyzer is not None and self.analyzer.isRunning()):
            self.analyzer.requestInterruption()
            self.analyzer.wait()
        self.prg_audio.hide()

    def setLibraryControlsEnabled(self, enabled):
        for w in (self.inp_find, self.btn_find, self.btn_play, self.btn_next, self.btn_random, self.sld_time, self.tbl_tracks):
            w.setEnabled(enabled)

    def setCommentatorEnabled(self, enabled):
        self.commentator.setEnabled(enabled)
        self.settings["commentator"] = enabled
        Settings.save(self.settings)
        self.showStatus("Commentator " + ("enabled" if enabled else "disabled"))

    def setAgent(self, agent):
        self.agent = agent
        self.session.agent = agent
        self.settings["agent"] = agent.id
        self.showAgent()
        self.showStatus("Next tracks are now chosen by: " + agent.name)
        self.startAnalysisIfNeeded()

    def showAgent(self):
        self.lbl_agent.setText("Agent: " + self.agent.name)
        self.lbl_agent.setToolTip(self.agent.description)

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
            self.transition += 1  # starting a track overrides any announcement still in progress
            self.commentator.cancel()
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
        self.announce(self.session.next)

    def randomTrack(self):
        self.announce(self.session.random)

    # DJ style: the old track stops, the Commentator announces the new one, then it starts playing.
    # Next/Random again (or Play) during the announcement cuts it short.
    def announce(self, move):
        self.transition += 1
        transition = self.transition
        self.commentator.cancel()
        self.clock.stop()
        self.player.stop()
        self.refreshIcons()
        move(onDone=lambda: self.announced.emit(transition))

    def playAnnounced(self, transition):
        if(transition == self.transition):
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
        self.stopAnalysis()
        if(self.scanner is not None and self.scanner.isRunning()):
            self.scanner.requestInterruption()
            self.scanner.wait()
        self.clock.stop()
        self.player.stop()
        self.commentator.shutdown()
        self.settings["volume"] = self.player.getVolume()
        self.settings["windowGeometry"] = self.saveGeometry().toBase64().data().decode()
        self.settings["tableHeader"] = self.tbl_tracks.horizontalHeader().saveState().toBase64().data().decode()
        Settings.save(self.settings)
        super().closeEvent(event)
