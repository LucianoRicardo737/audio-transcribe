#!/usr/bin/env python3
"""
Floating Panel GUI for Audio Transcription (Qt Version).

Vertical panel with Record, Pause, and Cancel buttons using PySide6.
"""
import sys
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QListWidget, QPushButton, QListWidgetItem,
    QComboBox, QGroupBox, QFormLayout, QMessageBox
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
from config import BUTTON_SIZE, BUTTON_POSITION, GROQ_MODEL
from settings import get_settings, update_settings, get_text, TRANSLATIONS


# Button sizes
BTN_SIZE = max(44, BUTTON_SIZE)
SMALL_BTN_SIZE = 18  # Small utility buttons
PANEL_PADDING = 8
PANEL_SPACING = 6
SMALL_BTN_SPACING = 3

# Colors
COLORS = {
    'idle': QColor('#4CAF50'),
    'idle_hover': QColor('#66BB6A'),
    'recording': QColor('#f44336'),
    'recording_hover': QColor('#EF5350'),
    'processing': QColor('#FFC107'),
    'processing_hover': QColor('#FFCA28'),
    'paused': QColor('#FF9800'),
    'paused_hover': QColor('#FFA726'),
    'cancel': QColor('#9E9E9E'),
    'cancel_hover': QColor('#BDBDBD'),
    'cancel_active': QColor('#F44336'),
    'disabled': QColor('#616161'),
    'panel_bg': QColor(30, 30, 30, 200),
    'utility': QColor('#607D8B'),
    'utility_hover': QColor('#78909C'),
}


class CircularButton(QWidget):
    """A single circular button."""

    clicked = Signal()

    def __init__(self, icon_name: str, color: QColor, parent=None):
        super().__init__(parent)
        self.setFixedSize(BTN_SIZE, BTN_SIZE)
        self.setCursor(Qt.PointingHandCursor)

        self._icon_name = icon_name
        self._color = color
        self._hover_color = color.lighter(120)
        self._is_hovered = False
        self._is_enabled = True
        self._scale = 1.0
        self._spin_angle = 0
        self._is_spinning = False
        self._is_pulsing = False
        self._pulse_direction = 1

        # Pre-load icon
        self._update_icon()

        # Animation timer
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._anim_tick)

    def _update_icon(self):
        """Update the icon pixmap."""
        icon_size = QSize(24, 24)
        self._icon_pixmap = qta.icon(self._icon_name, color='white').pixmap(icon_size)

    def set_icon(self, icon_name: str):
        """Change the button icon."""
        self._icon_name = icon_name
        self._update_icon()
        self.update()

    def set_color(self, color: QColor, hover_color: QColor = None):
        """Change button colors."""
        self._color = color
        self._hover_color = hover_color or color.lighter(120)
        self.update()

    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        self._is_enabled = enabled
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ForbiddenCursor)
        self.update()

    def start_pulse(self):
        """Start pulse animation."""
        self._is_pulsing = True
        self._is_spinning = False
        self._scale = 1.0
        self._pulse_direction = 1
        if not self._anim_timer.isActive():
            self._anim_timer.start(50)

    def start_spin(self):
        """Start spin animation."""
        self._is_spinning = True
        self._is_pulsing = False
        self._spin_angle = 0
        if not self._anim_timer.isActive():
            self._anim_timer.start(30)

    def stop_animation(self):
        """Stop all animations."""
        self._is_pulsing = False
        self._is_spinning = False
        self._scale = 1.0
        self._anim_timer.stop()
        self.update()

    def _anim_tick(self):
        """Animation tick."""
        if self._is_pulsing:
            self._scale += 0.012 * self._pulse_direction
            if self._scale >= 1.08:
                self._pulse_direction = -1
            elif self._scale <= 0.92:
                self._pulse_direction = 1
        elif self._is_spinning:
            self._spin_angle = (self._spin_angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        """Draw the circular button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = BTN_SIZE / 2
        radius = (BTN_SIZE / 2 - 2) * self._scale

        # Determine color
        if not self._is_enabled:
            color = COLORS['disabled']
        elif self._is_hovered:
            color = self._hover_color
        else:
            color = self._color

        # Draw glow
        for i in range(2):
            glow_radius = radius + (2 - i) * 2
            glow_color = QColor(color)
            glow_color.setAlpha(25 + i * 15)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(
                int(center - glow_radius),
                int(center - glow_radius),
                int(glow_radius * 2),
                int(glow_radius * 2)
            )

        # Draw circle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 1))
        painter.drawEllipse(
            int(center - radius),
            int(center - radius),
            int(radius * 2),
            int(radius * 2)
        )

        # Draw icon
        icon_size = int(20 * self._scale)
        scaled_pixmap = self._icon_pixmap.scaled(
            icon_size, icon_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        if self._is_spinning:
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

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_enabled:
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_enabled:
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
            event.accept()


class SmallButton(QWidget):
    """A small circular utility button."""

    clicked = Signal()

    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(SMALL_BTN_SIZE, SMALL_BTN_SIZE)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)

        self._icon_name = icon_name
        self._color = COLORS['utility']
        self._hover_color = COLORS['utility_hover']
        self._is_hovered = False

        # Pre-load icon
        icon_size = QSize(12, 12)
        self._icon_pixmap = qta.icon(icon_name, color='white').pixmap(icon_size)

    def paintEvent(self, event):
        """Draw the small button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = SMALL_BTN_SIZE / 2
        radius = SMALL_BTN_SIZE / 2 - 1

        color = self._hover_color if self._is_hovered else self._color

        # Draw circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(
            int(center - radius),
            int(center - radius),
            int(radius * 2),
            int(radius * 2)
        )

        # Draw icon
        icon_size = 12
        painter.drawPixmap(
            int(center - icon_size / 2),
            int(center - icon_size / 2),
            self._icon_pixmap
        )

        painter.end()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
            event.accept()


