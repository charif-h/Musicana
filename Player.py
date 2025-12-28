"""
Audio player module for music playback.

This module provides a Player class that wraps pygame's mixer functionality
to handle MP3 playback with volume control and position tracking.
"""

import pygame
import mutagen

from FileSystem import getMp3Info


class Player():
    """
    Audio player for MP3 files using pygame mixer.
    
    Handles playback, pause/resume, volume control, and track position.
    Automatically adjusts sample rate for each track to ensure correct playback speed.
    """
    
    def __init__(self):
        """Initialize the player with pygame mixer."""
        pygame.mixer.init()
        self.playing = None  # None: no track, True: playing, False: paused

    def play(self, song):
        """
        Load and play an MP3 file.
        
        Args:
            song (str): Path to the MP3 file to play
            
        Returns:
            dict: MP3 metadata (ID3 tags)
        """
        mp3 = mutagen.mp3.MP3(song)
        v = self.getVolume()
        
        # Reinitialize mixer with the correct sample rate for this track
        pygame.mixer.quit()
        pygame.mixer.init(frequency=mp3.info.sample_rate)
        self.setVolume(v)
        
        pygame.mixer.music.load(song)
        mp3info = getMp3Info(song)
        
        pygame.mixer.music.play()
        self.playing = pygame.mixer.music.get_busy() == 1
        self.mp3Length = mp3.info.length
        
        return mp3info

    def pause(self):
        """Pause the currently playing track."""
        pygame.mixer.music.pause()
        self.playing = False

    def resume(self):
        """Resume the paused track."""
        pygame.mixer.music.unpause()
        self.playing = True

    def stop(self):
        """Stop playback completely."""
        pygame.mixer.music.stop()
        self.playing = None

    def isTrackEnded(self):
        """
        Check if the current track has finished playing.
        
        Returns:
            bool: True if track has ended, False otherwise
        """
        return not pygame.mixer.music.get_busy()

    def getVolume(self):
        """
        Get current volume level.
        
        Returns:
            float: Volume level (0-100)
        """
        return pygame.mixer.music.get_volume() * 100

    def setVolume(self, v):
        """
        Set volume level.
        
        Args:
            v (float): Volume level (0.0-1.0)
        """
        pygame.mixer.music.set_volume(v)

    def getPos(self):
        """
        Get current playback position.
        
        Returns:
            float: Position in seconds
        """
        return pygame.mixer.music.get_pos() / 1000

    def setPos(self, v):
        """
        Set playback position (currently not implemented).
        
        Args:
            v (float): Desired position in seconds
            
        Note:
            Seeking is not currently supported by pygame mixer for MP3 files.
            This method is a placeholder for future implementation.
        """
        # TODO: Implement seeking functionality
        # pygame.mixer.music doesn't support reliable seeking for MP3
        pass