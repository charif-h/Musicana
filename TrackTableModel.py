from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QFont

COLUMNS = (("title", "Title"), ("artist", "Artist"), ("album", "Album"), ("genre", "Genre"), ("date", "Year"))
PATH_ROLE = Qt.UserRole

class TrackTableModel(QAbstractTableModel):
    def __init__(self, tracks, parent=None):
        super().__init__(parent)
        self.tracks = tracks
        self.paths = list(tracks)
        # Precomputed once: sorting and filtering over thousands of rows must not go through data().
        self.cells = [tuple(" / ".join(tracks[p].get(key, [])) for key, name in COLUMNS) for p in self.paths]
        self.searchText = [str(tracks[p]).lower() for p in self.paths]  # same rule as FileSystem.matches()
        self.rows = {path: row for row, path in enumerate(self.paths)}
        self.current = None
        self.boldFont = QFont()
        self.boldFont.setBold(True)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.paths)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        path = self.paths[index.row()]
        if(role == Qt.DisplayRole):
            text = self.cells[index.row()][index.column()]
            if(index.column() == 0 and path == self.current):
                return "▶  " + text
            return text
        if(role == Qt.FontRole and path == self.current):
            return self.boldFont
        if(role == Qt.ToolTipRole):
            return path
        if(role == PATH_ROLE):
            return path
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if(role == Qt.DisplayRole and orientation == Qt.Horizontal):
            return COLUMNS[section][1]
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        self.layoutAboutToBeChanged.emit()
        keys = [cells[column].lower() for cells in self.cells]
        filled = [r for r in range(len(keys)) if keys[r]]
        order = sorted(filled, key=keys.__getitem__, reverse=(order == Qt.DescendingOrder))
        order += [r for r in range(len(keys)) if not keys[r]]  # tracks missing this tag always go last
        newRow = {old: new for new, old in enumerate(order)}
        self.paths = [self.paths[r] for r in order]
        self.cells = [self.cells[r] for r in order]
        self.searchText = [self.searchText[r] for r in order]
        self.rows = {path: row for row, path in enumerate(self.paths)}
        before = self.persistentIndexList()
        self.changePersistentIndexList(before, [self.index(newRow[i.row()], i.column()) for i in before])
        self.layoutChanged.emit()

    def setCurrent(self, path):
        previous, self.current = self.current, path
        for p in (previous, path):
            if(p in self.rows):
                row = self.rows[p]
                self.dataChanged.emit(self.index(row, 0), self.index(row, len(COLUMNS) - 1), [Qt.DisplayRole, Qt.FontRole])

# Only filters; sorting is forwarded to the source model, which sorts its precomputed text.
class TrackFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterText = ""

    def setFilterText(self, text):
        self.beginFilterChange()
        self.filterText = text.lower()
        self.endFilterChange(QSortFilterProxyModel.Direction.Rows)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        return self.filterText in self.sourceModel().searchText[sourceRow]

    def sort(self, column, order=Qt.AscendingOrder):
        self.sourceModel().sort(column, order)