class FloatingPanel(QWidget):
    """Vertical floating panel with transcription controls."""

    # Signals for thread-safe UI updates
    state_changed = Signal(object)
    transcription_completed = Signal(str)
    transcription_errored = Signal(str)

    def __init__(self):
        super().__init__()

        # Window flags: frameless, always on top, tool window
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Calculate panel size (3 main buttons + 1 row of 3 small buttons)
        panel_width = BTN_SIZE + PANEL_PADDING * 2
        panel_height = (BTN_SIZE * 3 + PANEL_SPACING * 2 +  # Main buttons
                       PANEL_SPACING + SMALL_BTN_SIZE +      # Small buttons row
                       PANEL_PADDING * 2)
        self.setFixedSize(panel_width, panel_height)

        # State
        self._state = TranscriptionState.IDLE

        # Drag support
        self._drag_position: Optional[QPoint] = None
        self._is_dragging = False

        # Controller
        self.controller: Optional[TranscriptionController] = None

        # Create buttons
        self._create_buttons()

        # Position window
        self._position_window()

        # Context menu
        self._create_context_menu()

        # Connect signals
        self.state_changed.connect(self._handle_state_change)
        self.transcription_completed.connect(self._handle_transcription_complete)
        self.transcription_errored.connect(self._handle_transcription_error)

    def _create_buttons(self):
        """Create the control buttons."""
        # Record/Stop button
        self.btn_record = CircularButton('mdi.microphone', COLORS['idle'], self)
        self.btn_record.move(PANEL_PADDING, PANEL_PADDING)
        self.btn_record.clicked.connect(self._on_record_click)

        # Pause/Resume button
        self.btn_pause = CircularButton('mdi.pause', COLORS['paused'], self)
        self.btn_pause.move(PANEL_PADDING, PANEL_PADDING + BTN_SIZE + PANEL_SPACING)
        self.btn_pause.clicked.connect(self._on_pause_click)
        self.btn_pause.set_enabled(False)

        # Cancel button
        self.btn_cancel = CircularButton('mdi.close', COLORS['cancel'], self)
        self.btn_cancel.move(PANEL_PADDING, PANEL_PADDING + (BTN_SIZE + PANEL_SPACING) * 2)
        self.btn_cancel.clicked.connect(self._on_cancel_click)
        self.btn_cancel.set_enabled(False)

        # Small utility buttons row
        small_row_y = PANEL_PADDING + (BTN_SIZE + PANEL_SPACING) * 3
        small_total_width = SMALL_BTN_SIZE * 3 + SMALL_BTN_SPACING * 2
        small_start_x = PANEL_PADDING + (BTN_SIZE - small_total_width) // 2

        settings = get_settings()
        lang = settings.get("language", "es")

        # Help button
        self.btn_help = SmallButton('mdi.help', get_text("tooltip_help", lang), self)
        self.btn_help.move(small_start_x, small_row_y)
        self.btn_help.clicked.connect(self._show_help)

        # Settings button (microphone selection)
        self.btn_settings = SmallButton('mdi.cog', get_text("tooltip_settings", lang), self)
        self.btn_settings.move(small_start_x + SMALL_BTN_SIZE + SMALL_BTN_SPACING, small_row_y)
        self.btn_settings.clicked.connect(self._show_device_selector)

        # Exit button
        self.btn_exit = SmallButton('mdi.exit-to-app', get_text("tooltip_exit", lang), self)
        self.btn_exit.move(small_start_x + (SMALL_BTN_SIZE + SMALL_BTN_SPACING) * 2, small_row_y)
        self.btn_exit.clicked.connect(QApplication.quit)

    def _update_tooltips(self):
        """Update button tooltips with current language."""
        settings = get_settings()
        lang = settings.get("language", "es")
        self.btn_help.setToolTip(get_text("tooltip_help", lang))
        self.btn_settings.setToolTip(get_text("tooltip_settings", lang))
        self.btn_exit.setToolTip(get_text("tooltip_exit", lang))

    def _position_window(self):
        """Position window based on config."""
        screen = QApplication.primaryScreen().geometry()
        margin = 30

        positions = {
            'top-left': QPoint(margin, margin),
            'top-right': QPoint(screen.width() - self.width() - margin, margin),
            'bottom-left': QPoint(margin, screen.height() - self.height() - margin - 50),
            'bottom-right': QPoint(
                screen.width() - self.width() - margin,
                screen.height() - self.height() - margin - 50
            ),
            'center': QPoint(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            ),
        }

        pos = positions.get(BUTTON_POSITION, positions['bottom-right'])
        self.move(pos)

    def _create_context_menu(self):
        """Create right-click menu."""
        self._menu = QMenu(self)
        self._menu.addAction("Cambiar microfono", self._show_device_selector)
        self._menu.addSeparator()
        self._menu.addAction("Salir", QApplication.quit)

    def paintEvent(self, event):
        """Draw the panel background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw rounded rectangle background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(COLORS['panel_bg']))
        painter.drawRoundedRect(self.rect(), 12, 12)

        painter.end()

    # === Button Click Handlers ===

    def _on_record_click(self):
        """Handle record/stop button click."""
        if not self.controller:
            return

        if self._state == TranscriptionState.IDLE:
            self.controller.start_recording()
        elif self._state in (TranscriptionState.RECORDING, TranscriptionState.PAUSED):
            self.controller.stop_recording()

    def _on_pause_click(self):
        """Handle pause/resume button click."""
        if self.controller:
            self.controller.toggle_pause()

    def _on_cancel_click(self):
        """Handle cancel button click."""
        if self.controller:
            self.controller.cancel_recording()

    def _show_help(self):
        """Show help dialog."""
        settings = get_settings()
        dialog = HelpDialog(settings.get("language", "es"), self)
        dialog.exec()

    # === State Updates ===

    def _update_buttons_for_state(self, state: TranscriptionState):
        """Update button appearance based on state."""
        self._state = state

        if state == TranscriptionState.IDLE:
            # Record button: green mic
            self.btn_record.set_icon('mdi.microphone')
            self.btn_record.set_color(COLORS['idle'], COLORS['idle_hover'])
            self.btn_record.set_enabled(True)
            self.btn_record.stop_animation()

            # Pause: disabled
            self.btn_pause.set_icon('mdi.pause')
            self.btn_pause.set_enabled(False)
            self.btn_pause.stop_animation()

            # Cancel: disabled
            self.btn_cancel.set_color(COLORS['cancel'], COLORS['cancel_hover'])
            self.btn_cancel.set_enabled(False)

        elif state == TranscriptionState.RECORDING:
            # Record button: red stop
            self.btn_record.set_icon('mdi.stop')
            self.btn_record.set_color(COLORS['recording'], COLORS['recording_hover'])
            self.btn_record.set_enabled(True)
            self.btn_record.start_pulse()

            # Pause: enabled
            self.btn_pause.set_icon('mdi.pause')
            self.btn_pause.set_color(COLORS['paused'], COLORS['paused_hover'])
            self.btn_pause.set_enabled(True)
            self.btn_pause.stop_animation()

            # Cancel: enabled
            self.btn_cancel.set_color(COLORS['cancel_active'], COLORS['cancel_hover'])
            self.btn_cancel.set_enabled(True)

        elif state == TranscriptionState.PAUSED:
            # Record button: red stop (still can stop)
            self.btn_record.set_icon('mdi.stop')
            self.btn_record.set_color(COLORS['recording'], COLORS['recording_hover'])
            self.btn_record.set_enabled(True)
            self.btn_record.stop_animation()

            # Pause: show play icon to resume
            self.btn_pause.set_icon('mdi.play')
            self.btn_pause.set_color(COLORS['idle'], COLORS['idle_hover'])
            self.btn_pause.set_enabled(True)
            self.btn_pause.start_pulse()

            # Cancel: enabled
            self.btn_cancel.set_color(COLORS['cancel_active'], COLORS['cancel_hover'])
            self.btn_cancel.set_enabled(True)

        elif state == TranscriptionState.PROCESSING:
            # Record button: processing spinner
            self.btn_record.set_icon('mdi.loading')
            self.btn_record.set_color(COLORS['processing'], COLORS['processing_hover'])
            self.btn_record.set_enabled(False)
            self.btn_record.start_spin()

            # Pause: disabled
            self.btn_pause.set_enabled(False)
            self.btn_pause.stop_animation()

            # Cancel: disabled
            self.btn_cancel.set_enabled(False)

        elif state == TranscriptionState.ERROR:
            # Show error briefly then return to idle
            self.btn_record.set_icon('mdi.alert-circle')
            self.btn_record.set_color(COLORS['cancel_active'], COLORS['cancel_hover'])
            self.btn_record.stop_animation()

    # === Mouse Events for Dragging ===

    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
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
        """Handle mouse release."""
        self._drag_position = None
        self._is_dragging = False
        event.accept()

    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        self._menu.exec(event.globalPos())

    # === Controller Callbacks ===

    def _on_state_change(self, state: TranscriptionState):
        """Handle state change from controller (called from worker thread)."""
        self.state_changed.emit(state)

    def _on_transcription_complete(self, text: str):
        """Handle successful transcription (called from worker thread)."""
        self.transcription_completed.emit(text)

    def _on_transcription_error(self, error: str):
        """Handle error (called from worker thread)."""
        self.transcription_errored.emit(error)

    # === Signal Handlers (main thread) ===

    @Slot(object)
    def _handle_state_change(self, state: TranscriptionState):
        """Handle state change in main thread."""
        self._update_buttons_for_state(state)

    @Slot(str)
    def _handle_transcription_complete(self, text: str):
        """Handle successful transcription in main thread."""
        # Show success briefly
        self.btn_record.set_icon('mdi.check-circle')
        self.btn_record.set_color(COLORS['idle'], COLORS['idle_hover'])
        self.btn_record.stop_animation()
        QTimer.singleShot(1000, lambda: self._update_buttons_for_state(TranscriptionState.IDLE))

    @Slot(str)
    def _handle_transcription_error(self, error: str):
        """Handle error in main thread."""
        self._update_buttons_for_state(TranscriptionState.ERROR)
        QTimer.singleShot(2000, lambda: self._update_buttons_for_state(TranscriptionState.IDLE))

    # === Settings ===

    def _show_device_selector(self):
        """Show settings dialog."""
        if not self.controller:
            return

        devices = self.controller.get_available_devices()
        if not devices:
            return

        settings = get_settings()
        current_device = self.controller.get_selected_device()
        current_device_id = current_device['id'] if current_device else None
        current_language = settings.get("language", "es")

        dialog = SettingsDialog(devices, current_device_id, current_language, self)
        if dialog.exec() == QDialog.Accepted:
            changed = False

            if dialog.selected_device_id is not None and dialog.selected_device_id != current_device_id:
                self.controller.select_device(dialog.selected_device_id)
                update_settings(device_id=dialog.selected_device_id)
                changed = True

            if dialog.selected_language and dialog.selected_language != current_language:
                self.controller.set_language(dialog.selected_language)
                update_settings(language=dialog.selected_language)
                # Update tooltips with new language
                self._update_tooltips()
                changed = True

            if changed:
                t = lambda key: get_text(key, dialog.selected_language)
                lang_name = "Español" if dialog.selected_language == "es" else "English"
                QMessageBox.information(
                    self, t("settings_saved"),
                    f"{t('settings_saved_msg')}\n{t('settings_language')}: {lang_name}"
                )

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


class HelpDialog(QDialog):
    """Help dialog explaining the controls."""

    def __init__(self, lang="es", parent=None):
        super().__init__(parent)
        self.lang = lang
        t = lambda key: get_text(key, lang)

        self.setWindowTitle(t("help_title"))
        self.setFixedSize(320, 380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel(t("help_app_title"))
        title.setFont(QFont("", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Current language indicator
        lang_name = "Español" if lang == "es" else "English"
        lang_label = QLabel(f"{t('help_current_lang')}: <b>{lang_name}</b>")
        lang_label.setAlignment(Qt.AlignCenter)
        lang_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(lang_label)

        # Help content
        help_text = f"""
