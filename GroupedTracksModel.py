import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap, QStandardItem, QStandardItemModel

import FileSystem
from TrackTableModel import PATH_ROLE

ART_ROLE = Qt.UserRole + 1  # path of the track whose artwork stands for a group (albums)
ALBUM_INFO_ROLE = Qt.UserRole + 2  # {"name", "artist", "year", "count"} of an album, for the grid's caption
COVER_SIZE = 160  # album cover in the grid; also the size the artwork is scaled to once

# Display modes: (id, menu label, levels from the top group down to the tracks).
MODES = (("tracks", "All &tracks", None),
         ("album", "Grouped by &album", ("album",)),
         ("artist", "Grouped by a&rtist", ("artist", "album")),
         ("genre", "Grouped by &genre", ("genre",)))

UNKNOWN = {"album": "Unknown album", "artist": "Unknown artist", "genre": "Unknown genre"}

# Tags that name several people or styles at once. Each name gets its own group, and the track is listed
# under every one of them.
SEPARATORS = {
    "artist": re.compile(r"\s*;\s*|\s+/\s+|\s+&\s+|\s+(?:feat\.?|ft\.?|featuring)\s+", re.IGNORECASE),
    "genre": re.compile(r"\s*[;,]\s*|\s+/\s+|\s+&\s+"),
}

# Genres whose name contains "&": kept whole instead of being read as two genres ("R&B" is always written "R&B").
PROTECTED_GENRES = re.compile(r"(?<!\w)(?:r\s*&\s*b|rhythm\s*&\s*blues|drum\s*&\s*bass|rock\s*&\s*roll)(?!\w)", re.IGNORECASE)
RHYTHM_AND_BLUES = re.compile(r"r\s*&\s*b", re.IGNORECASE)
HIDDEN_AMPERSAND = chr(0)

# Acts whose name contains a separator: kept whole instead of being read as two artists.
SINGLE_ARTISTS = {"simon & garfunkel", "hall & oates", "crosby, stills & nash", "florence & the machine",
                  "mumford & sons", "brooks & dunn", "sly & the family stone", "ike & tina turner"}

# The first letter of each word of an artist name is capitalized ("marcel khalife" -> "Marcel Khalife"); the
# other letters are left as tagged, so "AC/DC" and "McCartney" survive.
WORD_START = re.compile(r"(^|\s)(\S)")
GENRE_WORD_START = re.compile(r"(^|[\s/-])(\S)")  # genres also start a word after "-" and "/" ("hip-hop" -> "Hip-Hop")

def capitalized(pattern, text):
    return pattern.sub(lambda m: m.group(1) + m.group(2).upper(), text)

# Splits an artist or genre tag value into its names.
def splitValue(key, value):
    if(key == "artist"):
        return [value] if(value.lower() in SINGLE_ARTISTS) else SEPARATORS[key].split(value)
    hidden = PROTECTED_GENRES.sub(lambda m: m.group(0).replace("&", HIDDEN_AMPERSAND), value)
    return [part.replace(HIDDEN_AMPERSAND, "&") for part in SEPARATORS[key].split(hidden)]

def tagText(tags, key):
    return " / ".join(tags.get(key, []))

# The group names a track belongs to for this tag: several for a collaboration or a multi-genre track.
def groupNames(tags, key):
    if(key not in SEPARATORS):
        return [tagText(tags, key)]
    names = []
    for value in tags.get(key, []):
        for part in splitValue(key, value):
            part = part.strip()
            if(key == "artist"):
                part = capitalized(WORD_START, part)
            elif(RHYTHM_AND_BLUES.fullmatch(part)):
                part = "R&B"
            else:
                part = capitalized(GENRE_WORD_START, part)
            if(part and part not in names):
                names.append(part)
    return names or [""]

# The artists of a track as one label, for lists that mix artists.
def artistLabel(tags):
    return ", ".join(n for n in groupNames(tags, "artist") if n) or UNKNOWN["artist"]

def trackNumber(tags):
    text = tagText(tags, "tracknumber").split("/")[0].strip()
    return int(text) if text.isdigit() else 0

# The group an item sits in at the first level (an album, artist or genre), or the item itself.
def topLevel(item):
    while(item.parent() is not None):
        item = item.parent()
    return item

# The year of the tracks' release dates: the oldest by default, the newest with newest=True ("" if undated).
def yearOf(tracks, members, newest=False):
    years = {tagText(tracks[p], "date")[:4] for p in members} - {""}
    return (max(years) if newest else min(years)) if years else ""

# Sorts case-insensitively, with the group missing its tag last.
def groupKey(name):
    return (name == "", name.lower())

