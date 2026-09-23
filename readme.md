# Musicana project
A radio-like audio player that jumps between tracks in a semi-random way (using a random step algorithm).
Find the next track is an open question in recommender systems domain. 
The final idea of the this project is to have many recommendations agents using different algorithms, and let each user chooses the agent that satisfies his needs.

# How to use it?
Root folder with subfolders getallMp3

Playback uses [VLC](https://www.videolan.org/vlc/): install it first (64-bit if your Python is 64-bit), then `pip install -r requirements.txt`.

Set `MUSIC_PATH` in `main.py` to your music root folder, then start the Tkinter GUI with:

```
python main.py
```

`main.py` is the only entry point; the PySide6 GUI itself lives in `MainWindow.py` (library table in `TrackTableModel.py`, light/dark theme in `Theme.py`).

Scanned tags are cached in `%LOCALAPPDATA%\Musicana\cache.json`, so later launches only re-read new or changed files. Delete that file to force a full rescan.

**つづく**

# TODO
- Comments
- audio analyser# Musicana
