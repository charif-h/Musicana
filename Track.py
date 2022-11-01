class Track:
    def __init__(self, title, path, artist="", album="", genre=[], date=0, other={}):
        self.title = title
        self.path = path
        self.artist = artist
        self.album = album
        self.genre = genre
        self.date = date
        self.other = other