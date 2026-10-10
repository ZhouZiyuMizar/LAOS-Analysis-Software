'''
Export Settings Dialog for LAOS Analysis
Allows users to configure export quality settings
'''

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QPushButton, QGroupBox, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt

from utils.settings import get_settings
from utils.i18n import tr
from utils.responsive import get_ui_scale


class ExportSettingsDialog(QDialog):
    '''
    Dialog for configuring export settings (DPI, format, etc.)
    '''

    DPI_OPTIONS = [
        (72, "72 DPI"),
        (150, "150 DPI"),
        (300, "300 DPI"),
        (600, "600 DPI"),
    ]

    DPI_DESCRIPTIONS = {
        72: "Low quality/Screen display",
        150: "Medium quality",
        300: "High quality/Print",
        600: "Very high quality",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Export Settings", "ExportSettingsDialog"))
        self.setMinimumWidth(get_ui_scale().scaled(350))
        self.setModal(True)

        self.settings = get_settings()

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        '''Create dialog UI'''
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Export quality group
        quality_group = QGroupBox(tr("Export Quality", "ExportSettingsDialog"))
        quality_layout = QFormLayout(quality_group)

        # DPI selection
        self.dpi_combo = QComboBox()
        for dpi in [72, 150, 300, 600]:
            description = self.DPI_DESCRIPTIONS.get(dpi, "")
            label = f"{dpi} DPI ({tr(description, 'ExportSettingsDialog')})"
            self.dpi_combo.addItem(label, dpi)

        # Also allow custom DPI
        self.dpi_combo.addItem(tr("Custom DPI", "ExportSettingsDialog"), -1)
        self.dpi_combo.currentIndexChanged.connect(self._on_dpi_combo_changed)

        quality_layout.addRow(tr("DPI (Resolution):", "ExportSettingsDialog"), self.dpi_combo)

        # Custom DPI spinbox (hidden by default)
        self.custom_dpi_spin = QSpinBox()
        self.custom_dpi_spin.setRange(72, 1200)
        self.custom_dpi_spin.setValue(300)
        self.custom_dpi_spin.setSuffix(" DPI")
        self.custom_dpi_spin.setVisible(False)

        custom_dpi_layout = QHBoxLayout()
        custom_dpi_layout.addWidget(self.custom_dpi_spin)
        quality_layout.addRow(tr("Custom Value:", "ExportSettingsDialog"), custom_dpi_layout)

        # DPI info label
        self.dpi_info_label = QLabel()
        self.dpi_info_label.setStyleSheet(f"color: #666; font-size: {get_ui_scale().scaled(11)}px;")
        self._update_dpi_info()
        quality_layout.addRow("", self.dpi_info_label)

        layout.addWidget(quality_group)

        # Default format group
        format_group = QGroupBox(tr("Default Format", "ExportSettingsDialog"))
        format_layout = QFormLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItem("PNG", "png")
        self.format_combo.addItem("JPG", "jpg")
        self.format_combo.addItem("SVG", "svg")
        self.format_combo.addItem("HTML", "html")

        format_layout.addRow(tr("Default Export Format:", "ExportSettingsDialog"), self.format_combo)

        layout.addWidget(format_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(tr("Save", "ExportSettingsDialog"))
        self.save_btn.clicked.connect(self._save_settings)

        self.cancel_btn = QPushButton(tr("Cancel", "ExportSettingsDialog"))
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _load_settings(self):
        '''Load current settings'''
        current_dpi = self.settings.get_plot_setting('export_dpi', 300)

        # Check if DPI matches preset option
        found_preset = False
        preset_dpis = [72, 150, 300, 600]
        for i, dpi in enumerate(preset_dpis):
            if dpi == current_dpi:
                self.dpi_combo.setCurrentIndex(i)
                found_preset = True
                break

        if not found_preset:
            # Use custom option
            self.dpi_combo.setCurrentIndex(len(preset_dpis))
            self.custom_dpi_spin.setValue(current_dpi)
            self.custom_dpi_spin.setVisible(True)

        current_format = self.settings.get_plot_setting('export_format', 'png')
        format_index = self.format_combo.findData(current_format)
        if format_index >= 0:
            self.format_combo.setCurrentIndex(format_index)

        self._update_dpi_info()

    def _on_dpi_combo_changed(self, index):
        '''Handle DPI combo selection change'''
        dpi_value = self.dpi_combo.currentData()

        if dpi_value == -1:  # Custom
            self.custom_dpi_spin.setVisible(True)
            self.dpi_info_label.setText(
                tr("Recommended: 150-600 DPI. Higher DPI = larger file size.", "ExportSettingsDialog")
            )
        else:
            self.custom_dpi_spin.setVisible(False)
            self._update_dpi_info()

    def _update_dpi_info(self):
        '''Update DPI info label based on selection'''
        dpi = self._get_selected_dpi()

        # Calculate approximate file size info
        if dpi <= 72:
            info = tr("Small file size, suitable for screen display.", "ExportSettingsDialog")
        elif dpi <= 150:
            info = tr("Medium file size, suitable for web and presentations.", "ExportSettingsDialog")
        elif dpi <= 300:
            info = tr("Large file size, suitable for printing and high-quality documents.", "ExportSettingsDialog")
        else:
            info = tr("Very large file size, suitable for professional printing.", "ExportSettingsDialog")

        self.dpi_info_label.setText(info)

    def _get_selected_dpi(self) -> int:
        '''Get the currently selected DPI value'''
        dpi_value = self.dpi_combo.currentData()
        if dpi_value == -1:  # Custom
            return self.custom_dpi_spin.value()
        return dpi_value

    def _save_settings(self):
        '''Save settings and close dialog'''
        dpi = self._get_selected_dpi()
        format_val = self.format_combo.currentData()

        self.settings.set_plot_setting('export_dpi', dpi)
        self.settings.set_plot_setting('export_format', format_val)

        QMessageBox.information(
            self,
            tr("Settings Saved", "Messages"),
            tr("Export settings have been saved successfully.", "Messages")
        )

        self.accept()

    def _refresh_ui(self):
        '''Refresh UI with new translations'''
        self.setWindowTitle(tr("Export Settings", "ExportSettingsDialog"))

        # Refresh DPI combo items
        self.dpi_combo.clear()
        for dpi in [72, 150, 300, 600]:
            description = self.DPI_DESCRIPTIONS.get(dpi, "")
            label = f"{dpi} DPI ({tr(description, 'ExportSettingsDialog')})"
            self.dpi_combo.addItem(label, dpi)
        self.dpi_combo.addItem(tr("Custom DPI", "ExportSettingsDialog"), -1)

        # Refresh group titles
        quality_group = self.findChild(QGroupBox)
        if quality_group:
            quality_group.setTitle(tr("Export Quality", "ExportSettingsDialog"))