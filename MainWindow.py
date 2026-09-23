from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QPushButton, QSlider, QStyle, QTableView, QVBoxLayout, QWidget)

ART_SIZE = 200

def formatTime(seconds):
    seconds = int(seconds)
    return str(seconds // 60) + ":" + str(seconds % 60).zfill(2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.btn_play = QPushButton(self.icon(QStyle.SP_MediaPlay), "Play")
        self.btn_next = QPushButton(self.icon(QStyle.SP_MediaSkipForward), "Next")
        self.btn_random = QPushButton(self.icon(QStyle.SP_BrowserReload), "Random")
        self.lbl_pos = QLabel(formatTime(0))
        self.sld_time = QSlider(Qt.Horizontal)
        self.lbl_length = QLabel(formatTime(0))
        lbl_volume = QLabel()
        lbl_volume.setPixmap(self.icon(QStyle.SP_MediaVolume).pixmap(16, 16))
        self.sld_volume = QSlider(Qt.Horizontal)
        self.sld_volume.setRange(0, 100)
        self.sld_volume.setFixedWidth(120)
        for w in (self.btn_play, self.btn_next, self.btn_random, self.lbl_pos):
            controls.addWidget(w)
        controls.addWidget(self.sld_time, 1)
        for w in (self.lbl_length, lbl_volume, self.sld_volume):
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
        self.tbl_tracks = QTableView()
        layout.addWidget(self.tbl_tracks, 1)

        self.statusBar().showMessage("on the way…")

    def icon(self, standardPixmap):
        return self.style().standardIcon(standardPixmap)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
