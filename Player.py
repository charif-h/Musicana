import vlc
import mutagen


class Player():
    def __init__(self):
        self.instance = vlc.Instance("--no-video", "--quiet")
        if(self.instance is None):
            raise RuntimeError("libVLC could not be loaded: install VLC (64-bit, same bitness as Python)")
        self.mediaPlayer = self.instance.media_player_new()
        self.volume = 100
        self.playing = None

    def play(self, song):
        self.mediaPlayer.set_media(self.instance.media_new_path(song))
        self.mediaPlayer.play()
        self.mediaPlayer.audio_set_volume(self.volume)
        self.playing = True
        self.trackLength = mutagen.File(song).info.length

    def pause(self):
        self.mediaPlayer.set_pause(1)
        self.playing = False

    def resume(self):
        self.mediaPlayer.set_pause(0)
        self.playing = True

    def isTrackEnded(self):
        return self.mediaPlayer.get_state() in (vlc.State.Ended, vlc.State.Error)

    def getVolume(self):
        return self.volume

    def setVolume(self, v):
        self.volume = int(v*100)
        self.mediaPlayer.audio_set_volume(self.volume)

    def getPos(self):
        return max(self.mediaPlayer.get_time(), 0)/1000

    def setPos(self, v):
        self.mediaPlayer.set_time(int(v*1000))
