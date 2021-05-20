import pygame
import mutagen

from FileSystem import getMp3Info


class Player():
    def __init__(self):
        pygame.mixer.init()
        self.playing = None

    def play(self, song):
        mp3 = mutagen.mp3.MP3(song)
        v = self.getVolume()
        pygame.mixer.quit()
        pygame.mixer.init(frequency=mp3.info.sample_rate)
        self.setVolume(v)
        pygame.mixer.music.load(song)
        mp3info = getMp3Info(song)
        print(mp3info)
        #print(mp3.info.sample_rate)
        pygame.mixer.music.play() #frequency=mp3.info.sample_rate
        self.playing = pygame.mixer.music.get_busy() == 1
        self.mp3Length = mp3.info.length
        return mp3info

    def getImage(self, path):
        print(path)
        #print(mutagen.File(path))
        print(mutagen.File(path)['APIC'])
        return mutagen.File(path)['APIC'].data
        '''tags = ID3(path)
        pict = tags.get("APIC:").data
        im = Image.open(BytesIO(pict))
        print('Picture size : ' + str(im.size))'''

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
        '''pygame.mixer.music.stop()
        pygame.mixer.music.set_pos(v)
        pygame.mixer.music.play(0, v)'''