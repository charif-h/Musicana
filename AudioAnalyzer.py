import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from PySide6.QtCore import QThread, Signal

import AudioFeatures
import TrackCache

# Computes the audio vectors of `paths` in worker processes (half the cores, below-normal priority, so
# playback and the UI stay smooth), saving them to the cache in batches so an interrupted run resumes.
# The cache is written by a helper process too: serializing it here would hold the GIL and stall the UI.
class AudioAnalyzer(QThread):
    progress = Signal(int, int)  # analysed, to analyse
    analysed = Signal(object)    # {path: vector}, one batch at a time

    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self):
        done = 0
        batch = {}
        lastSave = time.time()
        workers = max(1, (os.cpu_count() or 2) // 2)
        executor = ProcessPoolExecutor(max_workers=workers, initializer=AudioFeatures.initWorker)
        self.saver = ProcessPoolExecutor(max_workers=1)  # one writer, so batches are saved in order
        try:
            futures = [executor.submit(AudioFeatures.analyse, p) for p in self.paths]
            for future in as_completed(futures):
                if(self.isInterruptionRequested()):
                    break
                done += 1
                result = future.result()
                batch[result[0]] = result[1]
                if(result[1] is None):
                    print("Audio analysis skipped", result[0], ":", result[2])
                if(len(batch) >= 200 or time.time() - lastSave > 30 or done == len(self.paths)):
                    self.flush(batch)
                    batch = {}
                    lastSave = time.time()
                self.progress.emit(done, len(self.paths))
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
            self.flush(batch)
            self.saver.shutdown(wait=True)  # the last batches reach the cache before the thread ends

    def flush(self, batch):
        if(batch):
            self.saver.submit(AudioFeatures.saveVectors, batch, TrackCache.defaultPath())
            self.analysed.emit(batch)
