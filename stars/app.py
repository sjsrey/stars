"""STARS application shell (Phase 2a).

Replaces starsgui.App (tkinter GuiMixin + GuiMaker) with a
PyQt6 QMainWindow.  The Observer/Subscriber wiring from Interaction.py
is reused unchanged; only the rendering backend changes.

Entry point::

    python app.py

or from a shell::

    from app import main; main()
"""

import sys
import os
import numpy as np

# ── Qt initialisation guard ───────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QMenuBar,
    QMenu, QToolBar, QStatusBar, QFileDialog,
    QInputDialog, QMessageBox, QDialog, QVBoxLayout,
    QHBoxLayout, QListWidget, QAbstractItemView,
    QPushButton, QLabel, QSpinBox, QDialogButtonBox,
    QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

# Ensure stars/stars is on path
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from stars import Project
from Interaction import viewObserver
from views import (MapView, HistogramView, TimeSeriesView, BoxPlotView,
                   CDFView, ScatterView, PCPView, TableView, MoranScatterView)


# ── Tiny dialog helpers ───────────────────────────────────────────────────

class _PickOneDialog(QDialog):
    """Pick one item from a list."""
    def __init__(self, parent, title, label, items):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(label))
        self._list = QListWidget()
        self._list.addItems(items)
        if items:
            self._list.setCurrentRow(0)
        lay.addWidget(self._list)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def selection(self):
        item = self._list.currentItem()
        return item.text() if item else None


class _PickManyDialog(QDialog):
    """Pick multiple items from a list."""
    def __init__(self, parent, title, label, items):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(label))
        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._list.addItems(items)
        lay.addWidget(self._list)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def selections(self):
        return [item.text() for item in self._list.selectedItems()]


class _VarTimeDialog(QDialog):
    """Pick a variable and one or more time periods."""
    def __init__(self, parent, title, var_names, time_names,
                 n_classes=None, default_classes=5):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)

        lay.addWidget(QLabel('Variable:'))
        self._var = QComboBox()
        self._var.addItems(var_names)
        lay.addWidget(self._var)

        if n_classes is not None:
            row = QHBoxLayout()
            row.addWidget(QLabel('Classes:'))
            self._spin = QSpinBox()
            self._spin.setRange(2, 10)
            self._spin.setValue(default_classes)
            row.addWidget(self._spin)
            lay.addLayout(row)
        else:
            self._spin = None

        lay.addWidget(QLabel('Time period(s):'))
        self._times = QListWidget()
        self._times.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._times.addItems(time_names)
        if time_names:
            self._times.setCurrentRow(0)
        lay.addWidget(self._times)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def var_name(self):
        return self._var.currentText()

    def n_classes(self):
        return self._spin.value() if self._spin else None

    def time_indices(self, all_times):
        selected = [item.text() for item in self._times.selectedItems()]
        if not selected:
            # default to first
            selected = [all_times[0]] if all_times else []
        return [all_times.index(t) for t in selected if t in all_times]


# ── SProject (mirrors starsgui.SProject) ─────────────────────────────────

class SProject(Project):
    """Project subclass with Qt-friendly extra methods."""
    def __init__(self, name):
        Project.__init__(self, name)

    def getVariableNames(self):
        return self.dataBase.getVariableNames()

    def getVariable(self, name):
        return self.dataBase.getVariable(name)

    def getCSCSTSVarNames(self, exclude=None):
        exclude = exclude or []
        names = self.getVariableNames()
        names = [n for n in names if self.getVariable(n).varType != 'TS']
        return [n for n in names if n not in exclude]

    def getTSVarNames(self, exclude=None):
        exclude = exclude or []
        names = self.getVariableNames()
        names = [n for n in names if self.getVariable(n).varType == 'TS']
        return [n for n in names if n not in exclude]


# ── Main application window ───────────────────────────────────────────────