# Groups, albums and tracks as a tree. Artwork is read lazily: only for the albums the view actually draws.
class GroupedTracksModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = {}  # track path -> its items (several when the track is listed under more than one group)
        self.current = None
        self.thumbnails = {}  # track path -> QIcon (empty when it has no artwork)
        self.boldFont = QFont()
        self.boldFont.setBold(True)
        self.listArtists = False

    def build(self, tracks, paths, levels):
        self.clear()
        self.items = {}
        self.thumbnails = {}
        self.listArtists = bool(levels) and levels[0] == "genre"  # a genre's tracks come from many artists
        self.fill(self.invisibleRootItem(), tracks, paths, levels)
        self.setCurrent(self.current)

    # One level of groups under `parent`; the deepest level holds the tracks. `top` is true for the first level.
    def fill(self, parent, tracks, paths, levels, top=True):
        if not(levels):
            if(self.listArtists):  # by artist, then album, then track
                key = lambda p: (artistLabel(tracks[p]).lower(), tagText(tracks[p], "album").lower(),
                                 trackNumber(tracks[p]), tagText(tracks[p], "title").lower())
            else:
                key = lambda p: (trackNumber(tracks[p]), tagText(tracks[p], "title").lower())
            for path in sorted(paths, key=key):
                parent.appendRow(self.trackItem(tracks[path], path))
            return
        key, rest = levels[0], levels[1:]
        groups = {}
        for path in paths:
            for name in groupNames(tracks[path], key):
                groups.setdefault(name, []).append(path)
        if(key == "album" and not top):  # an artist's discography: oldest first, undated last
            order = sorted(groups, key=lambda n: (yearOf(tracks, groups[n]) == "", yearOf(tracks, groups[n]), n.lower()))
        else:
            order = sorted(groups, key=groupKey)
        for name in order:
            members = groups[name]
            item = QStandardItem()
            item.setEditable(False)
            if(key == "album"):
                self.describeAlbum(item, name, tracks, members, withArtist=top)
            elif(key == "artist" and "album" in rest):
                self.describeArtist(item, name, tracks, members)
            else:
                self.describeGenre(item, name, members)
            parent.appendRow(item)
            self.fill(item, tracks, members, rest, top=False)

    def describeAlbum(self, item, name, tracks, members, withArtist=True):
        artists = sorted({a for p in members for a in groupNames(tracks[p], "artist")} - {""})
        artist = artists[0] if len(artists) == 1 else ("Various artists" if artists else "")
        years = sorted({tagText(tracks[p], "date")[:4] for p in members} - {""})
        count = str(len(members)) + (" track" if len(members) == 1 else " tracks")
        name = name or UNKNOWN["album"]
        year = years[0] if years else ""
        item.setText(name + "\n" + " · ".join(v for v in ((artist if withArtist else ""), year, count) if v))
        item.setToolTip(item.text())
        item.setData({"name": name, "artist": artist, "year": year, "count": count}, ALBUM_INFO_ROLE)
        item.setData(members[0], ART_ROLE)

    # An artist, shown with the cover of the newest of their albums.
    def describeArtist(self, item, name, tracks, members):
        byAlbum = {}
        for p in members:
            for album in groupNames(tracks[p], "album"):
                byAlbum.setdefault(album, []).append(p)
        newest = max(sorted(byAlbum, key=groupKey), key=lambda a: (yearOf(tracks, byAlbum[a], newest=True), a != ""))
        name = name or UNKNOWN["artist"]
        count = str(len(byAlbum)) + (" album" if len(byAlbum) == 1 else " albums")
        count += " · " + str(len(members)) + (" track" if len(members) == 1 else " tracks")
        item.setText(name + "\n" + count)
        item.setToolTip(item.text())
        item.setData({"name": name, "artist": "", "year": "", "count": count}, ALBUM_INFO_ROLE)
        item.setData(byAlbum[newest][0], ART_ROLE)
        item.setFont(self.boldFont)

    # A genre, drawn as a coloured tile with its name and track count (no artwork).
    def describeGenre(self, item, name, members):
        count = format(len(members), ",") + (" track" if len(members) == 1 else " tracks")
        shown = name or UNKNOWN["genre"]
        item.setText(shown + "\n" + count)
        item.setToolTip(item.text())
        item.setData({"name": shown, "artist": "", "year": "", "count": count, "unknown": name == ""}, ALBUM_INFO_ROLE)

    def trackItem(self, tags, path):
        item = QStandardItem()
        item.setEditable(False)
        number = trackNumber(tags)
        title = tagText(tags, "title") or path
        if(self.listArtists):
            item.setText(artistLabel(tags) + " — " + title)
        else:
            item.setText((str(number).zfill(2) + "  " if number else "") + title)
        item.setToolTip(path)
        item.setData(path, PATH_ROLE)
        self.items.setdefault(path, []).append(item)
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
                icon = QIcon(pixmap.scaled(COVER_SIZE, COVER_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
            for item in self.items.get(p, []):
                text = item.text()
                if(text.startswith("▶  ")):
                    text = text[3:]
                item.setText("▶  " + text if marked else text)
                item.setFont(self.boldFont if marked else QFont())
        self.current = path
