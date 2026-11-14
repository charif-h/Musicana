# Musicana

A radio-like desktop audio player that decides by itself which track comes next, and announces it like a DJ.

Finding the next track is an open question in the domain of recommender systems. The idea of this project is to offer several **recommendation agents**, each using a different algorithm (random walk over shared tags, album order, genre, era, or how the music actually *sounds*), and to let each user choose the agent that suits them. A spoken **commentator** introduces every transition, and the library can be browsed as a flat table or as grids of albums, artists and genres.

- [Features](#features)
- [Requirements](#requirements)
- [Installation and first run](#installation-and-first-run)
- [Using Musicana](#using-musicana)
- [Display modes](#display-modes)
- [Recommendation agents](#recommendation-agents)
- [The commentator](#the-commentator)
- [Files and settings](#files-and-settings)
- [How your tags are read](#how-your-tags-are-read)
- [Project layout](#project-layout)
- [Extending Musicana](#extending-musicana)
- [Contributing](#contributing)
- [Known limitations and ideas](#known-limitations-and-ideas)

## Features

- Scans a music folder (with sub-folders) in the background and caches the tags, so later launches are fast.
- Plays `.mp3`, `.flac`, `.ogg`, `.wav`, `.m4a` and `.wma` files through [VLC](https://www.videolan.org/vlc/).
- Six recommendation agents choose the next track, including one based on audio analysis (*Sound-alike*).
- A spoken commentator announces each transition; it can be switched off from the menu.
- Four ways to browse the library: a sortable table, or grids of albums, artists and genres, each with a track panel.
- Live search over every tag.
- A now-playing banner with the cover art, the tags, and colours taken from the cover.
- Light and dark theme that follow the system setting.
- Volume, window size, table layout, chosen agent, display mode and commentator choice are remembered between sessions.

## Requirements

- **Python 3.11** (the version the project is developed with).
- **VLC**, installed beforehand. Use the 64-bit build if your Python is 64-bit.
- **Windows.** The project is developed and used on Windows 11. The commentator speaks through Windows SAPI, and the settings and cache live in `%LOCALAPPDATA%`. If the voice cannot be started the app keeps working silently.
- The Python packages listed in [requirements.txt](requirements.txt): `PySide6-Essentials` (interface), `python-vlc` (playback), `mutagen` (tags and cover art), `python-dotenv` (the `.env` file), `comtypes` (speech), and `numpy`, `librosa` and `av` (audio analysis for the Sound-alike agent).

## Installation and first run

```powershell
git clone https://github.com/charif-h/Musicana.git
cd Musicana
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

`main.py` is the only entry point.

**Choosing your music folder.** The folder is resolved in this order:

1. The `MUSICANA_MUSIC_PATH` variable, set in the environment or in a `.env` file next to the code (copy [.env.example](.env.example) to `.env` and edit it; `.env` is ignored by git).
2. The folder saved in the settings by a previous run.
3. Otherwise a folder dialog opens the first time, and your choice is remembered.

You can change the folder at any time with **File > Change music folder…** (`Ctrl+O`). If `MUSICANA_MUSIC_PATH` is set it takes priority again at the next start, and the app reminds you of that when you change the folder.

The first scan reads the tags of every file and shows a *Reading tags* progress bar in the status bar; the window stays usable meanwhile. Later launches only re-read new or modified files.

## Using Musicana

**Window layout**, from top to bottom:

- **Search bar**: typing filters the library live, over *every* tag of every track (title, artist, album, genre, year, composer…), without caring about case. Pressing `Enter` or the **Filter** button starts playing a random track among the matches.
- **Player controls**: **Play / Pause**, **Next** (the agent picks the next track), **Random** (a completely random track), the position slider (click or drag to seek), and the volume slider.
- **Now playing**: the cover art (read from the file's embedded picture), the title, "artist — album", genre and year, and the remaining tags. The panel is tinted with the dominant colour of the cover, and its text stays readable.
- **Library**: the table or one of the grids (see [Display modes](#display-modes)).
- **Status bar**: messages (including what the commentator says), progress bars while scanning tags or analysing audio, the current agent, and the number of tracks (for example `12 of 5795 tracks` while a search is active).

**Playing tracks.**

- Double-click (or press `Enter` on) a track to play it.
- When a track ends, the current agent picks the next one automatically.
- Pressing **Next** or **Random** stops the current track, lets the commentator announce the new one, then starts it. Pressing **Next** or **Random** again, or **Play**, during the announcement cuts it short.
- The playing track is marked with a ▶ and followed in the library, scrolling to it if needed.
- Recently played tracks (the last 20) are not picked again by the agents.

**Menus.**

| Menu | Entries |
| --- | --- |
| **File** | *Change music folder…* (`Ctrl+O`), *Quit* (`Ctrl+Q`) |
| **Commentator** | *Enable commentator* (checkable, remembered) |
| **View** | *All tracks*, *Grouped by album*, *Grouped by artist*, *Grouped by genre* (remembered) |
| **Agent** | the six recommendation agents (remembered); hover an entry for its description |

## Display modes

The **View** menu changes how the library is shown. The search bar filters every mode.

### All tracks

The default: a table with the columns *Title*, *Artist*, *Album*, *Genre* and *Year*. Click a header to sort (tracks missing that tag always come last); the column widths and the sort order are remembered.

### Grouped by album

The albums are shown side by side as a grid of **covers**. Under each cover: the album title in bold, the artist, and the year and track count in a smaller, muted style. Click an album and its tracks (in track-number order) appear in a **panel on the right**; drag the divider to resize it. Double-click an album to play it from its first track.

### Grouped by artist

A grid of artists. Each artist is shown with the **cover of their newest album** (by year), their name, and the number of albums and tracks. The panel on the right lists the artist's tracks **grouped by album**: a heading with a small cover, the album title and its year, then the tracks of that album, until the next album. Albums are in chronological order, oldest first, those without a year last. Double-click an artist to play from their first track.

### Grouped by genre

A grid of coloured **tiles**, with no picture: each tile shows the capitalized name of the genre, written as large as fits the square, and the total number of tracks. The colour is derived from the genre's name, so a genre always keeps the same colour. Click a tile and its tracks appear in the panel on the right as "Artist — Title", ordered by artist, album and track number. Double-click a tile to play from its first track.

### Rules shared by the grouped modes

- Groups are sorted alphabetically, ignoring case. Tracks missing the tag go to an *Unknown album / artist / genre* group, last.
- **Several artists or genres**: a track by "A & B" appears under A *and* under B; a track tagged with two genres appears under both. When you play a track from B's panel, the panel stays on B.
- **Capitalization**: artist names get a capital letter on every word ("marcel khalife" is shown as "Marcel Khalife"); genre names too, including after `-` and `/` ("hip-hop" becomes "Hip-Hop"). The other letters are left as tagged, so "AC/DC" is unchanged.
- **Names that contain a separator** are kept whole: *R&B*, *Rhythm & Blues*, *Drum & Bass*, *Rock & Roll* for genres, and acts such as *Simon & Garfunkel*, *Hall & Oates*, *AC/DC* or *Earth, Wind & Fire* for artists. See [How your tags are read](#how-your-tags-are-read) for why this is needed.
- Covers are the pictures embedded in the audio files, loaded only for the albums currently on screen, so large libraries open quickly. An album without a picture gets a ♪ placeholder.

## Recommendation agents

The **Agent** menu chooses how the next track is picked. The choice is remembered.

| Agent | Behaviour |
| --- | --- |
| **Random walk** (default) | Jumps to a track that shares something with the current one: album, artist, composer, genre, year… The linking feature is drawn at random, with weights (album counts double). Falls back to a random track. |
| **Shuffle** | Any track that was not played recently, at random. |
| **Album journey** | Plays the current album through in track order (by disc, then track number, skipping duplicate copies of a song), then moves to a related album (same artist, genre or year) and starts it from its first track. An album is its name *within its folder*, so compilations stay whole and same-named albums stay apart. |
| **Genre explorer** | Stays in the current genre, moving between its artists, albums and years, and drifting now and then via the artist or the year. |
| **Era explorer** | Stays in the current decade (for example the 1970s), preferring a different artist each time (75% of the time). Tracks without a year fall back to Random walk. |
| **Sound-alike** | Picks among the 10 tracks whose *sound* is closest to the current one (see below). |

Every agent returns the next track together with the **cause** of the link (`album`, `artist`, `genre`, `date`, `sound` or `random`), which the commentator uses to word its announcement.

### Sound-alike and audio analysis

Sound-alike compares tracks by how they sound, not by their tags.

- Each track gets an **audio vector** of about 67 numbers describing timbre (MFCC), harmony (chroma), spectral contrast, brightness, noisiness, loudness and tempo, computed with `librosa` from **30 seconds taken from the middle** of the track.
- The vectors are normalized so every feature weighs the same, and similarity is the cosine similarity between vectors.
- The analysis runs **once per track, in the background, only while Sound-alike is selected**. It uses half of the CPU cores at below-normal priority so playback and the interface stay smooth, and a progress bar shows *Analysing audio n / m* in the status bar.
- Results are saved to the cache in batches, so an interrupted analysis resumes where it stopped. Files that cannot be decoded are remembered and not retried at every launch.
- Until a track has been analysed, Sound-alike falls back to Random walk. The console logs the 10 candidates of each pick with their similarity.

## The commentator

Before each change of track made by **Next**, **Random** or the end of a track, a commentator announces the new track in a sentence that depends on the cause: same album, same artist, same genre, same year, "something that sounds alike", or a generic "time to change". At startup it also says hello. Playing a track yourself (double-click) is not announced.

- The text is shown in the status bar and spoken through Windows speech (SAPI) on its own thread, so the interface never waits. The voice *Zira* is used when installed, otherwise the system default.
- Arabic titles and names are transliterated to Latin letters so that the English voice can read them.
- Switch it off with **Commentator > Enable commentator**. The choice is remembered, and switching it off cuts short what is being said.
- If speech is unavailable, a message is printed in the console and the app continues silently.

## Files and settings

Everything Musicana writes is in `%LOCALAPPDATA%\Musicana` (or `~/Musicana` when `LOCALAPPDATA` is not defined).

**`settings.json`**: your choices. Delete it to go back to the defaults.

| Key | Meaning | Default |
| --- | --- | --- |
| `musicPath` | the music folder | none (asked at first run) |
| `agent` | id of the selected agent (`random-walk`, `shuffle`, `album-journey`, `genre-explorer`, `era-explorer`, `sound-alike`) | `random-walk` |
| `commentator` | commentator enabled | `true` |
| `volume` | 0 to 100 | `100` |
| `displayMode` | `tracks`, `album`, `artist` or `genre` | `tracks` |
| `windowGeometry` | window size and position | none |
| `tableHeader` | column widths and sort of the table | none |

**`cache.json`**: for each audio file, its modification time and size, its tags, and (once analysed) its audio vector. A file is only re-read when its time or size changes. Delete the file to force a full rescan; note that this also discards the audio vectors, so Sound-alike analyses your library again.

Libraries of several folders share the cache: switching folder keeps the entries of the others.

## How your tags are read

Tags are read with `mutagen` and stored as `{tag: [values]}`, all **lowercased** (which makes the search case-insensitive). Every value is also **split on `/`, `,`, `&` and `;`**, so "queen & david bowie" is stored as the two artists `queen` and `david bowie`. The recommendation agents rely on this to detect artists or genres in common.

The side effect is that a name containing one of those characters arrives in pieces: "R&B" is stored as `r` and `b`, "AC/DC" as `ac` and `dc`. The display layer puts the **known** names back together from consecutive values (see `WHOLE_NAMES` in [GroupedTracksModel.py](GroupedTracksModel.py)). It cannot tell such a name from two genuinely separate values: a track really tagged with the two genres "rock" and "roll" would be joined too. If another name shows up split, add it to that list. Names written with "feat.", "ft." or "featuring" are split into several artists as well.

## Project layout

| File | Role |
| --- | --- |
| `main.py` | Entry point: loads the settings, builds the player, the commentator and the window. |
| `MainWindow.py` | The PySide6 window: menus, search, controls, now-playing banner, library views, background tasks. |
| `TrackTableModel.py` | Model of the *All tracks* table, with sorting and the search filter. |
| `GroupedTracksModel.py` | Model of the album, artist and genre modes: groups tracks, splits and capitalizes names, loads covers lazily. Display modes are declared in `MODES`. |
| `AlbumDelegate.py` | How the grids are drawn: album and artist cells, album headings in the artist panel, genre tiles. |
| `Theme.py` | Light and dark theme (QSS), and the colours of the now-playing banner. |
| `Session.py` | The playing session: current track, history, and which agent picks the next one. |
| `Agents.py` | The recommendation agents. |
| `Nexter_RandomWalk.py` | The random-walk logic over shared tags (`TrackFilter`). |
| `Player.py` | Playback through VLC. |
| `Comentateur.py` | The commentator: sentences, speech on its own thread. |
| `FileSystem.py` | Finds the audio files, reads tags and cover art, filters tracks. |
| `LibraryScanner.py` | Scans the library on a background thread and reports progress. |
| `TrackCache.py` | Reads and writes `cache.json`. |
| `AudioFeatures.py` | Computes, stores and loads the audio vectors. |
| `AudioAnalyzer.py` | Runs the audio analysis in background worker processes. |
| `Settings.py` | Reads and writes `settings.json`. |

## Extending Musicana

**A new recommendation agent.** Subclass `Agents.RecommendationAgent`, give it an `id`, a `name` and a `description`, implement `next(tracks, current, history) -> (track, cause)`, and add an instance to `Agents.AGENTS`. It then appears in the *Agent* menu. If it needs the audio vectors, set `needsAudioVectors = True` and implement `setVectors(vectors)`; the window computes the vectors in the background while the agent is selected and passes them in. A `cause` the commentator does not know gets the generic sentence; add a sentence in `Commentator.transition` for a new one.

**A new display mode.** Add an entry to `MODES` in `GroupedTracksModel.py` (an id, a menu label, and the levels to group by), and handle how its groups are described and drawn.

**A name that must not be split.** Add it to `WHOLE_NAMES` in `GroupedTracksModel.py`.

## Contributing

Work happens on feature branches created from `dev`, and pull requests target `dev`; `main` receives the stable merges. Branch names follow `feat/…`, `fix/…`, `chore/…`, `refactor/…`, `docs/…`, and commit messages mention the issue they address (for example `(#46)`). Issues are tracked on GitHub.

## Known limitations and ideas

- Windows only for the commentator (SAPI) and for the default data folder.
- Covers come from the pictures embedded in the audio files; an image file next to the tracks (`folder.jpg`) is not used.
- Names containing `/`, `,` or `&` are recognized from a fixed list (see [How your tags are read](#how-your-tags-are-read)).
- There is no automated test suite yet.
- The code needs more comments.
