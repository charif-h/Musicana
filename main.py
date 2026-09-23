import sys
from PySide6.QtWidgets import QApplication

import Comentateur
import Player
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
    player = Player.Player()
    window = MainWindow(player, commentator, settings)
    window.show()
    window.loadLibrary(MUSIC_PATH)
    commentator.say("Hello, Any filter to start from? : ")
    sys.exit(app.exec())