class STARSApp(QMainWindow):
    """Qt replacement for starsgui.App."""

    def __init__(self):
        super().__init__()
        self.project = None
        self._views = []       # keep references so windows stay alive

        self.setWindowTitle('STARS: Space-Time Analysis of Regional Systems')
        self.resize(700, 450)

        # ── Log / status area ─────────────────────────────────────────────
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont('Courier', 9))
        self.setCentralWidget(self._log)

        # ── Status bar ────────────────────────────────────────────────────
        self.statusBar().showMessage('Ready')

        # ── Toolbar ───────────────────────────────────────────────────────
        tb = self.addToolBar('Interaction')
        for label, slot in [
            ('Off',      self._interaction_off),
            ('Link',     self._interaction_link),
            ('Brush',    self._interaction_brush),
            ('Close All', self._close_all),
        ]:
            act = QAction(label, self)
            act.triggered.connect(slot)
            tb.addAction(act)

        # ── Menu bar ──────────────────────────────────────────────────────
        mb = self.menuBar()
        self._build_menus(mb)

    # ── Menu construction ─────────────────────────────────────────────────

    def _build_menus(self, mb):
        # File
        file_m = mb.addMenu('&File')
        self._add_action(file_m, 'Open Project…', self._open_project)
        self._add_action(file_m, 'Project Summary', self._project_summary)
        file_m.addSeparator()
        self._add_action(file_m, 'Exit', self.close)

        # Data
        data_m = mb.addMenu('&Data')
        self._add_action(data_m, 'List Variables', self._list_variables)
        self._add_action(data_m, 'View Variable Table…', self._show_table)

        # Analysis
        an_m = mb.addMenu('&Analysis')
        esda_m = an_m.addMenu('ESDA')
        self._add_action(esda_m, 'Moran Global…',        lambda: self._run_esda('moran'))
        self._add_action(esda_m, 'Moran Scatter Plot…',  lambda: self._run_esda('moran_scatter'))
        self._add_action(esda_m, 'Moran Local…',         lambda: self._run_esda('local_moran'))
        self._add_action(esda_m, 'Geary Global…',        lambda: self._run_esda('geary'))
        markov_m = an_m.addMenu('Markov')
        self._add_action(markov_m, 'Classic…',  lambda: self._run_markov('classic'))
        self._add_action(markov_m, 'Spatial…',  lambda: self._run_markov('spatial'))
        ineq_m = an_m.addMenu('Inequality')
        self._add_action(ineq_m, 'Theil Global…', lambda: self._run_inequality('theil'))
        self._add_action(ineq_m, 'Theil Decomp…', lambda: self._run_inequality('theild'))

        # Visualization
        viz_m = mb.addMenu('&Visualization')

        map_m = viz_m.addMenu('Map')
        self._add_action(map_m, 'Quantile',       lambda: self._show_map('percentiles'))
        self._add_action(map_m, 'Equal Width',    lambda: self._show_map('equalWidth'))
        self._add_action(map_m, 'Std. Deviation', lambda: self._show_map('stdev'))
        self._add_action(map_m, 'Box Map',        lambda: self._show_map('boxMap'))
        self._add_action(map_m, 'Diverging',      lambda: self._show_map('percentiles', legend='diverging'))

        hist_m = viz_m.addMenu('Histogram')
        self._add_action(hist_m, 'Sturges Rule',  lambda: self._show_histogram('sturges'))
        self._add_action(hist_m, 'Equal Width',   lambda: self._show_histogram('equalWidth'))
        self._add_action(hist_m, 'Percentiles',   lambda: self._show_histogram('percentiles'))

        self._add_action(viz_m, 'Time Series',            self._show_timeseries)
        self._add_action(viz_m, 'Box Plot',               self._show_boxplot)
        self._add_action(viz_m, 'CDF',                    self._show_cdf)
        self._add_action(viz_m, 'Scatter Plot',           self._show_scatter)
        self._add_action(viz_m, 'Parallel Coordinate',    self._show_pcp)

        # Window
        win_m = mb.addMenu('&Window')
        self._add_action(win_m, 'Close All',  self._close_all)
        self._add_action(win_m, 'Raise All',  self._raise_all)

        # Help
        help_m = mb.addMenu('&Help')
        self._add_action(help_m, 'About', self._about)

    @staticmethod
    def _add_action(menu, label, slot):
        act = QAction(label, menu)
        act.triggered.connect(slot)
        menu.addAction(act)

    # ── Logging ───────────────────────────────────────────────────────────

    def report(self, text):
        self._log.append(str(text))
        self.statusBar().showMessage(str(text)[:120])

    # ── Project I/O ───────────────────────────────────────────────────────

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open STARS Project', '',
            'STARS Project (*.prj);;All files (*)')
        if not path:
            return
        proj_dir = os.path.dirname(path)
        orig = os.getcwd()
        os.chdir(proj_dir)
        try:
            self.project = SProject(os.path.basename(path))
            self.project.ReadProjectFile(path)
            if hasattr(self.project, 'coords'):
                self.project.scaleCoords()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to open project:\n{e}')
            return
        finally:
            os.chdir(orig)
        self.report(f'Opened: {path}')
        self._project_summary()

    def _project_summary(self):
        if not self._check_project():
            return
        try:
            self.report(self.project.catalogue())
        except Exception as e:
            self.report(str(e))

    # ── Guard ─────────────────────────────────────────────────────────────

    def _check_project(self):
        if self.project is None:
            QMessageBox.information(self, 'No project', 'Please open a project first.')
            return False
        return True

    def _var_time_dialog(self, title, var_names, n_classes=None):
        """Show variable + time period picker, return (varName, t_indices, n_cls)."""
        if not var_names:
            self.report('No suitable variables found.')
            return None, [], None
        time_names = list(self.project.timeString)
        dlg = _VarTimeDialog(self, title, var_names, time_names, n_classes)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None, [], None
        var_name = dlg.var_name()
        t_idx = dlg.time_indices(time_names)
        n_cls = dlg.n_classes()
        return var_name, t_idx, n_cls

    # ── Data callbacks ────────────────────────────────────────────────────

    def _list_variables(self):
        if not self._check_project():
            return
        names = self.project.getVariableNames()
        lines = []
        for n in names:
            v = self.project.getVariable(n)
            lines.append(f'  {n:<20s}  {v.varType}  shape={v.shape}')
        self.report('Variables:\n' + '\n'.join(lines))

    def _show_table(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        dlg = _PickOneDialog(self, 'View Table', 'Variable:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        var_name = dlg.selection()
        if not var_name:
            return
        variable = self.project.getVariable(var_name)
        arr = np.asarray(variable)
        n, k = arr.shape
        row_labels = list(self.project.regionNames) if hasattr(self.project, 'regionNames') \
            else [str(i) for i in range(n)]
        col_labels = list(variable.timeString) if hasattr(variable, 'timeString') \
            else [str(j) for j in range(k)]
        view = TableView(
            name=var_name,
            observer=viewObserver,
            values=arr,
            varName=var_name,
            rowLabels=row_labels,
            columnLabels=col_labels,
            tsId=list(range(k)),
            csId=list(range(n)),
        )
        self._views.append(view)
        self.report(f'Table: {var_name}')

    # ── Analysis callbacks ────────────────────────────────────────────────

    def _pick_var_and_weight(self, title):
        """Return (var_name, weight_name) or (None, None)."""
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        dlg = _PickOneDialog(self, title, 'Variable:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None, None
        var_name = dlg.selection()
        mat_names = list(self.project.dataBase.getMatrixNames())
        if not mat_names:
            QMessageBox.information(self, 'No weights', 'Load a spatial weights matrix first.')
            return None, None
        dlg2 = _PickOneDialog(self, 'Weights', 'Weights matrix:', mat_names)
        if dlg2.exec() != QDialog.DialogCode.Accepted:
            return None, None
        return var_name, dlg2.selection()

    def _run_esda(self, kind):
        if not self._check_project():
            return
        var_name, weight_name = self._pick_var_and_weight(f'ESDA — {kind}')
        if var_name is None:
            return
        try:
            import Esda
            variable = self.project.getVariable(var_name)
            w = self.project.dataBase.getMatrix(weight_name)
            if kind == 'moran':
                result = Esda.Moran(variable, w)
                lines = ['Moran I by period:']
                for t, (mi, zi, pv) in enumerate(zip(result.mi, result.zi, result.npvalue)):
                    lines.append(f'  t={t:3d}  I={mi:8.4f}  z={zi:7.3f}  p={pv:.4f}')
                self.report('\n'.join(lines))
            elif kind == 'moran_scatter':
                # Pick a single time period for the scatter
                time_names = list(self.project.timeString)
                dlg_t = _PickOneDialog(self, 'Time period', 'Period:', time_names)
                if dlg_t.exec() != QDialog.DialogCode.Accepted:
                    return
                t_label = dlg_t.selection()
                t = time_names.index(t_label) if t_label in time_names else 0
                y_t = np.asarray(variable[:, t]).flatten()
                # z-score
                std = y_t.std()
                x_z = (y_t - y_t.mean()) / (std if std > 0 else 1.0)
                # spatial lag
                result_moran = Esda.Moran(variable, w)
                y_lag = np.asarray(result_moran.ylag[:, t]).flatten()
                lag_std = y_lag.std()
                y_lag_z = (y_lag - y_lag.mean()) / (lag_std if lag_std > 0 else 1.0)
                # Local Moran for quadrant colouring (optional)
                try:
                    result_lm = Esda.LocalMoran(variable, w)
                    quad_ids = result_lm.qvalue[:, t].astype(int)
                    sig_mask = result_lm.ppvalue[:, t] < 0.05 \
                        if hasattr(result_lm, 'ppvalue') else None
                except Exception:
                    quad_ids = None
                    sig_mask = None
                n_cs = len(x_z)
                view = MoranScatterView(
                    name=var_name,
                    observer=viewObserver,
                    x=x_z,
                    y_lag=y_lag_z,
                    varName=var_name,
                    t=t,
                    csIds=list(range(n_cs)),
                    quad_ids=quad_ids,
                    sig_mask=sig_mask,
                    time_string=t_label,
                )
                self._register(view)
                self.report(f'Moran scatter: {var_name} {t_label}  '
                            f'I={result_moran.mi[t]:.4f}')
                return
            elif kind == 'geary':
                result = Esda.Geary(variable, w)
                lines = [f'Geary C by period:']
                for t, (gc, zc) in enumerate(zip(result.gc, result.zc)):
                    lines.append(f'  t={t:3d}  C={gc:8.4f}  z={zc:7.3f}')
                self.report('\n'.join(lines))
            elif kind == 'local_moran':
                result = Esda.LocalMoran(variable, w)
                self.report(f'Local Moran: mi shape={result.mi.shape}, '
                            f'quadrant counts: {np.bincount(result.qvalue[:, 0].astype(int), minlength=5)[1:]}')
        except Exception as e:
            self.report(f'ESDA error: {e}')

    def _run_markov(self, kind):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        dlg = _PickOneDialog(self, f'Markov — {kind}', 'Variable:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        var_name = dlg.selection()
        if not var_name:
            return
        try:
            import Markov
            variable = self.project.getVariable(var_name)
            if kind == 'classic':
                result = Markov.ClMarkov(variable)
                self.report(
                    f'Classic Markov  k={result.k}  '
                    f'transitions total={result.transMat.sum()}\n'
                    f'Ergodic dist: {np.array2string(result.edist, precision=4)}')
            elif kind == 'spatial':
                mat_names = list(self.project.dataBase.getMatrixNames())
                if not mat_names:
                    self.report('Load a spatial weights matrix first.')
                    return
                dlg2 = _PickOneDialog(self, 'Weights', 'Weights matrix:', mat_names)
                if dlg2.exec() != QDialog.DialogCode.Accepted:
                    return
                w = self.project.dataBase.getMatrix(dlg2.selection())
                result = Markov.SpMarkov(variable, w)
                self.report(
                    f'Spatial Markov  k={result.k}  '
                    f'lag classes={result.numLags}')
        except Exception as e:
            self.report(f'Markov error: {e}')

    def _run_inequality(self, kind):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        dlg = _PickOneDialog(self, f'Inequality — {kind}', 'Variable:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        var_name = dlg.selection()
        if not var_name:
            return
        try:
            import Inequality
            variable = self.project.getVariable(var_name)
            if kind == 'theil':
                result = Inequality.Theil(variable)
                self.report(
                    f'Theil T by period:\n' +
                    '\n'.join(f'  t={t}  T={v:.6f}' for t, v in enumerate(result.T)))
            elif kind == 'theild':
                # Requires regime variable
                reg_names = [n for n in self.project.getVariableNames()
                             if self.project.getVariable(n).varType == 'CS']
                dlg2 = _PickOneDialog(self, 'Regime variable', 'Regime (CS):', reg_names)
                if dlg2.exec() != QDialog.DialogCode.Accepted:
                    return
                regime = self.project.getVariable(dlg2.selection())
                result = Inequality.TheilD(variable, regime)
                self.report(
                    f'Theil Decomp  BG={result.BG[-1]:.6f}  WG={result.WG[-1]:.6f}')
        except Exception as e:
            self.report(f'Inequality error: {e}')

    # ── View factories ────────────────────────────────────────────────────

    def _register(self, view):
        """Keep a reference and return the view."""
        self._views.append(view)
        view.show()
        return view

    def _show_map(self, classification='percentiles', legend='sequential'):
        if not self._check_project():
            return
        if not hasattr(self.project, 'coords'):
            self.report('Project has no spatial coordinates.')
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        var_name, t_indices, n_cls = self._var_time_dialog(
            'Map', var_names, n_classes=True)
        if var_name is None:
            return
        variable = self.project.getVariable(var_name)
        coords = self.project.coords
        poly2cs = self.project.poly2cs
        cs2poly = self.project.cs2poly
        for t in t_indices:
            y = np.asarray(variable[:, t]).flatten()
            ts_label = variable.timeString[t]
            view = MapView(
                name=f'{var_name}  {ts_label}',
                observer=viewObserver,
                coords=coords,
                values=y,
                varName=var_name,
                t=t,
                poly2cs=poly2cs,
                cs2poly=cs2poly,
                classification=classification,
                nBins=n_cls or 5,
                legendType=legend,
                time_string=ts_label,
            )
            self._register(view)
            self.report(f'Map: {var_name} {ts_label}')

    def _show_histogram(self, classification='sturges'):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        var_name, t_indices, n_cls = self._var_time_dialog(
            'Histogram', var_names, n_classes=(classification == 'equalWidth'))
        if var_name is None:
            return
        variable = self.project.getVariable(var_name)
        n_cs = variable.shape[0]
        for t in t_indices:
            y = np.asarray(variable[:, t]).flatten()
            ts_label = variable.timeString[t]
            view = HistogramView(
                name=f'{var_name}  {ts_label}',
                observer=viewObserver,
                values=y,
                varName=var_name,
                t=t,
                csIds=list(range(n_cs)),
                classification=classification,
                nBins=n_cls or 5,
                time_string=ts_label,
            )
            self._register(view)
            self.report(f'Histogram: {var_name} {ts_label}')

    def _show_timeseries(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        dlg = _PickOneDialog(self, 'Time Series', 'Variable:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        var_name = dlg.selection()
        if not var_name:
            return
        variable = self.project.getVariable(var_name)
        arr = np.asarray(variable)   # (n_cs, n_t)
        ts_labels = list(variable.timeString)
        view = TimeSeriesView(
            name=var_name,
            observer=viewObserver,
            values=arr,
            varName=var_name,
            tsLabels=ts_labels,
        )
        self._register(view)
        self.report(f'Time series: {var_name}')

    def _show_boxplot(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        var_name, t_indices, _ = self._var_time_dialog('Box Plot', var_names)
        if var_name is None:
            return
        variable = self.project.getVariable(var_name)
        n_cs = variable.shape[0]
        for t in t_indices:
            y = np.asarray(variable[:, t]).flatten()
            ts_label = variable.timeString[t]
            view = BoxPlotView(
                name=f'{var_name}  {ts_label}',
                observer=viewObserver,
                values=y,
                varName=var_name,
                t=t,
                csIds=list(range(n_cs)),
                time_string=ts_label,
            )
            self._register(view)
            self.report(f'Box plot: {var_name} {ts_label}')

    def _show_cdf(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        var_name, t_indices, _ = self._var_time_dialog('CDF', var_names)
        if var_name is None:
            return
        variable = self.project.getVariable(var_name)
        n_cs = variable.shape[0]
        for t in t_indices:
            y = np.asarray(variable[:, t]).flatten()
            ts_label = variable.timeString[t]
            view = CDFView(
                name=f'{var_name}  {ts_label}',
                observer=viewObserver,
                values=y,
                varName=var_name,
                t=t,
                csIds=list(range(n_cs)),
                time_string=ts_label,
            )
            self._register(view)
            self.report(f'CDF: {var_name} {ts_label}')

    def _show_scatter(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        if len(var_names) < 2:
            self.report('Need at least 2 variables for scatter plot.')
            return
        # Pick X variable
        dlg_x = _PickOneDialog(self, 'Scatter X', 'X variable:', var_names)
        if dlg_x.exec() != QDialog.DialogCode.Accepted:
            return
        x_name = dlg_x.selection()
        # Pick Y variable
        dlg_y = _PickOneDialog(self, 'Scatter Y', 'Y variable:', var_names)
        if dlg_y.exec() != QDialog.DialogCode.Accepted:
            return
        y_name = dlg_y.selection()
        # Pick time period
        time_names = list(self.project.timeString)
        dlg_t = _PickOneDialog(self, 'Time period', 'Period:', time_names)
        if dlg_t.exec() != QDialog.DialogCode.Accepted:
            return
        t_label = dlg_t.selection()
        t = time_names.index(t_label) if t_label in time_names else 0

        x_var = self.project.getVariable(x_name)
        y_var = self.project.getVariable(y_name)
        n_cs = x_var.shape[0]
        x = np.asarray(x_var[:, t]).flatten()
        y = np.asarray(y_var[:, t]).flatten()
        view = ScatterView(
            name=f'{x_name} vs {y_name}',
            observer=viewObserver,
            x=x, y=y,
            varName=f'{x_name} vs {y_name}',
            csIds=list(range(n_cs)),
            xLabel=x_name, yLabel=y_name,
            time_string=t_label,
        )
        self._register(view)
        self.report(f'Scatter: {x_name} vs {y_name}  {t_label}')

    def _show_pcp(self):
        if not self._check_project():
            return
        var_names = self.project.getCSCSTSVarNames(exclude=['Time'])
        # Pick multiple variables
        dlg = _PickManyDialog(self, 'Parallel Coordinates', 'Variables:', var_names)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        chosen = dlg.selections()
        if len(chosen) < 2:
            self.report('Select at least 2 variables.')
            return
        # Pick time period
        time_names = list(self.project.timeString)
        dlg_t = _PickOneDialog(self, 'Time period', 'Period:', time_names)
        if dlg_t.exec() != QDialog.DialogCode.Accepted:
            return
        t_label = dlg_t.selection()
        t = time_names.index(t_label) if t_label in time_names else 0

        n_cs = self.project.getVariable(chosen[0]).shape[0]
        # Build (n_vars, n_cs) matrix
        arr = np.stack([
            np.asarray(self.project.getVariable(v)[:, t]).flatten()
            for v in chosen
        ], axis=0)
        view = PCPView(
            name='PCP',
            observer=viewObserver,
            varNames=chosen,
            values=arr,
            t=t,
            csIds=list(range(n_cs)),
            time_string=t_label,
        )
        self._register(view)
        self.report(f'PCP: {", ".join(chosen)}  {t_label}')

    # ── Window management ─────────────────────────────────────────────────

    def _close_all(self):
        for view in list(self._views):
            try:
                view.close()
            except Exception:
                pass
        self._views.clear()

    def _raise_all(self):
        for view in self._views:
            try:
                view.raise_()
                view.activateWindow()
            except Exception:
                pass

    # ── Interaction modes ─────────────────────────────────────────────────

    def _interaction_off(self):
        viewObserver.setInteractionMode('off')
        self.report('Interaction: off')

    def _interaction_link(self):
        viewObserver.setInteractionMode('linking')
        self.report('Interaction: linking')

    def _interaction_brush(self):
        viewObserver.setInteractionMode('brushing')
        self.report('Interaction: brushing')

    # ── Help ─────────────────────────────────────────────────────────────

    def _about(self):
        QMessageBox.about(
            self, 'About STARS',
            'STARS: Space-Time Analysis of Regional Systems\n\n'
            'Phase 2 — PyQt6 + matplotlib interface\n'
            'Original authors: S. Rey, M. Janikas, B. Dev')

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._close_all()
        event.accept()


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    win = STARSApp()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
