"""
Activation Dialog for LAOS Analysis
"""

import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from utils.activation import verify_activation_code, save_activation, get_expected_activation_code
from utils.responsive import get_ui_scale


class ActivationDialog(QDialog):
    '''Dialog for software activation'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LAOS Analysis - Activation")
        self.setMinimumWidth(get_ui_scale().scaled(400))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self._activated = False
        self._setup_ui()

    def _setup_ui(self):
        '''Setup the dialog UI'''
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Software Activation")
        title_font = QFont("Segoe UI", get_ui_scale().scaled(16), QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel("Please enter your activation code to use this software.\nThe activation is valid for this computer only.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666;")
        layout.addWidget(desc_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)

        code_label = QLabel("Activation Code:")
        layout.addWidget(code_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("LAOS-XXXX-XXXX-XXXX")
        self.code_input.setStyleSheet(f"""
            QLineEdit {{
                padding: {get_ui_scale().scaled(10)}px;
                font-size: {get_ui_scale().scaled(14)}px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }}
            QLineEdit:focus {{
                border: 2px solid #2196F3;
            }}
        """)
        self.code_input.textChanged.connect(self._format_code)
        layout.addWidget(self.code_input)

        hint_label = QLabel("Demo code: LAOS-8888-8888-8888")
        hint_label.setStyleSheet(f"color: #999; font-size: {get_ui_scale().scaled(11)}px;")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setStyleSheet(f"""
            QPushButton {{
                padding: {get_ui_scale().scaled(10)}px {get_ui_scale().scaled(30)}px;
                font-size: {get_ui_scale().scaled(14)}px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:pressed {{
                background-color: #1565C0;
            }}
        """)
        self.activate_btn.clicked.connect(self._on_activate)
        self.activate_btn.setDefault(True)
        button_layout.addWidget(self.activate_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #F44336;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def _format_code(self, text):
        '''Auto-format the activation code'''
        cleaned = "".join(c for c in text.upper())
        if not cleaned.startswith("LAOS"):
            if cleaned.startswith("L"):
                cleaned = "LAOS" + cleaned[1:]
            else:
                cleaned = "LAOS-" + cleaned

        parts = cleaned.replace("LAOS-", "").replace("-", "")
        if len(parts) > 0:
            formatted = "LAOS-"
            for i in range(0, min(len(parts), 12), 4):
                formatted += parts[i:i + 4]
                if i + 4 < len(parts) and len(formatted) < 18:
                    formatted += "-"
            cleaned = formatted

        if cleaned != text:
            self.code_input.setText(cleaned)

    def _on_activate(self):
        '''Handle activation button click'''
        code = self.code_input.text().strip()
        if not code:
            self.status_label.setText("Please enter an activation code")
            return

        valid, message = verify_activation_code(code)
        if valid:
            if save_activation(code):
                self._activated = True
                QMessageBox.information(self, "Success", "Activation successful!\n\nYou can now use LAOS Analysis.")
                self.accept()
            else:
                self.status_label.setText("Failed to save activation. Please try again.")
        else:
            self.status_label.setText("Invalid activation code. Please check and try again.")

    def closeEvent(self, event):
        '''Prevent closing without activation'''
        if not self._activated:
            event.ignore()
            QMessageBox.warning(self, "Activation Required", "You must activate the software before using it.\n\nClick 'Activate' button after entering your code.")
        else:
            event.accept()

    def keyPressEvent(self, event):
        '''Handle key press events'''
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self._on_activate()
        elif event.key() == Qt.Key_Escape:
            QMessageBox.warning(self, "Activation Required", "You must activate the software before using it.")
        else:
            super().keyPressEvent(event)