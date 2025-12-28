# Musicana

A radio-like intelligent audio player that creates a unique listening experience by intelligently jumping between tracks using a random walk algorithm. Musicana analyzes your music library's metadata (artist, album, genre, date, etc.) to find natural transitions between songs, similar to how a radio DJ would curate a playlist.

## Features

- 🎵 **Intelligent Track Transitions**: Uses metadata-based random walk algorithm to select the next track
- 🎙️ **Voice Announcements**: Text-to-speech commentator announces transitions and track information
- 🎨 **Dynamic UI**: Album artwork extraction with color-based theming
- 🔍 **Smart Filtering**: Search and filter your music library
- 🎛️ **Full Player Controls**: Play, pause, next, random track selection, volume control, and time slider
- 📊 **Multiple Recommendation Strategies**: 
  - By Album
  - By Artist
  - By Genre
  - By Date/Year
  - By Composer
  - Combined strategies (e.g., same genre + same artist)

## How It Works

Musicana's recommendation engine uses a weighted random selection based on track metadata. Instead of playing songs randomly or in order, it finds connections between tracks:

- **Album-based transitions**: Continue with tracks from the same album
- **Artist-based transitions**: Stay with the same artist or explore their discography
- **Genre-based transitions**: Maintain the musical atmosphere
- **Date-based transitions**: Keep the same era or year
- **Hybrid approaches**: Combine multiple features (e.g., same genre + different artist)

The algorithm maintains a history of recently played tracks to avoid repetition.

## Installation

### Prerequisites

- Python 3.7+
- A music library with MP3 files

### Steps

1. Clone the repository:
```bash
git clone https://github.com/charif-h/Musicana.git
cd Musicana
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your music library path:
   - Copy `.env.example` to `.env`
   - Edit `.env` and set your music library path:
   ```
   MUSICANA_MUSIC_PATH=C:/Path/To/Your/Music/
   ```

## Usage

### Running with GUI

Run the main application with the graphical interface:

```bash
python Windelphi.py
```

The GUI provides:
- Search bar for filtering tracks
- Player controls (play/pause, next, random)
- Volume and time sliders
- Track information display with album artwork
- Dynamic color theming based on album art

### Running CLI Version

For a command-line experience:

```bash
python main.py
```

You'll be prompted to enter a filter to start with, or press Enter to start with any track.

## Project Structure

- **`Windelphi.py`**: Main GUI application using Tkinter
- **`main.py`**: Command-line version of the player
- **`Player.py`**: Audio player class handling pygame mixer operations
- **`FileSystem.py`**: Music library scanner and MP3 metadata extractor
- **`Nexter_RandomWalk.py`**: Smart recommendation algorithm implementation
- **`Comentateur.py`**: Text-to-speech commentator for track transitions
- **`ImageColorExtract.py`**: Album artwork color extraction utilities
- **`requirements.txt`**: Python package dependencies

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```
MUSICANA_MUSIC_PATH=C:/Users/yourname/Music/
```

### Music Library Requirements

- Organize your music in a directory structure
- MP3 files with ID3 tags (title, artist, album, genre, date, etc.)
- Album artwork embedded in MP3 files (optional, for better visual experience)

## Dependencies

- **mutagen**: MP3 metadata reading and manipulation
- **pygame**: Audio playback engine
- **Pillow (PIL)**: Image processing for album artwork
- **chardet**: Character encoding detection
- **pyttsx3**: Text-to-speech engine
- **python-dotenv**: Environment variable management

## TODO / Future Enhancements

- [ ] Link time slider to the interface for seeking
- [ ] Add tracks table view
- [ ] Add more detailed comments in code
- [ ] Audio spectrum analyzer visualization
- [ ] Playlist export functionality
- [ ] User preference learning
- [ ] Support for additional audio formats
- [ ] Web-based interface

## Contributing

Contributions are welcome! The vision for Musicana is to have multiple recommendation agents using different algorithms, allowing each user to choose the agent that best satisfies their needs.

## License

This project is open source. Please check the repository for license details.

## Acknowledgments

Musicana explores the open question of "finding the next track" in recommender systems, aiming to create a more personalized and intelligent music listening experience.
