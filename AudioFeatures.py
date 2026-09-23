import os

import TrackCache

# Bump when the features change, so every track is analysed again.
VERSION = 1
SAMPLE_RATE = 22050
EXCERPT_SECONDS = 30

# 30 s of mono audio from the middle of the track (intros and fades say little about its sound).
def decodeExcerpt(path, duration):
    import av
    import numpy
    start = max(0.0, duration / 2 - EXCERPT_SECONDS / 2)
    chunks = []
    with av.open(path) as container:
        stream = container.streams.audio[0]
        if(start > 0):
            container.seek(int(start * av.time_base))
        resampler = av.AudioResampler(format="flt", layout="mono", rate=SAMPLE_RATE)
        needed = EXCERPT_SECONDS * SAMPLE_RATE
        for frame in container.decode(stream):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
            if(sum(len(c) for c in chunks) >= needed):
                break
    samples = numpy.concatenate(chunks) if chunks else numpy.zeros(0, dtype="float32")
    return samples[:EXCERPT_SECONDS * SAMPLE_RATE]

def decodeWithSoundfile(path):
    import librosa
    import soundfile
    with soundfile.SoundFile(path) as f:
        f.seek(max(0, f.frames // 2 - EXCERPT_SECONDS * f.samplerate // 2))
        y = f.read(EXCERPT_SECONDS * f.samplerate, dtype="float32", always_2d=True).mean(axis=1)
        return librosa.resample(y, orig_sr=f.samplerate, target_sr=SAMPLE_RATE)

# About 67 numbers describing how the excerpt sounds: timbre (MFCC mean/std), harmony (chroma),
# spectral contrast, brightness, noisiness, loudness and tempo.
def computeVector(path, duration):
    import librosa
    import numpy
    try:
        y = decodeExcerpt(path, duration)
    except Exception:
        try:
            y = decodeExcerpt(path, 0)  # some files cannot be seeked into: take the excerpt from the start
        except Exception:
            y = decodeWithSoundfile(path)  # e.g. WAV audio saved under an .mp3 name, which FFmpeg rejects
    if(len(y) < SAMPLE_RATE * 5):
        raise ValueError("less than 5 s of audio decoded")
    sr = SAMPLE_RATE
    spectrum = numpy.abs(librosa.stft(y))
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    chroma = librosa.feature.chroma_stft(S=spectrum ** 2, sr=sr)
    contrast = librosa.feature.spectral_contrast(S=spectrum, sr=sr)
    centroid = librosa.feature.spectral_centroid(S=spectrum, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(S=spectrum, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(S=spectrum, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    rms = librosa.feature.rms(S=spectrum)
    tempo = librosa.feature.tempo(y=y, sr=sr)
    parts = [mfcc.mean(axis=1), mfcc.std(axis=1), chroma.mean(axis=1), contrast.mean(axis=1),
             [centroid.mean(), centroid.std(), bandwidth.mean(), rolloff.mean(), zcr.mean(), rms.mean(), rms.std()],
             numpy.atleast_1d(tempo)[:1]]
    return [round(float(v), 5) for v in numpy.concatenate([numpy.asarray(p, dtype="float64") for p in parts])]

# Vectors already stored in the cache for these tracks (same file size/date, same feature version);
# None for a file that could not be analysed, so it is not retried at every launch.
def loadVectors(paths, cachePath=None):
    cache = TrackCache.load(cachePath or TrackCache.defaultPath())
    vectors = {}
    for p in paths:
        entry = cache.get(p)
        if(entry and entry.get("vectorVersion") == VERSION):
            vectors[p] = entry.get("vector")
    return vectors

# Stores vectors (None: analysis failed) in the cache next to each track's tags; files changed since are skipped.
def saveVectors(vectors, cachePath=None):
    cachePath = cachePath or TrackCache.defaultPath()
    cache = TrackCache.load(cachePath)
    changed = False
    for p, vector in vectors.items():
        entry = cache.get(p)
        try:
            stat = os.stat(p)
        except OSError:
            continue
        if(entry is not None and TrackCache.isFresh(entry, stat)):
            entry["vector"] = vector
            entry["vectorVersion"] = VERSION
            changed = True
    if(changed):
        TrackCache.save(cachePath, cache)

# --- run in worker processes (see AudioAnalyzer) ---

def initWorker():
    # One math thread per worker: the pool already uses half the cores, and numpy/numba would
    # otherwise start a thread per core in every worker and fight over them.
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
        os.environ[variable] = "1"
    if(os.name == "nt"):
        import ctypes
        BELOW_NORMAL_PRIORITY_CLASS = 0x4000
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS)

# Returns (path, vector), or (path, None, reason) if the file cannot be analysed.
def analyse(path):
    import mutagen
    try:
        return path, computeVector(path, mutagen.File(path).info.length)
    except Exception as e:
        return path, None, str(e)
