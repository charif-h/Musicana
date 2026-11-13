import zlib

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QLinearGradient, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionViewItem

from GroupedTracksModel import ALBUM_INFO_ROLE, COVER_SIZE

PADDING = 8
CELL_SIZE = QSize(COVER_SIZE + 2 * PADDING + 14, COVER_SIZE + 2 * PADDING + 92)
CORNER = 8

# Draws an album cell of the grid: the cover, then the title (bold, up to two lines), the artist,
# and the year and track count (smaller, muted).
class AlbumDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        return CELL_SIZE

    def paint(self, painter, option, index):
        info = index.data(ALBUM_INFO_ROLE)
        if(info is None):
            return super().paint(painter, option, index)
        selected = bool(option.state & QStyle.State_Selected)
        palette = option.palette
        text = palette.color(QPalette.HighlightedText if selected else QPalette.Text)
        muted = palette.color(QPalette.HighlightedText if selected else QPalette.PlaceholderText)
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        cell = option.rect.adjusted(2, 2, -2, -2)
        if(selected):
            painter.setPen(Qt.NoPen)
            painter.setBrush(palette.color(QPalette.Highlight))
            painter.drawRoundedRect(cell, CORNER, CORNER)
        elif(option.state & QStyle.State_MouseOver):
            painter.setPen(palette.color(QPalette.Mid))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(cell, CORNER, CORNER)
        inner = cell.adjusted(PADDING, PADDING, -PADDING, -PADDING)

        cover = QRect(inner.left() + (inner.width() - COVER_SIZE) // 2, inner.top(), COVER_SIZE, COVER_SIZE)
        icon = index.data(Qt.DecorationRole)
        if(isinstance(icon, QIcon) and not icon.isNull()):
            pixmap = icon.pixmap(COVER_SIZE, COVER_SIZE)
            painter.drawPixmap(cover.left() + (COVER_SIZE - pixmap.width()) // 2,
                               cover.bottom() + 1 - pixmap.height(), pixmap)  # smaller covers sit on the baseline
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(palette.color(QPalette.AlternateBase))
            painter.drawRoundedRect(cover, CORNER, CORNER)
            painter.setPen(muted)
            painter.setFont(QFont(option.font.family(), 40))
            painter.drawText(cover, Qt.AlignCenter, "♪")

        y = cover.bottom() + 8
        width = inner.width()
        titleFont = QFont(option.font)
        titleFont.setBold(True)
        metrics = QFontMetrics(titleFont)
        titleRect = QRect(inner.left(), y, width, metrics.lineSpacing() * 2)
        title = info["name"]
        if(metrics.boundingRect(titleRect, Qt.AlignHCenter | Qt.TextWordWrap, title).height() > titleRect.height()):
            title = metrics.elidedText(title, Qt.ElideRight, width * 2 - metrics.averageCharWidth() * 4)
        painter.setFont(titleFont)
        painter.setPen(text)
        painter.drawText(titleRect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, title)
        y = titleRect.bottom() + 3

        painter.setFont(option.font)
        metrics = QFontMetrics(option.font)
        if(info["artist"]):
            painter.setPen(text)
            painter.drawText(QRect(inner.left(), y, width, metrics.lineSpacing()), Qt.AlignHCenter,
                             metrics.elidedText(info["artist"], Qt.ElideRight, width))
            y += metrics.lineSpacing()

        smallFont = QFont(option.font)
        smallFont.setPointSizeF(max(option.font.pointSizeF() - 1.5, 6))
        metrics = QFontMetrics(smallFont)
        painter.setFont(smallFont)
        painter.setPen(muted)
        meta = " · ".join(v for v in (info["year"], info["count"]) if v)
        painter.drawText(QRect(inner.left(), y, width, metrics.lineSpacing()), Qt.AlignHCenter,
                         metrics.elidedText(meta, Qt.ElideRight, width))
        painter.restore()

HEADER_COVER = 48
HEADER_HEIGHT = HEADER_COVER + 2 * 6

# Draws an album heading in the artist's track panel: a small cover, the title (bold) and, under it,
# the year and track count (muted). Rows without album info (the tracks) are drawn as usual.
class AlbumHeaderDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if(index.data(ALBUM_INFO_ROLE) is not None):
            size.setHeight(HEADER_HEIGHT)
        return size

    def paint(self, painter, option, index):
        info = index.data(ALBUM_INFO_ROLE)
        if(info is None):
            return super().paint(painter, option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        background = QStyleOptionViewItem(option)
        self.initStyleOption(background, index)
        background.text = ""
        background.icon = QIcon()
        style.drawControl(QStyle.CE_ItemViewItem, background, painter, option.widget)  # selection and hover only
        selected = bool(option.state & QStyle.State_Selected)
        text = option.palette.color(QPalette.HighlightedText if selected else QPalette.Text)
        muted = option.palette.color(QPalette.HighlightedText if selected else QPalette.PlaceholderText)
        painter.save()
        area = option.rect.adjusted(8, 6, -8, -6)
        cover = QRect(area.left(), area.top(), HEADER_COVER, HEADER_COVER)
        icon = index.data(Qt.DecorationRole)
        if(isinstance(icon, QIcon) and not icon.isNull()):
            pixmap = icon.pixmap(HEADER_COVER, HEADER_COVER)
            painter.drawPixmap(cover.left() + (HEADER_COVER - pixmap.width()) // 2,
                               cover.top() + (HEADER_COVER - pixmap.height()) // 2, pixmap)
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(option.palette.color(QPalette.AlternateBase))
            painter.drawRoundedRect(cover, 4, 4)
            painter.setPen(muted)
            painter.setFont(QFont(option.font.family(), 16))
            painter.drawText(cover, Qt.AlignCenter, "♪")

        left = cover.right() + 10
        width = area.right() - left
        titleFont = QFont(option.font)
        titleFont.setBold(True)
        titleFont.setPointSizeF(option.font.pointSizeF() + 1)
        titleMetrics = QFontMetrics(titleFont)
        smallFont = QFont(option.font)
        smallFont.setPointSizeF(max(option.font.pointSizeF() - 1, 6))
        smallMetrics = QFontMetrics(smallFont)
        meta = " · ".join(v for v in (info["year"], info["count"]) if v)
        block = titleMetrics.lineSpacing() + 2 + smallMetrics.lineSpacing()
        y = area.top() + (HEADER_COVER - block) // 2
        painter.setFont(titleFont)
        painter.setPen(text)
        painter.drawText(QRect(left, y, width, titleMetrics.lineSpacing()), Qt.AlignLeft | Qt.AlignVCenter,
                         titleMetrics.elidedText(info["name"], Qt.ElideRight, width))
        painter.setFont(smallFont)
        painter.setPen(muted)
        painter.drawText(QRect(left, y + titleMetrics.lineSpacing() + 2, width, smallMetrics.lineSpacing()),
                         Qt.AlignLeft | Qt.AlignVCenter, smallMetrics.elidedText(meta, Qt.ElideRight, width))
        painter.restore()

GENRE_CELL = QSize(COVER_SIZE + 24, COVER_SIZE + 24)
TILE_CORNER = 18

def genreColor(name, unknown):
    if(unknown):
        return QColor.fromHslF(0.0, 0.0, 0.38)
    hue = zlib.crc32(name.lower().encode("utf-8")) % 360  # the same genre always gets the same colour
    return QColor.fromHslF(hue / 360, 0.52, 0.40)

# The largest bold font (in points) in which the wrapped text fits the area; falls back to the smallest.
def fitFont(base, text, width, height, largest=24, smallest=8):
    font = QFont(base)
    font.setBold(True)
    for size in range(largest, smallest - 1, -1):
        font.setPointSize(size)
        box = QFontMetrics(font).boundingRect(QRect(0, 0, width, 10000), Qt.AlignCenter | Qt.TextWordWrap, text)
        if(box.width() <= width and box.height() <= height):
            break
    return font

# Draws a genre as a square tile: a colour from the genre's name, the name as large as fits, and a track-count pill.
class GenreTileDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        return GENRE_CELL

    def paint(self, painter, option, index):
        info = index.data(ALBUM_INFO_ROLE)
        if(info is None):
            return super().paint(painter, option, index)
        selected = bool(option.state & QStyle.State_Selected)
        hovered = bool(option.state & QStyle.State_MouseOver)
        tile = option.rect.adjusted(12, 12, -12, -12)
        base = genreColor(info["name"], info.get("unknown", False))
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)

        shape = QPainterPath()
        shape.addRoundedRect(tile, TILE_CORNER, TILE_CORNER)
        gradient = QLinearGradient(tile.topLeft(), tile.bottomRight())
        gradient.setColorAt(0, base.lighter(125 if hovered else 112))
        gradient.setColorAt(1, base.darker(145))
        painter.fillPath(shape, gradient)
        painter.setClipPath(shape)  # soft circles in the corners, cut by the tile's edge
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 30))
        painter.drawEllipse(QPoint(tile.right() - 8, tile.top() + 4), 72, 72)
        painter.setBrush(QColor(0, 0, 0, 34))
        painter.drawEllipse(QPoint(tile.left() - 6, tile.bottom() + 10), 62, 62)
        painter.setClipping(False)

        margin = 14
        pill = QFont(option.font)
        pill.setPointSizeF(max(option.font.pointSizeF() - 1.5, 6))
        pillMetrics = QFontMetrics(pill)
        pillText = pillMetrics.elidedText(info["count"], Qt.ElideRight, tile.width() - 2 * margin - 16)
        pillRect = QRect(0, 0, pillMetrics.horizontalAdvance(pillText) + 18, pillMetrics.lineSpacing() + 6)
        pillRect.moveCenter(QPoint(tile.center().x(), tile.bottom() - margin - pillRect.height() // 2 + 4))

        area = QRect(tile.left() + margin, tile.top() + margin, tile.width() - 2 * margin,
                     pillRect.top() - tile.top() - margin - 6)
        font = fitFont(option.font, info["name"], area.width(), area.height())
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0, 60))  # a faint shadow keeps the name readable on light colours
        painter.drawText(area.translated(1, 2), Qt.AlignCenter | Qt.TextWordWrap, info["name"])
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(area, Qt.AlignCenter | Qt.TextWordWrap, info["name"])

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 70))
        painter.drawRoundedRect(pillRect, pillRect.height() / 2, pillRect.height() / 2)
        painter.setFont(pill)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(pillRect, Qt.AlignCenter, pillText)

        if(selected or hovered):
            ring = QPen(option.palette.color(QPalette.Highlight if selected else QPalette.Mid), 3 if selected else 2)
            painter.setPen(ring)
            painter.setBrush(Qt.NoBrush)
            outer = tile.adjusted(-5, -5, 5, 5)
            painter.drawRoundedRect(outer, TILE_CORNER + 4, TILE_CORNER + 4)
        painter.restore()
