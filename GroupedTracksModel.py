from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap, QStandardItem, QStandardItemModel

import FileSystem
from TrackTableModel import PATH_ROLE

ART_ROLE = Qt.UserRole + 1  # path of the track whose artwork stands for a group (albums)
THUMB_SIZE = 56

# Display modes: (id, menu label, levels from the top group down to the tracks).
MODES = (("tracks", "All &tracks", None),
         ("album", "Grouped by &album", ("album",)),
         ("artist", "Grouped by a&rtist", ("artist", "album")),
         ("genre", "Grouped by &genre", ("genre", "artist")))

UNKNOWN = {"album": "Unknown album", "artist": "Unknown artist", "genre": "Unknown genre"}

def tagText(tags, key):
    return " / ".join(tags.get(key, []))

def trackNumber(tags):
    text = tagText(tags, "tracknumber").split("/")[0].strip()
    return int(text) if text.isdigit() else 0

# Sorts case-insensitively, with the group missing its tag last.
def groupKey(name):
    return (name == "", name.lower())

# Groups, albums and tracks as a tree. Artwork is read lazily: only for the albums the view actually draws.
class GroupedTracksModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = {}  # track path -> its item
        self.current = None
        self.thumbnails = {}  # track path -> QIcon (empty when it has no artwork)
        self.boldFont = QFont()
        self.boldFont.setBold(True)

    def build(self, tracks, paths, levels):
        self.clear()
        self.items = {}
        self.thumbnails = {}
        self.fill(self.invisibleRootItem(), tracks, paths, levels)
        self.setCurrent(self.current)

    # One level of groups under `parent`; the deepest level holds the tracks.
    def fill(self, parent, tracks, paths, levels):
        if not(levels):
            for path in sorted(paths, key=lambda p: (trackNumber(tracks[p]), tagText(tracks[p], "title").lower())):
                parent.appendRow(self.trackItem(tracks[path], path))
            return
        key, rest = levels[0], levels[1:]
        groups = {}
        for path in paths:
            groups.setdefault(tagText(tracks[path], key), []).append(path)
        for name in sorted(groups, key=groupKey):
            members = groups[name]
            item = QStandardItem()
            item.setEditable(False)
            if(key == "album"):
                self.describeAlbum(item, name, tracks, members)
            else:
                item.setText((name or UNKNOWN[key]) + "  (" + str(len(members)) + ")")
                item.setFont(self.boldFont)
            parent.appendRow(item)
            self.fill(item, tracks, members, rest)

    def describeAlbum(self, item, name, tracks, members):
        first = tracks[members[0]]
        artists = sorted({tagText(tracks[p], "artist") for p in members} - {""})
        artist = artists[0] if len(artists) == 1 else ("Various artists" if artists else "")
        years = sorted({tagText(tracks[p], "date")[:4] for p in members} - {""})
        count = str(len(members)) + (" track" if len(members) == 1 else " tracks")
        details = " · ".join(v for v in (artist, years[0] if years else "", count) if v)
        item.setText((name or UNKNOWN["album"]) + "\n" + details)
        item.setData(members[0], ART_ROLE)
        item.setSizeHint(QSize(0, THUMB_SIZE + 8))

    def trackItem(self, tags, path):
        item = QStandardItem()
        item.setEditable(False)
        number = trackNumber(tags)
        item.setText((str(number).zfill(2) + "  " if number else "") + (tagText(tags, "title") or path))
        item.setToolTip(path)
        item.setData(path, PATH_ROLE)
        self.items[path] = item
        return item

    def thumbnail(self, path):
        if(path not in self.thumbnails):
            icon = QIcon()
            pixmap = QPixmap()
            try:
                artwork = FileSystem.getArtwork(path)
            except Exception:  # unreadable or vanished file: no thumbnail
                artwork = None
            if(artwork is not None and pixmap.loadFromData(artwork)):
                icon = QIcon(pixmap.scaled(THUMB_SIZE, THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.thumbnails[path] = icon
        return self.thumbnails[path]

    def data(self, index, role=Qt.DisplayRole):
        if(role == Qt.DecorationRole):
            art = self.itemFromIndex(index).data(ART_ROLE)  # not index.data(): that would call this method again
            if(art is not None):
                return self.thumbnail(art)
        return super().data(index, role)

    def setCurrent(self, path):
        for p, marked in ((self.current, False), (path, True)):
            item = self.items.get(p)
            if(item is not None):
                text = item.text()
                if(text.startswith("▶  ")):
                    text = text[3:]
                item.setText("▶  " + text if marked else text)
                item.setFont(self.boldFont if marked else QFont())
        self.current = path
