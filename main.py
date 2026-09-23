import sys
from PySide6.QtWidgets import QApplication

import Comentateur
import FileSystem
import Player
import Session
import Settings
import Theme
from MainWindow import MainWindow

# Root folder scanned recursively for audio files (see FileSystem.AUDIO_EXTENSIONS).
MUSIC_PATH = 'C:\\Users\\chari\\Documents\\D\\Music/'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Theme.apply(app)
    settings = Settings.load()
    commentator = Comentateur.Commentator()
    session = Session.PlayerSession(FileSystem.getAllTracks(MUSIC_PATH), commentator)
    player = Player.Player()
    commentator.say("Hello, Any filter to start from? : ")
    session.start()
    window = MainWindow(session, player, commentator, settings)
    window.show()
    sys.exit(app.exec())