<table cellspacing="6">
<tr><td><b style="color:#4CAF50">{t('help_record')}</b></td><td>{t('help_record_desc')}</td></tr>
<tr><td><b style="color:#f44336">{t('help_stop')}</b></td><td>{t('help_stop_desc')}</td></tr>
<tr><td><b style="color:#FF9800">{t('help_pause')}</b></td><td>{t('help_pause_desc')}</td></tr>
<tr><td><b style="color:#4CAF50">{t('help_resume')}</b></td><td>{t('help_resume_desc')}</td></tr>
<tr><td><b style="color:#f44336">{t('help_cancel')}</b></td><td>{t('help_cancel_desc')}</td></tr>
</table>
<br>
<b>{t('help_buttons')}:</b><br>
<b>?</b> = {t('tooltip_help')} &nbsp; <b>⚙</b> = {t('tooltip_settings')} &nbsp; <b>⏻</b> = {t('tooltip_exit')}
<br><br>
<i>{t('help_tip')}</i>
"""
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.RichText)
        layout.addWidget(help_label)

        layout.addStretch()

        # Close button
        close_btn = QPushButton(t("help_ok"))
        close_btn.setFixedWidth(80)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)


# Available languages
LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
]


class SettingsDialog(QDialog):
    """Settings dialog for microphone and language selection."""

    def __init__(self, devices, current_device_id, current_language, parent=None):
        super().__init__(parent)
        self.lang = current_language
        t = lambda key: get_text(key, current_language)

        self.setWindowTitle(t("settings_title"))
        self.setFixedSize(360, 280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.selected_device_id = current_device_id
        self.selected_language = current_language

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Microphone section
        mic_group = QGroupBox(t("settings_microphone"))
        mic_layout = QVBoxLayout(mic_group)

        self.mic_combo = QComboBox()
        self.mic_combo.setStyleSheet("QComboBox { padding: 6px; }")

        current_idx = 0
        for i, device in enumerate(devices):
            name = device['name'][:40]
            if device['is_default']:
                name += " *"
            self.mic_combo.addItem(name, device['id'])
            if device['id'] == current_device_id:
                current_idx = i

        self.mic_combo.setCurrentIndex(current_idx)
        mic_layout.addWidget(self.mic_combo)
        layout.addWidget(mic_group)

        # Language section
        lang_group = QGroupBox(t("settings_language"))
        lang_layout = QVBoxLayout(lang_group)

        self.lang_combo = QComboBox()
        self.lang_combo.setStyleSheet("QComboBox { padding: 6px; }")

        current_lang_idx = 0
        for i, (code, name) in enumerate(LANGUAGES):
            self.lang_combo.addItem(name, code)
            if code == current_language:
                current_lang_idx = i

        self.lang_combo.setCurrentIndex(current_lang_idx)
        lang_layout.addWidget(self.lang_combo)
        layout.addWidget(lang_group)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton(t("settings_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton(t("settings_save"))
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        ok_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _on_accept(self):
        """Save selections."""
        self.selected_device_id = self.mic_combo.currentData()
        self.selected_language = self.lang_combo.currentData()
        self.accept()


class DeviceDialog(QDialog):
    """Device selection dialog."""

    def __init__(self, devices, current_device, parent=None, initial=False):
        super().__init__(parent)
        self.devices = devices
        self.selected_device_id = None

        settings = get_settings()
        lang = settings.get("language", "es")
        t = lambda key: get_text(key, lang)

        self.setWindowTitle(t("device_title") if initial else t("settings_microphone"))
        self.setFixedSize(420, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        if initial:
            # Header
            title = QLabel(t("device_title"))
            title.setFont(QFont("", 14, QFont.Bold))
            layout.addWidget(title)

            lang_name = "Español" if lang == "es" else "English"
            subtitle = QLabel(f"{t('settings_language')}: {lang_name} | Model: {GROQ_MODEL}")
            subtitle.setStyleSheet("color: #666;")
            layout.addWidget(subtitle)

            layout.addSpacing(10)

        # Instruction
        layout.addWidget(QLabel(t("device_select")))

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
                text += " *"
                default_idx = i
            if current_device and device['id'] == current_device['id']:
                text = "> " + text

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, device['id'])
            self.list_widget.addItem(item)

        self.list_widget.setCurrentRow(default_idx)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton(t("device_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton(t("device_start") if initial else t("device_select_btn"))
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

    # Load saved settings
    settings = get_settings()
    saved_language = settings.get("language", "es")

    # Create panel
    panel = FloatingPanel()

    # Create controller with callbacks
    panel.controller = TranscriptionController(
        on_state_change=panel._on_state_change,
        on_transcription_complete=panel._on_transcription_complete,
        on_transcription_error=panel._on_transcription_error,
    )

    # Set language from saved settings
    panel.controller.set_language(saved_language)

    # Show device selector
    if not panel.show_initial_device_selector():
        return 1

    panel.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
