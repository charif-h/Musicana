from Windelphi import Application

# Root folder scanned recursively for .mp3 files.
MUSIC_PATH = 'C:\\Users\\chari\\Documents\\D\\Music/'

if __name__ == '__main__':
    Application(MUSIC_PATH).run()
