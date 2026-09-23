from PySide6.QtCore import QThread, Signal

import AudioFeatures
import FileSystem

class ScanCancelled(Exception):
    pass

# Scans the library off the UI thread; results come back through Qt signals (queued to the UI thread).
class LibraryScanner(QThread):
    progress = Signal(int, int)  # files read, files to read
    loaded = Signal(object, object)  # {path: tags}, {path: audio vector} already in the cache

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

    def run(self):
        try:
            tracks = FileSystem.getAllTracks(self.path, progress=self.report)
        except ScanCancelled:
            return
        self.loaded.emit(tracks, AudioFeatures.loadVectors(tracks))

    def report(self, done, total):
        if(self.isInterruptionRequested()):
            raise ScanCancelled()
        if(done == total or done % 25 == 0):
            self.progress.emit(done, total)
