import os
import json

DEFAULTS = {"volume": 100, "windowGeometry": None, "tableHeader": None}

def appDataDir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "Musicana")

def defaultPath():
    return os.path.join(appDataDir(), "settings.json")

# Returns DEFAULTS overlaid with the saved values; a missing or unreadable file just gives the defaults.
def load(path=None):
    settings = dict(DEFAULTS)
    try:
        with open(path or defaultPath(), encoding="utf-8") as f:
            saved = json.load(f)
        if(isinstance(saved, dict)):
            settings.update(saved)
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as e:
        print("Ignoring unreadable settings file:", e)
    return settings

def save(settings, path=None):
    path = path or defaultPath()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        os.replace(path + ".tmp", path)
    except OSError as e:
        print("Could not save settings:", e)
