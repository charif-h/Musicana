from Windelphi import Application

# Root folder scanned recursively for audio files (see FileSystem.AUDIO_EXTENSIONS).
MUSIC_PATH = 'C:\\Users\\chari\\Documents\\D\\Music/'

if __name__ == '__main__':
    Application(MUSIC_PATH).run()
