"""Table view for STARS (Phase 2d).

Replaces gView.Table (tkinter canvas Text grid + DataViewer.DataTable)
with a QTableView backed by a QAbstractTableModel.

Public interface (mirrors gView.Table):
  TableView(name, observer, values, varName,
            rowLabels, columnLabels, tsId, csId, fmt)

Linking/brushing semantics:
  - Click a row   → publish 'newSelectedObservations' (cs_id)
  - Click a column header → publish 'newColumnSelected' (ts_id)
  - Receive 'selectObservations' / 'newSelectColumn' → scroll + highlight
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QApplication, QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex,
)
from PyQt6.QtGui import QColor, QFont

_HIGHLIGHT_COLOR = QColor('#ffff00')       # yellow
_DEFAULT_BG      = QColor('#ffffff')       # white
_HEADER_HL_COLOR = QColor('#ffe082')       # amber for column highlight


# ── Qt table model ────────────────────────────────────────────────────────

class _ArrayModel(QAbstractTableModel):
    """Wraps a 2-D numpy array for QTableView."""

    def __init__(self, data, row_labels, col_labels, fmt='%.3f', parent=None):
        super().__init__(parent)
        self._data = data                  # (n_rows, n_cols) float array
        self._row_labels = row_labels
        self._col_labels = col_labels
        self._fmt = fmt
        n, k = data.shape
        # Highlight sets
        self._hl_rows = set()
        self._hl_col  = None

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        r, c = index.row(), index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            val = self._data[r, c]
            try:
                return self._fmt % val
            except Exception:
                return str(val)
        if role == Qt.ItemDataRole.BackgroundRole:
            if r in self._hl_rows or c == self._hl_col:
                return _HIGHLIGHT_COLOR
            return _DEFAULT_BG
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._col_labels[section] if section < len(self._col_labels) else str(section)
            else:
                return self._row_labels[section] if section < len(self._row_labels) else str(section)
        if role == Qt.ItemDataRole.BackgroundRole:
            if orientation == Qt.Orientation.Horizontal and section == self._hl_col:
                return _HEADER_HL_COLOR
        return None

    # ── Highlight API ─────────────────────────────────────────────────────

    def highlight_rows(self, row_indices):
        self._hl_rows = set(row_indices)
        self._hl_col = None
        self.layoutChanged.emit()

    def highlight_col(self, col_index):
        self._hl_col = col_index
        self._hl_rows = set()
        self.layoutChanged.emit()

    def clear_highlights(self):
        self._hl_rows = set()
        self._hl_col = None
        self.layoutChanged.emit()


# ── TableView ─────────────────────────────────────────────────────────────

class TableView(QMainWindow):
    """Spreadsheet window for a 2-D array.

    Parameters
    ----------
    name : str
        Window title.
    observer : Observer
        STARS viewObserver singleton.
    values : array-like, shape (n_cs, n_t)
        Numerical matrix to display.
    varName : str
        Variable name (used in title).
    rowLabels : list of str
        One label per row (CS unit names).
    columnLabels : list of str
        One label per column (time-period names).
    tsId : list of int
        Time-series ids matching each column (for publishing).
    csId : list of int
        Cross-section ids matching each row (for publishing).
    fmt : str
        printf-style format for cell values (default '%.3f').
    """

    _ntable = 0

    def __init__(self, name, observer,
                 values, varName,
                 rowLabels=None, columnLabels=None,
                 tsId=None, csId=None,
                 fmt='%.3f',
                 width=None, height=None):

        TableView._ntable += 1

        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        QMainWindow.__init__(self)
        self.name = f'table_{TableView._ntable}'
        self.type = 'table'
        self.observer = observer

        arr = np.asarray(values, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        n, k = arr.shape

        self._varName = varName
        self._csId  = list(csId)  if csId  is not None else list(range(n))
        self._tsId  = list(tsId)  if tsId  is not None else list(range(k))
        row_labels  = list(rowLabels)    if rowLabels    else [str(i) for i in self._csId]
        col_labels  = list(columnLabels) if columnLabels else [str(j) for j in self._tsId]

        # id → row/col for hit-testing
        self._cs_to_row = {cs: i for i, cs in enumerate(self._csId)}
        self._ts_to_col = {ts: j for j, ts in enumerate(self._tsId)}

        # Qt model + view
        self._model = _ArrayModel(arr, row_labels, col_labels, fmt=fmt)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setFont(QFont('Courier', 9))
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.setCentralWidget(self._table)

        # Window sizing
        screen = self._app.primaryScreen().availableGeometry()
        w = width  or min(900, screen.width() // 2)
        h = height or min(600, screen.height() // 2)
        self.resize(w, h)
        self.setWindowTitle(f'{varName}')

        # Connect row-click signal
        self._table.clicked.connect(self._on_cell_clicked)
        self._table.horizontalHeader().sectionClicked.connect(self._on_col_clicked)

        # Subscriber wiring
        self.methods = {}
        self.buildMethods()
        observer.subscribe(self)

        self.show()

    # ── Subscriber protocol (inlined to avoid MRO conflict with QMainWindow) ──

    def dispatch(self, commandName, options=[]):
        if commandName not in self.methods:
            return
        if options or options == []:
            try:
                self.methods[commandName](options)
            except TypeError:
                self.methods[commandName]()
        else:
            self.methods[commandName]()

    def publish(self, commandName, options=[]):
        self.observer.processSignal(self.name, self.type, commandName, options)

    def unsubscribe(self):
        self.observer.unsubscribe(self)

    def buildMethods(self):
        self.methods = {
            'selectObservations':     self.selectObservations,
            'selectedObservations':   self.selectObservations,
            'newSelectedObservations':self.selectObservations,
            'newBrushObservations':   self.selectObservations,
            'newSelectColumn':        self.newSelectColumn,
            'selectObservationsCS':   self.selectObservations,
            'updateTime':             self.newSelectColumn,
        }

    # ── Interaction — incoming ────────────────────────────────────────────

    def selectObservations(self, obs_ids):
        """Highlight rows matching the given cs_ids."""
        cs_set = set(obs_ids) if obs_ids else set()
        rows = [self._cs_to_row[cs] for cs in cs_set if cs in self._cs_to_row]
        self._model.highlight_rows(rows)
        if rows:
            self._table.scrollTo(self._model.index(min(rows), 0))

    def highlightObservations(self, obs_ids):
        self.selectObservations(obs_ids)

    def unhighlightObservations(self, obs_ids):
        self._model.clear_highlights()

    def newSelectColumn(self, ts_id):
        """Highlight the column corresponding to ts_id."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        col = self._ts_to_col.get(ts_id)
        if col is not None:
            self._model.highlight_col(col)
            self._table.scrollTo(self._model.index(0, col))

    def updateTime(self, ts_id):
        self.newSelectColumn(ts_id)

    # ── Interaction — outgoing ────────────────────────────────────────────

    def _on_cell_clicked(self, index):
        """Row click → publish newSelectedObservations with cs_id."""
        row = index.row()
        if row < len(self._csId):
            cs_id = self._csId[row]
            self.publish('newSelectedObservations', [cs_id])

    def _on_col_clicked(self, col):
        """Column header click → publish newColumnSelected with ts_id."""
        if col < len(self._tsId):
            ts_id = self._tsId[col]
            self.publish('newColumnSelected', [ts_id])

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self.unsubscribe()
        event.accept()

    def cleanup(self):
        self.close()
