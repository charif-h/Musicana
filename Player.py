import pygame
import mutagen


class Player():
    def __init__(self):
        pygame.mixer.init()
        self.playing = None

    def play(self, song):
        audio = mutagen.File(song)
        v = self.getVolume()
        pygame.mixer.quit()
        pygame.mixer.init(frequency=audio.info.sample_rate)
        self.setVolume(v)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        self.playing = pygame.mixer.music.get_busy() == 1
        self.trackLength = audio.info.length

    def pause(self):
        pygame.mixer.music.pause()
        self.playing = False

    def resume(self):
        pygame.mixer.music.unpause()
        self.playing = True

    def isTrackEnded(self):
        return not pygame.mixer.music.get_busy()

    def getVolume(self):
        return pygame.mixer.music.get_volume()*100

    def setVolume(self, v):
        pygame.mixer.music.set_volume(v)

    def getPos(self):
        return pygame.mixer.music.get_pos()/1000

    def setPos(self, v):
        pass  # seeking is not supported by pygame.mixer; see M3 (python-vlc)
