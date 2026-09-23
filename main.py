import sys
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

import Comentateur
import Player
import Settings
import Theme
from MainWindow import MainWindow

if __name__ == '__main__':
    load_dotenv()  # lets a .env file next to the code set MUSICANA_MUSIC_PATH
    app = QApplication(sys.argv)
    Theme.apply(app)
    settings = Settings.load()
    commentator = Comentateur.Commentator()
    player = Player.Player()
    window = MainWindow(player, commentator, settings)
    window.show()
    musicPath = window.initialMusicFolder()
    if(musicPath is None):
        window.showStatus("No music folder chosen: use File > Change music folder…")
    else:
        window.loadLibrary(musicPath)
    commentator.say("Hello, Any filter to start from? : ")
    sys.exit(app.exec())
