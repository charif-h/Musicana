import os
import json

# Bump when the stored tag format changes, so old caches are rebuilt.
CACHE_VERSION = 1

def defaultPath():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "Musicana", "cache.json")

# Returns {path: {"mtime": ns, "size": bytes, "tags": {...}}}, or {} if missing/unreadable.
def load(cachePath):
    try:
        with open(cachePath, encoding="utf-8") as f:
            data = json.load(f)
        if(data.get("version") == CACHE_VERSION):
            return data["tracks"]
        print("Metadata cache is from another version, rebuilding it")
    except FileNotFoundError:
        pass
    except (OSError, ValueError, KeyError, AttributeError) as e:
        print("Ignoring unreadable metadata cache", cachePath, ":", e)
    return {}

def save(cachePath, entries):
    os.makedirs(os.path.dirname(cachePath), exist_ok=True)
    tmp = cachePath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": CACHE_VERSION, "tracks": entries}, f, ensure_ascii=False)
    os.replace(tmp, cachePath)

def isFresh(entry, stat):
    return entry is not None and entry.get("mtime") == stat.st_mtime_ns and entry.get("size") == stat.st_size

def makeEntry(stat, tags):
    return {"mtime": stat.st_mtime_ns, "size": stat.st_size, "tags": tags}
