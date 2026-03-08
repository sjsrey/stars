"""Base view class for STARS PyQt6 views (Phase 2a/2b).

Replaces gView.View (tkinter Toplevel + Canvas) with a
QMainWindow containing a FigureCanvasQTAgg.

The Observer/Subscriber contract is identical:
  - Each view calls buildMethods() to populate self.methods
  - dispatch(commandName, options) calls the appropriate method
  - publish(commandName, options) routes through viewObserver
"""

from PyQt6.QtWidgets import QMainWindow, QApplication, QToolBar, QStatusBar
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import sys
import os

# Ensure stars/stars is on the path so bare-name imports work
_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

# Interaction modes (mirror gView.py constants)
OFF = "off"
LINKING = "linking"
BRUSHING = "brushing"
TRAVELING = "traveling"
BRUSH_TRAVELING = "brushTraveling"


class STARSView(QMainWindow):
    """Abstract PyQt6 view that replaces gView.View.

    Each concrete subclass must implement:
        draw(self)         — initial render onto self.ax
        buildMethods(self) — populate self.methods dict
        highlightObservations(self, obs_ids) — visually select observations
        unhighlightObservations(self, obs_ids) — clear visual selection

    Mouse interaction follows the Subscriber pattern:
        left-click + release → publish('selectedObservations', obs_ids)
        The observer routes that signal to other views based on mode.
    """

    _nviews = 0

    def __init__(self, name, view_type, observer,
                 width=None, height=None, title=None):
        """
        name (str)       : unique view name (e.g. 'map_1')
        view_type (str)  : Subscriber type key (e.g. 'map', 'histogram')
        observer         : viewObserver singleton from Interaction.py
        width, height    : window size in pixels (default: half screen)
        title (str)      : window title bar text
        """
        # Qt must be initialised before creating any widget
        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        QMainWindow.__init__(self)
        STARSView._nviews += 1
        self.name = name
        self.type = view_type
        self.observer = observer
        self.methods = {}
        self._interaction_mode = OFF

        # Selected observation ids (set by highlighting)
        self.selectedIds = set()

        # ── Matplotlib figure + canvas ────────────────────────────────────
        self.fig = Figure(figsize=(7, 6), tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.setCentralWidget(self.canvas)

        # ── Window sizing and placement (4-quadrant cascade) ─────────────
        screen = self._app.primaryScreen().availableGeometry()
        w = width or screen.width() // 2
        h = height or screen.height() // 2
        self.resize(w, h)

        pos = (STARSView._nviews - 1) % 4
        offsets = [(0, 0), (w, 0), (0, h), (w, h)]
        dx, dy = offsets[pos]
        self.move(dx, dy)

        # ── Window title ─────────────────────────────────────────────────
        self.setWindowTitle(title or name)

        # ── Matplotlib mouse event connections ───────────────────────────
        # Rubber-band selection state
        self._press_xy = None
        self._rect_patch = None

        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

        # ── Status bar for coordinate readout ───────────────────────────
        self.statusBar().showMessage('Ready')
        self.canvas.mpl_connect('motion_notify_event', self._update_status)

        # ── Subscribe to observer ────────────────────────────────────────
        self.buildMethods()
        observer.subscribe(self)

        # ── Initial render ───────────────────────────────────────────────
        self.draw()
        self.canvas.draw()
        self.show()

    # ── Abstract interface ────────────────────────────────────────────────

    def draw(self):
        """Render initial content onto self.ax.  Override in subclasses."""
        pass

    def buildMethods(self):
        """Populate self.methods for Subscriber dispatch.  Override and
        call super().buildMethods() to include the common methods."""
        self.methods = {
            'selectObservations':   self.selectObservations,
            'selectedObservations': self.selectedObservations,
            'updateTime':           self.updateTime,
        }

    def selectObservations(self, obs_ids):
        """Respond to a selection from another view."""
        self.selectedIds = set(obs_ids)
        self.highlightObservations(obs_ids)
        self.canvas.draw_idle()

    def selectedObservations(self, obs_ids):
        """Handle a selection initiated by this view: highlight + publish."""
        self.selectObservations(obs_ids)
        self.publish('selectedObservations', obs_ids)

    def updateTime(self, ts_id):
        """Respond to a time-period change from a TimeSeries view."""
        pass

    def highlightObservations(self, obs_ids):
        """Visually mark obs_ids as selected.  Override in subclasses."""
        pass

    def unhighlightObservations(self, obs_ids):
        """Clear visual selection for obs_ids.  Override in subclasses."""
        pass

    # ── Mouse event handlers ──────────────────────────────────────────────

    def _on_press(self, event):
        if event.inaxes is None:
            return
        if event.button == 1:
            self._press_xy = (event.xdata, event.ydata)

    def _on_motion(self, event):
        if self._press_xy is None or event.inaxes is None:
            return
        x0, y0 = self._press_xy
        x1, y1 = event.xdata, event.ydata
        # Draw rubber-band rectangle
        if self._rect_patch is not None:
            self._rect_patch.remove()
        from matplotlib.patches import Rectangle
        self._rect_patch = self.ax.add_patch(Rectangle(
            (min(x0, x1), min(y0, y1)),
            abs(x1 - x0), abs(y1 - y0),
            linewidth=1, edgecolor='black', facecolor='yellow', alpha=0.3,
        ))
        self.canvas.draw_idle()

    def _on_release(self, event):
        if self._press_xy is None or event.inaxes is None:
            self._press_xy = None
            return
        if self._rect_patch is not None:
            self._rect_patch.remove()
            self._rect_patch = None

        x0, y0 = self._press_xy
        x1, y1 = event.xdata, event.ydata
        self._press_xy = None

        obs_ids = self._hit_test(x0, y0, x1, y1)
        if obs_ids:
            self.selectedObservations(obs_ids)
        self.canvas.draw_idle()

    def _hit_test(self, x0, y0, x1, y1):
        """Return list of observation ids inside the selection rectangle.
        Override in subclasses to implement geometry-specific hit-testing."""
        return []

    def _update_status(self, event):
        if event.inaxes:
            self.statusBar().showMessage(
                f'x={event.xdata:.4f}  y={event.ydata:.4f}')
        else:
            self.statusBar().showMessage('Ready')

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

    def addMethod(self, methodName, method):
        self.methods[methodName] = method

    def unsubscribe(self):
        self.observer.unsubscribe(self)

    # ── Interaction mode ──────────────────────────────────────────────────

    def setInteractionMode(self, mode):
        self._interaction_mode = mode
        self.observer.setInteractionMode(mode)

    # ── Qt lifecycle ──────────────────────────────────────────────────────

    def closeEvent(self, event):
        self.unsubscribe()
        STARSView._nviews = max(0, STARSView._nviews - 1)
        event.accept()

    def cleanup(self):
        self.close()
