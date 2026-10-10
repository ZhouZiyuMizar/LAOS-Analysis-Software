'''
Step Indicator Widget - Visual progress indicator for multi-step workflows
'''

from typing import List, Optional
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

from utils.i18n import tr
from utils.responsive import get_ui_scale


class StepIndicator(QWidget):
    '''
    Visual step indicator showing progress through a workflow

    Displays numbered steps with states:
    - pending: gray, waiting
    - active: blue, currently processing
    - completed: green, done
    - error: red, failed
    '''

    # Signal emitted when a step is clicked
    step_clicked = pyqtSignal(int)

    # Step states
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ERROR = 'error'

    # Style definitions
    STYLES = {
        'pending': """
            QLabel {
                background-color: #E0E0E0;
                color: #757575;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
        """,
        'active': """
            QLabel {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """,
        'completed': """
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
        """,
        'error': """
            QLabel {
                background-color: #F44336;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
        """
    }

    CONNECTOR_STYLES = {
        'pending': "background-color: #E0E0E0;",
        'active': "background-color: #2196F3;",
        'completed': "background-color: #4CAF50;",
        'error': "background-color: #F44336;"
    }

    def __init__(self, steps: Optional[List[str]] = None, parent=None):
        '''
        Initialize step indicator

        Args:
            steps: List of step names (optional, can be set later)
            parent: Parent widget
        '''
        super().__init__(parent)
        self._steps: List[str] = steps or []
        self._states: List[str] = []
        self._step_labels: List[QLabel] = []
        self._connectors: List[QFrame] = []
        self._current_step = -1

        self._init_ui()
        get_ui_scale().register(self)

    def _scaled_style(self, style: str) -> str:
        '''Scale pixel metrics in a step style for the current UI scale.'''
        return get_ui_scale().scale_stylesheet(style)

    def apply_ui_scale(self):
        '''Re-apply UI scale to step labels and connectors.'''
        scale = get_ui_scale()
        for i, label in enumerate(self._step_labels):
            state = self._states[i] if i < len(self._states) else self.PENDING
            label.setMinimumHeight(scale.scaled(28))
            label.setStyleSheet(self._scaled_style(self.STYLES.get(state, self.STYLES[self.PENDING])))
        for connector in self._connectors:
            connector.setFixedWidth(scale.scaled(15))
            connector.setFixedHeight(scale.scaled(3))

    def _init_ui(self):
        '''Initialize the user interface'''
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(0)

        if self._steps:
            self._build_steps()

        self._layout.addStretch()

    def set_steps(self, steps: List[str]):
        '''
        Set the list of steps

        Args:
            steps: List of step names
        '''
        # Clear existing
        self._clear_steps()

        self._steps = steps
        self._states = [self.PENDING] * len(steps)
        self._build_steps()

    def _clear_steps(self):
        '''Clear existing step widgets'''
        for label in self._step_labels:
            label.deleteLater()
        for connector in self._connectors:
            connector.deleteLater()

        self._step_labels = []
        self._connectors = []
        self._states = []
        self._current_step = -1

    def _build_steps(self):
        '''Build step widgets from current step list'''
        for i, step_name in enumerate(self._steps):
            # Create step label
            label = QLabel(f"{i+1}. {step_name}")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(get_ui_scale().scaled(28))
            label.setStyleSheet(self._scaled_style(self.STYLES[self.PENDING]))
            label.setCursor(Qt.PointingHandCursor)
            label.mousePressEvent = lambda event, idx=i: self._on_step_clicked(idx)

            self._layout.addWidget(label)
            self._step_labels.append(label)

            # Create connector line (except after last step)
            if i < len(self._steps) - 1:
                connector = QFrame()
                connector.setFrameShape(QFrame.HLine)
                connector.setFixedWidth(get_ui_scale().scaled(15))
                connector.setFixedHeight(get_ui_scale().scaled(3))
                connector.setStyleSheet(self.CONNECTOR_STYLES[self.PENDING])

                self._layout.addWidget(connector)
                self._connectors.append(connector)

    def _on_step_clicked(self, index: int):
        '''Handle step label click'''
        self.step_clicked.emit(index)

    def set_current_step(self, index: int):
        '''
        Set the currently active step

        Args:
            index: Step index (0-based)
        '''
        if index < 0 or index >= len(self._steps):
            return

        self._current_step = index

        # Update all step styles
        for i in range(len(self._steps)):
            if i < index:
                # Completed steps before current
                state = self._states[i] if self._states[i] == self.ERROR else self.COMPLETED
            elif i == index:
                state = self.ACTIVE
            else:
                state = self.PENDING

            self._update_step_style(i, state)

        # Update connectors
        for i, connector in enumerate(self._connectors):
            if i < index:
                connector.setStyleSheet(self.CONNECTOR_STYLES[self.COMPLETED])
            else:
                connector.setStyleSheet(self.CONNECTOR_STYLES[self.PENDING])

    def set_step_state(self, index: int, state: str):
        '''
        Set the state of a specific step

        Args:
            index: Step index (0-based)
            state: One of PENDING, ACTIVE, COMPLETED, ERROR
        '''
        if index < 0 or index >= len(self._steps):
            return

        self._states[index] = state
        self._update_step_style(index, state)

    def _update_step_style(self, index: int, state: str):
        '''Update the style of a step label'''
        if 0 <= index < len(self._step_labels):
            self._step_labels[index].setStyleSheet(self._scaled_style(self.STYLES.get(state, self.STYLES[self.PENDING])))
            self._states[index] = state

    def reset(self):
        '''Reset all steps to pending state'''
        self._current_step = -1
        for i in range(len(self._steps)):
            self._update_step_style(i, self.PENDING)
        for connector in self._connectors:
            connector.setStyleSheet(self.CONNECTOR_STYLES[self.PENDING])

    def get_current_step(self) -> int:
        '''Get the current step index'''
        return self._current_step

    def get_step_count(self) -> int:
        '''Get the total number of steps'''
        return len(self._steps)


class PreprocessStepIndicator(StepIndicator):
    '''
    Step indicator specifically for preprocessing workflow
    '''

    # Preprocessing steps
    PREPROCESS_STEPS = [
        ("split", "Split Files"),
        ("noise", "Noise Reduction"),
        ("phase", "Phase Correction"),
        ("shear", "Shear Rate"),
        ("fourier", "Fourier Transform")
    ]

    def __init__(self, parent=None):
        '''Initialize preprocessing step indicator'''
        # Translate step names
        steps = [tr(name, "PreprocessSteps") for _, name in self.PREPROCESS_STEPS]
        super().__init__(steps, parent)

        # Store step codes for mapping
        self._step_codes = [code for code, _ in self.PREPROCESS_STEPS]

    def set_step_by_code(self, code: str):
        '''
        Set current step by code

        Args:
            code: Step code ('split', 'noise', 'phase', 'shear', 'fourier')
        '''
        if code in self._step_codes:
            index = self._step_codes.index(code)
            self.set_current_step(index)

    def get_step_code(self, index: int) -> Optional[str]:
        '''Get step code by index'''
        if 0 <= index < len(self._step_codes):
            return self._step_codes[index]
        return None