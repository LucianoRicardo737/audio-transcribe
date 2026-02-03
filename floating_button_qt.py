#!/usr/bin/env python3
"""
Floating Button GUI for Audio Transcription (Qt Version).

Modern circular floating button with transparency, using PySide6 and QtAwesome icons.
"""
import sys
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QListWidget, QPushButton, QListWidgetItem
)
from PySide6.QtCore import (
    Qt, QPoint, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, Property, Signal, Slot, QMetaObject, Q_ARG
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QRegion,
    QFont, QFontDatabase, QCursor, QPixmap
)
import qtawesome as qta

from transcription_controller import TranscriptionController, TranscriptionState
from config import BUTTON_SIZE, BUTTON_POSITION, LANGUAGE, GROQ_MODEL

# Pre-load icons to avoid creating them in paintEvent
ICONS = {}


# Colors
COLORS = {
    'idle': QColor('#4CAF50'),
    'idle_dark': QColor('#388E3C'),
    'recording': QColor('#f44336'),
    'recording_dark': QColor('#D32F2F'),
    'processing': QColor('#FFC107'),
    'processing_dark': QColor('#FFA000'),
    'error': QColor('#78909C'),
    'error_dark': QColor('#546E7A'),
}


class FloatingButton(QWidget):
    """Modern circular floating button for audio transcription."""

    # Signals for thread-safe UI updates
    state_changed = Signal(object)
    transcription_completed = Signal(str)
    transcription_errored = Signal(str)

    def __init__(self):
        super().__init__()

        # Window flags: frameless, always on top, tool window (no taskbar)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        # Transparent background - KEY for circular appearance
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Size
        self.button_size = max(50, BUTTON_SIZE)
        self.setFixedSize(self.button_size, self.button_size)

        # State
        self._state = 'idle'
        self._scale = 1.0
        self._color = COLORS['idle']
        self._color_dark = COLORS['idle_dark']

        # Drag support
        self._drag_position: Optional[QPoint] = None
        self._is_dragging = False

        # Animation
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_tick)
        self._pulse_direction = 1
        self._spin_angle = 0

        # Controller
        self.controller: Optional[TranscriptionController] = None

        # Position window
        self._position_window()

        # Context menu
        self._create_context_menu()

        # Pre-load icons (avoid creating in paintEvent)
        self._load_icons()

        # Connect signals for thread-safe updates
        self.state_changed.connect(self._handle_state_change)
        self.transcription_completed.connect(self._handle_transcription_complete)
        self.transcription_errored.connect(self._handle_transcription_error)

    def _load_icons(self):
        """Pre-load all icons."""
        global ICONS
        icon_size = QSize(32, 32)
        ICONS = {
            'idle': qta.icon('mdi.microphone', color='white').pixmap(icon_size),
            'recording': qta.icon('mdi.stop', color='white').pixmap(icon_size),
            'processing': qta.icon('mdi.loading', color='white').pixmap(icon_size),
            'success': qta.icon('mdi.check-circle', color='white').pixmap(icon_size),
            'error': qta.icon('mdi.close-circle', color='white').pixmap(icon_size),
        }

    def _position_window(self):
        """Position window based on config."""
        screen = QApplication.primaryScreen().geometry()
        margin = 30

        positions = {
            'top-left': QPoint(margin, margin),
            'top-right': QPoint(screen.width() - self.button_size - margin, margin),
            'bottom-left': QPoint(margin, screen.height() - self.button_size - margin - 50),
            'bottom-right': QPoint(
                screen.width() - self.button_size - margin,
                screen.height() - self.button_size - margin - 50
            ),
            'center': QPoint(
                (screen.width() - self.button_size) // 2,
                (screen.height() - self.button_size) // 2
            ),
        }

        pos = positions.get(BUTTON_POSITION, positions['bottom-right'])
        self.move(pos)

    def _create_context_menu(self):
        """Create right-click menu."""
        self._menu = QMenu(self)
        self._menu.addAction("Cambiar micrófono", self._show_device_selector)
        self._menu.addSeparator()
        self._menu.addAction("Salir", QApplication.quit)

    def paintEvent(self, event):
        """Draw the circular button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.button_size / 2
        radius = (self.button_size / 2 - 2) * self._scale

        # Draw outer glow/shadow
        for i in range(3):
            glow_radius = radius + (3 - i) * 2
            glow_color = QColor(self._color)
            glow_color.setAlpha(30 + i * 15)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(
                int(center - glow_radius),
                int(center - glow_radius),
                int(glow_radius * 2),
                int(glow_radius * 2)
            )

        # Draw main circle with gradient-like effect
        painter.setBrush(QBrush(self._color))
        painter.setPen(QPen(self._color_dark, 1.5))
        painter.drawEllipse(
            int(center - radius),
            int(center - radius),
            int(radius * 2),
            int(radius * 2)
        )

        # Draw icon (use pre-loaded pixmaps)
        pixmap = ICONS.get(self._state, ICONS['idle'])
        icon_size = int(24 * self._scale)
        scaled_pixmap = pixmap.scaled(
            icon_size, icon_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # For spinning animation
        if self._state == 'processing':
            painter.save()
            painter.translate(center, center)
            painter.rotate(self._spin_angle)
            painter.drawPixmap(
                int(-icon_size / 2),
                int(-icon_size / 2),
                scaled_pixmap
            )
            painter.restore()
        else:
            painter.drawPixmap(
                int(center - icon_size / 2),
                int(center - icon_size / 2),
                scaled_pixmap
            )

        painter.end()

    def _set_state(self, state: str, color: QColor, color_dark: QColor):
        """Update visual state."""
        self._state = state
        self._color = color
        self._color_dark = color_dark
        self._scale = 1.0
        self.update()

    @Slot()
    def set_idle(self):
        """Set idle state."""
        self._pulse_timer.stop()
        self._set_state('idle', COLORS['idle'], COLORS['idle_dark'])

    @Slot()
    def set_recording(self):
        """Set recording state with pulse animation."""
        self._set_state('recording', COLORS['recording'], COLORS['recording_dark'])
        self._pulse_timer.start(50)

    @Slot()
    def set_processing(self):
        """Set processing state with spin animation."""
        self._set_state('processing', COLORS['processing'], COLORS['processing_dark'])
        self._spin_angle = 0
        self._pulse_timer.start(30)

    @Slot()
    def set_success(self):
        """Show success briefly."""
        self._pulse_timer.stop()
        self._set_state('success', COLORS['idle'], COLORS['idle_dark'])
        QTimer.singleShot(1000, self.set_idle)

    @Slot()
    def set_error(self):
        """Show error briefly."""
        self._pulse_timer.stop()
        self._set_state('error', COLORS['error'], COLORS['error_dark'])
        QTimer.singleShot(2000, self.set_idle)

    def _pulse_tick(self):
        """Animation tick."""
        if self._state == 'recording':
            # Pulse scale
            self._scale += 0.008 * self._pulse_direction
            if self._scale >= 1.06:
                self._pulse_direction = -1
            elif self._scale <= 0.94:
                self._pulse_direction = 1
        elif self._state == 'processing':
            # Spin
            self._spin_angle = (self._spin_angle + 8) % 360
        self.update()

    # === Mouse Events ===

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse drag."""
        if event.buttons() & Qt.LeftButton and self._drag_position:
            delta = event.globalPosition().toPoint() - self._drag_position - self.pos()
            if delta.manhattanLength() > 5:
                self._is_dragging = True
            if self._is_dragging:
                self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release - click if not dragging."""
        if event.button() == Qt.LeftButton and not self._is_dragging:
            self._on_click()
        self._drag_position = None
        self._is_dragging = False
        event.accept()

    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        self._menu.exec(event.globalPos())

    def _on_click(self):
        """Handle button click."""
        if self.controller:
            self.controller.toggle_recording()

    # === Controller Callbacks (emit signals for thread-safety) ===

    def _on_state_change(self, state: TranscriptionState):
        """Handle state change from controller (called from worker thread)."""
        self.state_changed.emit(state)

    def _on_transcription_complete(self, text: str):
        """Handle successful transcription (called from worker thread)."""
        self.transcription_completed.emit(text)

    def _on_transcription_error(self, error: str):
        """Handle error (called from worker thread)."""
        self.transcription_errored.emit(error)

    # === Signal Handlers (run in main thread) ===

    @Slot(object)
    def _handle_state_change(self, state: TranscriptionState):
        """Handle state change in main thread."""
        if state == TranscriptionState.IDLE:
            self.set_idle()
        elif state == TranscriptionState.RECORDING:
            self.set_recording()
        elif state == TranscriptionState.PROCESSING:
            self.set_processing()
        elif state == TranscriptionState.ERROR:
            self.set_error()

    @Slot(str)
    def _handle_transcription_complete(self, text: str):
        """Handle successful transcription in main thread."""
        self.set_success()

    @Slot(str)
    def _handle_transcription_error(self, error: str):
        """Handle error in main thread."""
        self.set_error()

    # === Device Selection ===

    def _show_device_selector(self):
        """Show device selection dialog."""
        if not self.controller:
            return

        devices = self.controller.get_available_devices()
        if not devices:
            return

        dialog = DeviceDialog(devices, self.controller.get_selected_device(), self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_device_id is not None:
            self.controller.select_device(dialog.selected_device_id)

    def show_initial_device_selector(self) -> bool:
        """Show initial device selection. Returns True if device selected."""
        devices = self.controller.get_available_devices()
        if not devices:
            return False

        # Auto-select if only one device
        if len(devices) == 1:
            self.controller.select_device(devices[0]['id'])
            return True

        dialog = DeviceDialog(devices, None, self, initial=True)
        if dialog.exec() == QDialog.Accepted and dialog.selected_device_id is not None:
            self.controller.select_device(dialog.selected_device_id)
            return True
        return False


class DeviceDialog(QDialog):
    """Device selection dialog."""

    def __init__(self, devices, current_device, parent=None, initial=False):
        super().__init__(parent)
        self.devices = devices
        self.selected_device_id = None

        self.setWindowTitle("Audio Transcription" if initial else "Seleccionar Micrófono")
        self.setFixedSize(420, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        if initial:
            # Header
            title = QLabel("Audio Transcription")
            title.setFont(QFont("", 14, QFont.Bold))
            layout.addWidget(title)

            subtitle = QLabel(f"Idioma: {LANGUAGE} | Modelo: {GROQ_MODEL}")
            subtitle.setStyleSheet("color: #666;")
            layout.addWidget(subtitle)

            layout.addSpacing(10)

        # Instruction
        layout.addWidget(QLabel("Selecciona tu micrófono:"))

        # Device list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #e8f5e9;
            }
        """)

        default_idx = 0
        for i, device in enumerate(devices):
            text = device['name'][:45]
            if device['is_default']:
                text += " ★"
                default_idx = i
            if current_device and device['id'] == current_device['id']:
                text = "→ " + text

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, device['id'])
            self.list_widget.addItem(item)

        self.list_widget.setCurrentRow(default_idx)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Iniciar" if initial else "Seleccionar")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        ok_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _on_accept(self):
        """Handle accept."""
        item = self.list_widget.currentItem()
        if item:
            self.selected_device_id = item.data(Qt.UserRole)
        self.accept()


def main():
    """Entry point."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # Create button
    button = FloatingButton()

    # Create controller with callbacks
    button.controller = TranscriptionController(
        on_state_change=button._on_state_change,
        on_transcription_complete=button._on_transcription_complete,
        on_transcription_error=button._on_transcription_error,
    )

    # Show device selector
    if not button.show_initial_device_selector():
        return 1

    button.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
