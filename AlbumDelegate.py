from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics, QIcon, QPalette
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

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
