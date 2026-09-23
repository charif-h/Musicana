from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette

TOKENS = {
    "light": {"window": "#f4f4f6", "surface": "#ffffff", "surfaceAlt": "#ececf0", "text": "#1d1d21",
              "muted": "#5f5f68", "border": "#d6d6dc", "accent": "#2f6fdb", "accentText": "#ffffff"},
    "dark": {"window": "#1b1b1e", "surface": "#232327", "surfaceAlt": "#2c2c31", "text": "#ececf0",
             "muted": "#a0a0aa", "border": "#3a3a41", "accent": "#6c9dff", "accentText": "#10131a"},
}

STYLESHEET = """
QPushButton {{ padding: 5px 12px; border: 1px solid {border}; border-radius: 6px; background: {surfaceAlt}; }}
QPushButton:hover {{ border-color: {accent}; }}
QPushButton:pressed {{ background: {border}; }}
QLineEdit {{ padding: 5px 8px; border: 1px solid {border}; border-radius: 6px; background: {surface}; }}
QLineEdit:focus {{ border-color: {accent}; }}
QSlider::groove:horizontal {{ height: 4px; background: {border}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; }}
QSlider::handle:horizontal {{ width: 14px; margin: -5px 0; border-radius: 7px; background: {accent}; }}
QTableView {{ border: 1px solid {border}; border-radius: 6px; gridline-color: transparent;
              selection-background-color: {accent}; selection-color: {accentText}; }}
QTableView::item {{ padding: 0 6px; }}
QHeaderView::section {{ padding: 5px 6px; border: none; border-bottom: 1px solid {border};
                        background: {surfaceAlt}; font-weight: 600; }}
QLabel#title {{ font-size: 20pt; font-weight: 600; }}
QLabel#subtitle {{ font-size: 13pt; }}
QLabel#extra {{ font-size: 9pt; }}
QStatusBar {{ color: {muted}; }}
"""

NOW_PLAYING = """
QFrame#nowPlaying {{ background: {background}; border-radius: 10px; }}
QFrame#nowPlaying QLabel {{ color: {text}; background: transparent; }}
QFrame#nowPlaying QLabel#extra {{ color: {muted}; }}
QFrame#nowPlaying QLabel#art {{ font-size: 64pt; color: {muted}; }}
"""

def isDark():
    return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark

def tokens():
    return TOKENS["dark" if isDark() else "light"]

# Fusion draws every widget itself, so the stylesheet looks the same whatever the platform style.
def apply(app):
    app.setStyle("Fusion")
    t = tokens()
    palette = QPalette()
    for role, key in ((QPalette.Window, "window"), (QPalette.Base, "surface"), (QPalette.AlternateBase, "surfaceAlt"),
                      (QPalette.Button, "surfaceAlt"), (QPalette.WindowText, "text"), (QPalette.Text, "text"),
                      (QPalette.ButtonText, "text"), (QPalette.ToolTipBase, "surface"), (QPalette.ToolTipText, "text"),
                      (QPalette.PlaceholderText, "muted"), (QPalette.Highlight, "accent"),
                      (QPalette.HighlightedText, "accentText")):
        palette.setColor(role, QColor(t[key]))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET.format(**t))

# WCAG 2 relative luminance and contrast ratio.
def luminance(color):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(color.red()) + 0.7152 * channel(color.green()) + 0.0722 * channel(color.blue())

def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def mix(a, b, amount):
    return QColor(*(round(x * (1 - amount) + y * amount) for x, y in ((a.red(), b.red()), (a.green(), b.green()), (a.blue(), b.blue()))))

# Most common color among a 24x24 thumbnail's reasonably saturated pixels (plain average if there are none).
def dominantColor(image):
    small = image.scaled(24, 24, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    buckets = {}
    total = [0, 0, 0]
    for x in range(small.width()):
        for y in range(small.height()):
            c = small.pixelColor(x, y)
            total = [total[0] + c.red(), total[1] + c.green(), total[2] + c.blue()]
            if(c.hsvSaturationF() > 0.25 and 0.15 < c.valueF()):
                key = (c.red() // 32, c.green() // 32, c.blue() // 32)
                buckets.setdefault(key, []).append(c)
    if not(buckets):
        n = small.width() * small.height()
        return QColor(total[0] // n, total[1] // n, total[2] // n)
    colors = max(buckets.values(), key=len)
    return QColor(*(sum(getattr(c, ch)() for c in colors) // len(colors) for ch in ("red", "green", "blue")))

# Panel tinted with the cover's dominant color; text is black or white, whichever reads better (always >= 4.58:1).
def nowPlayingStyle(image=None):
    t = tokens()
    window = QColor(t["window"])
    if(image is None or image.isNull()):
        background = QColor(t["surface"])
    else:
        background = mix(window, dominantColor(image), 0.55)
    text = max((QColor("#ffffff"), QColor("#000000")), key=lambda c: contrast(c, background))
    # Fade the text toward the background only as far as it stays readable.
    muted = text
    for amount in (0.3, 0.2, 0.1):
        if(contrast(mix(text, background, amount), background) >= 4.5):
            muted = mix(text, background, amount)
            break
    return NOW_PLAYING.format(background=background.name(), text=text.name(), muted=muted.name())
