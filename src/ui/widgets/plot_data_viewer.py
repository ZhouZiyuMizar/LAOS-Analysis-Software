# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\plot_data_viewer.py
"""
Data Table Widget - Display plot data in Excel-like table format
Embedded as a tab in the main window
"""
import os, numpy as np
from typing import Optional, List, Dict
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QGroupBox, QHeaderView, QSplitter, QComboBox, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from utils.i18n import tr
from utils.responsive import get_ui_scale

class DataTableWidget(QWidget):
    __doc__ = "\n    Widget for displaying plot data in Excel-like table format\n    Embedded as a tab in the plot container\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._current_data = None
        self._current_headers = []
        self._current_title = ""
        get_ui_scale().register(self)

    def apply_ui_scale(self):
        """Re-apply UI scale to scaled inline styles after a font change."""
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: {get_ui_scale().scaled(14)}px; color: #2196F3;")

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        header_layout = QHBoxLayout()
        self.title_label = QLabel(tr("Plot Data", "DataTable"))
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: {get_ui_scale().scaled(14)}px; color: #2196F3;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        self.export_btn = QPushButton(tr("Export to Excel", "DataTable"))
        self.export_btn.setStyleSheet("\n            QPushButton {\n                background-color: #4CAF50;\n                color: white;\n                padding: 5px 15px;\n                border-radius: 3px;\n            }\n            QPushButton:hover {\n                background-color: #45a049;\n            }\n        ")
        self.export_btn.clicked.connect(self._export_to_excel)
        header_layout.addWidget(self.export_btn)
        self.copy_all_btn = QPushButton(tr("Copy All", "DataTable"))
        self.copy_all_btn.setStyleSheet("\n            QPushButton {\n                background-color: #2196F3;\n                color: white;\n                padding: 5px 15px;\n                border-radius: 3px;\n            }\n            QPushButton:hover {\n                background-color: #1976D2;\n            }\n        ")
        self.copy_all_btn.clicked.connect(self._copy_all_to_clipboard)
        header_layout.addWidget(self.copy_all_btn)
        self.clear_btn = QPushButton(tr("Clear", "DataTable"))
        self.clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(self.clear_btn)
        layout.addLayout(header_layout)
        self.info_label = QLabel(tr("No data loaded", "DataTable"))
        self.info_label.setStyleSheet(f"color: gray; font-size: {get_ui_scale().scaled(11)}px;")
        layout.addWidget(self.info_label)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("\n            QTableWidget {\n                gridline-color: #d0d0d0;\n                background-color: #fafafa;\n            }\n            QTableWidget::item {\n                padding: 2px;\n            }\n            QHeaderView::section {\n                background-color: #e0e0e0;\n                padding: 5px;\n                border: 1px solid #c0c0c0;\n                font-weight: bold;\n            }\n        ")
        layout.addWidget(self.table)

    def show_lissajous_data(self, file_number: str, data: np.ndarray):
        """
        Show Lissajous curve data (stress, strain, strain_rate)

        Args:
            file_number: File number string (e.g., "030")
            data: Data array with columns [time, stress, strain, strain_rate]
        """
        self._current_title = f"Lissajous Curve - File {file_number}"
        self.title_label.setText(self._current_title)
        if data.shape[1] >= 4:
            headers = [
             tr("Index", "DataTable"),
             tr("Stress (σ)", "DataTable"),
             tr("Strain (γ)", "DataTable"),
             tr("Strain Rate (γ̇)", "DataTable")]
            row_indices = np.arange(len(data)).reshape(-1, 1)
            display_data = np.column_stack([row_indices, data[:, 1:4]])
        else:
            headers = [tr("Column " + str(i + 1), "DataTable") for i in range(data.shape[1])]
            display_data = data
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(data)} data points", "DataTable"))

    def show_st_values(self, strain: np.ndarray, S: np.ndarray, T: np.ndarray, G_l: np.ndarray=None, G_m: np.ndarray=None, eta_l: np.ndarray=None, eta_m: np.ndarray=None):
        """
        Show ST values data

        Args:
            strain: Strain values
            S: S values
            T: T values
            G_l: G'_L values (optional)
            G_m: G'_M values (optional)
            eta_l: η'_L values (optional)
            eta_m: η'_M values (optional)
        """
        self._current_title = "ST Values"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain (γ)", "DataTable"),
            tr("S", "DataTable"),
            tr("T", "DataTable")]
        if G_l is not None:
            if G_m is not None:
                headers.append(tr("G'_L (Pa)", "DataTable"))
                headers.append(tr("G'_M (Pa)", "DataTable"))
        if eta_l is not None:
            if eta_m is not None:
                headers.append(tr("η'_L (Pa·s)", "DataTable"))
                headers.append(tr("η'_M (Pa·s)", "DataTable"))
        display_data = np.column_stack([strain, S, T])
        if G_l is not None:
            if G_m is not None:
                display_data = np.column_stack([display_data, G_l, G_m])
        if eta_l is not None:
            if eta_m is not None:
                display_data = np.column_stack([display_data, eta_l, eta_m])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_spp_data(self, file_number: str, data: np.ndarray):
        """
        Show SPP method data

        Args:
            file_number: File number string
            data: SPP data array [Gt', Gt'', dGt'/dt, dGt''/dt]
        """
        self._current_title = f"SPP Data - File {file_number}"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Gt' (G' prime)", "DataTable"),
            tr("Gt'' (G'' double prime)", "DataTable"),
            tr("dGt'/dt", "DataTable"),
            tr("dGt''/dt", "DataTable")]
        self._populate_table(data, headers)
        self.info_label.setText(tr(f"Total {len(data)} data points", "DataTable"))

    def show_spp_circular_data(self, file_number: str, component: str, components, mean, residual):
        """Show circular decomposition components (radius / frequency / direction)."""
        comp_label = "dG′ₜ/dt - dG″ₜ/dt" if component == "Gt_deriv" else "G′ₜ - G″ₜ"
        self._current_title = f"Circular Decomposition - File {file_number} ({comp_label})"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Harmonic n", "DataTable"),
            tr("ω (rad/s)", "DataTable"),
            tr("Direction", "DataTable"),
            tr("Radius |c|", "DataTable"),
            tr("Phase (deg)", "DataTable"),
            tr("Real", "DataTable"),
            tr("Imag", "DataTable")]
        rows = []
        for c in components:
            rows.append([
                c['n'],
                c['omega'],
                "CCW" if c['direction'] == 'ccw' else "CW",
                c['radius'],
                c['phase_deg'],
                c['real'],
                c['imag'],
            ])
        if rows:
            arr = np.array([[r[0], r[1], 1 if r[2] == "CCW" else -1, r[3], r[4], r[5], r[6]]
                            for r in rows], dtype=object)
        else:
            arr = np.empty((0, 7))
        self._populate_table(arr, headers)
        self.info_label.setText(
            tr(f"Total {len(rows)} components, residual {residual*100:.3g}%", "DataTable"))

        def show_spp_multi_data(self, file_numbers, folder_path):
            pass



    def show_fourier_multi(self, file_list, max_harmonic, folder_path):
        """
        Show multi-file Fourier coefficients Iₙ/I₁ data

        Args:
            file_list: List of Fourier coefficient file names
            max_harmonic: Maximum harmonic number to display
            folder_path: Folder containing fourier_coefficients
        """
        import os, numpy as np
        self._current_title = "Multi-File Fourier Coefficients (Iₙ/I₁)"
        self.title_label.setText(self._current_title)
        fourier_folder = os.path.join(folder_path, "fourier_coefficients")
        headers = [
            tr("File", "DataTable")]
        for n in range(1, min(max_harmonic + 1, 31)):
            headers.append(tr(f"I{self._get_subscript(n)}/I₁", "DataTable"))
        else:
            data_rows = []
            for ffile in file_list:
                try:
                    fpath = os.path.join(fourier_folder, ffile)
                    with open(fpath, "r") as f:
                        lines = f.readlines()
                    row = [ffile.replace(".txt", "")]
                    if len(lines) > 0:
                        first_line = lines[0].strip()
                        i1 = float(first_line.split(",")[0].strip() if "," in first_line else first_line.split()[0])
                        for n in range(1, min(max_harmonic + 1, len(lines) + 1)):
                            nth_line = lines[n - 1].strip()
                            in_val = float(nth_line.split(",")[0].strip() if "," in nth_line else nth_line.split()[0])
                            ratio = in_val / i1 if i1 != 0 else 0
                            row.append(ratio)
                        else:
                            while True:
                                if len(row) < len(headers):
                                    row.append(0)

                    else:
                        row.extend([0] * (len(headers) - 1))
                    data_rows.append(row)
                except Exception:
                    continue

            else:
                if data_rows:
                    display_data = np.array(data_rows)
                    self._populate_table(display_data, headers)
                    self.info_label.setText(tr(f"Total {len(data_rows)} files", "DataTable"))
                else:
                    self.info_label.setText(tr("No data available", "DataTable"))

    def show_fourier_ratio(self, strain_values, ratio_values, harmonics):
        """
        Show In/I1 ratio data
        
        Args:
            strain_values: Array of strain amplitudes
            ratios: In/I1 ratios
            harmonics: Harmonic number
        """
        self._current_title = f"I{harmonics}/I1 Ratio"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain (γ)", "DataTable"),
            tr(f"I{self._get_subscript(harmonics)}/I₁", "DataTable")]
        display_data = np.column_stack([strain_values, ratio_values])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain_values)} data points", "DataTable"))
    
    def show_q_value(self, strain_values: np.ndarray, q_values: np.ndarray):
        """
        Show Q value data: Q = I3/I1/(strain0)^2
        
        Args:
            strain_values: Array of strain amplitudes (strain0)
            q_values: Array of Q values
        """
        self._current_title = tr("Q Value", "DataTable")
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain (γ₀)", "DataTable"),
            tr("Q Value", "DataTable")]
        display_data = np.column_stack([strain_values, q_values])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain_values)} data points", "DataTable"))

    def show_fourier_multi_data(self, fourier_data: dict, max_harmonic: int):
        """
        Show multi-file Fourier coefficients data
        
        Args:
            fourier_data: Dictionary with file_number as key, containing:
                - strain: strain amplitude
                - harmonics: harmonic numbers list
                - ratios: In/I1 ratios list
            max_harmonic: Maximum harmonic number
        """
        self._current_title = f"Fourier Coefficients (n=1-{max_harmonic})"
        self.title_label.setText(self._current_title)
        
        headers = [tr("File", "DataTable"), tr("Strain", "DataTable")]
        for n in range(1, max_harmonic + 1):
            headers.append(tr(f"I{self._get_subscript(n)}/I₁", "DataTable"))
        
        rows = []
        for file_num, data in sorted(fourier_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
            row = [file_num, f"{data['strain']:.4f}"]
            ratios = data['ratios']
            for ratio in ratios:
                row.append(f"{ratio:.6e}")
            while len(row) < len(headers):
                row.append("")
            rows.append(row)
        
        if rows:
            display_data = np.array(rows)
            self._populate_table(display_data, headers)
            self.info_label.setText(tr(f"Total {len(fourier_data)} files", "DataTable"))
        else:
            self.info_label.setText(tr("No data available", "DataTable"))

    def _get_subscript(self, n):
        """Convert number to subscript characters"""
        subscript_digits = [
         '₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
        return "".join((subscript_digits[int(d)] for d in str(n)))

    def show_stress_bifurcation(self, sigma_0: np.ndarray, gamma_0: np.ndarray, gamma_dot_0: np.ndarray, gamma_sigma_0: np.ndarray, sigma_gamma_0: np.ndarray, sigma_gamma_dot_0: np.ndarray, gamma_dot_sigma_0: np.ndarray):
        """
        Show stress bifurcation data (all 7 columns)

        Args:
            sigma_0: Maximum stress (σ_0)
            gamma_0: Maximum strain (γ_0)
            gamma_dot_0: Maximum strain rate (γ̇_0)
            gamma_sigma_0: Strain at maximum stress (γ_{σ_0})
            sigma_gamma_0: Stress at maximum strain (σ_{γ_0})
            sigma_gamma_dot_0: Stress at maximum strain rate (σ_{γ̇_0})
            gamma_dot_sigma_0: Strain rate at maximum stress (γ̇_{σ_0})
        """
        self._current_title = "Stress Bifurcation"
        self.title_label.setText(self._current_title)
        headers = [
            tr("σ_0 (Max Stress)", "DataTable"),
            tr("γ_0 (Max Strain)", "DataTable"),
            tr("γ̇_0 (Max Strain Rate)", "DataTable"),
            tr("γ_{σ_0} (Strain at σ_max)", "DataTable"),
            tr("σ_{γ_0} (Stress at γ_max)", "DataTable"),
            tr("σ_{γ̇_0} (Stress at γ̇_max)", "DataTable"),
            tr("γ̇_{σ_0} (Strain Rate at σ_max)", "DataTable")]
        display_data = np.column_stack([sigma_0, gamma_0, gamma_dot_0, 
         gamma_sigma_0,  sigma_gamma_0, 
         sigma_gamma_dot_0,  gamma_dot_sigma_0])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(sigma_0)} files analyzed", "DataTable"))

    def show_dissipation_rate(self, strain: np.ndarray, dissipation: np.ndarray):
        """
        Show dissipation rate data

        Args:
            strain: Strain values
            dissipation: Dissipation rate values
        """
        self._current_title = "Dissipation Rate"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain", "DataTable"),
            tr("Dissipation Rate", "DataTable")]
        display_data = np.column_stack([strain, dissipation])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_cage_modulus(self, strain: np.ndarray, G_ratio: np.ndarray):
        """
        Show cage modulus data

        Args:
            strain: Strain values
            G_ratio: G'/G_cage ratio values
        """
        self._current_title = "Cage Modulus"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain", "DataTable"),
            tr("$G'/G_{cage}$", "DataTable")]
        display_data = np.column_stack([strain, G_ratio])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_cage_modulus_gcage(self, strain: np.ndarray, G_cage: np.ndarray):
        """
        Show G_cage vs strain data

        Args:
            strain: Strain values
            G_cage: G_cage values
        """
        self._current_title = "Cage Modulus ($G_{cage}$)"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain", "DataTable"),
            tr("$G_{cage}$ (Pa)", "DataTable")]
        display_data = np.column_stack([strain, G_cage])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_contact_stress(self, file_number: str, strain: np.ndarray, stress: np.ndarray, sigma_H: np.ndarray, sigma_C: np.ndarray):
        """
        Show contact stress decomposition data

        Args:
            file_number: File number
            strain: Strain values
            stress: Total stress
            sigma_H: Hydrodynamic stress
            sigma_C: Contact stress
        """
        self._current_title = f"Contact Stress - File {file_number}"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain (γ)", "DataTable"),
            tr("Total Stress (σ)", "DataTable"),
            tr("σ_H (Hydrodynamic)", "DataTable"),
            tr("σ_C (Contact)", "DataTable")]
        display_data = np.column_stack([strain, stress, sigma_H, sigma_C])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_contact_stress_viscous(self, file_number: str, strain_rate: np.ndarray, stress: np.ndarray, eta_H: float, eta_HC: float):
        """
        Show viscous Lissajous contact stress data

        Args:
            file_number: File number
            strain_rate: Strain rate values
            stress: Total stress
            eta_H: Hydrodynamic viscosity
            eta_HC: Total viscosity
        """
        self._current_title = f"Contact Stress (Viscous) - File {file_number}"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain Rate (γ̇)", "DataTable"),
            tr("Total Stress (σ)", "DataTable"),
            tr("σ_H = η_H × γ̇", "DataTable"),
            tr("σ_HC = η_HC × γ̇", "DataTable")]
        sigma_H = eta_H * strain_rate
        sigma_HC = eta_HC * strain_rate
        display_data = np.column_stack([strain_rate, stress, sigma_H, sigma_HC])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain_rate)} data points", "DataTable"))

    def show_xi_sigma_batch(self, strain_amplitudes: np.ndarray, xi_max: np.ndarray, sigma_C_max: np.ndarray):
        """
        Show ξ_max and σ_C_max batch analysis data

        Args:
            strain_amplitudes: Strain amplitude values
            xi_max: ξ_max values
            sigma_C_max: σ_C_max values
        """
        self._current_title = "ξ_max and σ_C_max vs Strain"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain Amplitude", "DataTable"),
            tr("ξ_max", "DataTable"),
            tr("σ_C_max", "DataTable")]
        display_data = np.column_stack([strain_amplitudes, xi_max, sigma_C_max])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain_amplitudes)} files analyzed", "DataTable"))

    def show_in_i1_ratio(self, strain: np.ndarray, ratios: np.ndarray, n: int):
        """
        Show In/I1 ratio data

        Args:
            strain: Strain values
            ratios: In/I1 ratios
            n: Harmonic number
        """
        self._current_title = f"I{n}/I1 Ratio"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain", "DataTable"),
            tr(f"I{n}/I1", "DataTable")]
        display_data = np.column_stack([strain, ratios])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strain)} data points", "DataTable"))

    def show_fourier_coefficients(self, file_number: str, harmonics: np.ndarray, In_I1: np.ndarray):
        """
        Show Fourier coefficients data

        Args:
            file_number: File number
            harmonics: Harmonic numbers
            In_I1: In/I1 ratios
        """
        self._current_title = f"Fourier Coefficients - File {file_number}"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Harmonic (n)", "DataTable"),
            tr("In/I1", "DataTable")]
        display_data = np.column_stack([harmonics, In_I1])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(harmonics)} harmonics", "DataTable"))

    def show_overlay_data(self, file_numbers: List[str], data_list: List[np.ndarray]):
        """
        Show overlay data from multiple files

        Args:
            file_numbers: List of file numbers
            data_list: List of data arrays
        """
        self._current_title = f"Overlay Data - {len(file_numbers)} files"
        self.title_label.setText(self._current_title)
        headers = [
            tr("File Number", "DataTable"),
            tr("Data Points", "DataTable")]
        rows = [[
         num, len(data)] for num, data in zip(file_numbers, data_list)]
        display_data = np.array(rows)
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(file_numbers)} files", "DataTable"))

    def show_same_strain_in_i1(self, file_indices: List[int], strain: float, harmonics: np.ndarray, In_I1_list: List[np.ndarray]):
        """
        Show same strain different In/I1 comparison data

        Args:
            file_indices: File indices
            strain: Strain value
            harmonics: Harmonic numbers
            In_I1_list: List of In/I1 ratio arrays
        """
        self._current_title = f"Same Strain In/I1 - γ={strain:.4f}"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Harmonic (n)", "DataTable")]
        for idx in file_indices:
            headers.append(tr(f"File {idx}", "DataTable"))
        else:
            n_harmonics = len(harmonics)
            display_data = np.zeros((n_harmonics, len(headers)))
            display_data[:, 0] = harmonics
            for i, ratios in enumerate(In_I1_list):
                display_data[:, i + 1] = ratios[:n_harmonics]
            else:
                self._populate_table(display_data, headers)
                self.info_label.setText(tr(f"{len(file_indices)} files at strain {strain:.4f}", "DataTable"))

    def show_different_strain_in_i1(self, strains: np.ndarray, ratios: np.ndarray, n: int):
        """
        Show different strain same In/I1 ratio data

        Args:
            strains: Strain values
            ratios: In/I1 ratios
            n: Harmonic number
        """
        self._current_title = f"Different Strain I{n}/I1"
        self.title_label.setText(self._current_title)
        headers = [
            tr("Strain", "DataTable"),
            tr(f"I{n}/I1", "DataTable")]
        display_data = np.column_stack([strains, ratios])
        self._populate_table(display_data, headers)
        self.info_label.setText(tr(f"Total {len(strains)} data points", "DataTable"))

    def _populate_table(self, data: np.ndarray, headers: List[str]):
        """Populate the table widget with data"""
        self._current_data = data
        self._current_headers = headers
        self.table.clear()
        rows, cols = data.shape if len(data.shape) > 1 else (len(data), 1)
        if cols == 1:
            if len(data.shape) == 1:
                data = data.reshape(-1, 1)
                cols = 1
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels(headers)
        for row in range(rows):
            for col in range(cols):
                value = data[(row, col)]
                if isinstance(value, str):
                    item = QTableWidgetItem(value)
                elif not hasattr(value, "dtype") or value.dtype.kind in ('U', 'S', 'O'):
                    item = QTableWidgetItem(str(value))
                else:
                    if abs(float(value)) < 0.001 or abs(float(value)) > 1000:
                        item = QTableWidgetItem((f"{float(value):.6e}"))
                    else:
                        item = QTableWidgetItem((f"{float(value):.6g}"))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if row % 2 == 0:
                    item.setBackground(QColor(255, 255, 255))
                else:
                    item.setBackground(QColor(240, 240, 240))
                self.table.setItem(row, col, item)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(20)

    def _export_to_excel(self):
        """Export current data to Excel file"""
        if self._current_data is None:
            QMessageBox.warning(self, tr("Warning", "DataTable"), tr("No data to export", "DataTable"))
            return
        
        default_name = f'{self._current_title.replace(" ", "_")}.xlsx'
        file_path, _ = QFileDialog.getSaveFileName(self, tr("Export to Excel", "DataTable"), default_name, "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            import pandas as pd
            df = pd.DataFrame(self._current_data, columns=self._current_headers)
            df.to_excel(file_path, index=False, engine="openpyxl")
            QMessageBox.information(self, tr("Success", "DataTable"), tr(f"Data exported to:\n{file_path}", "DataTable"))
        except ImportError:
            QMessageBox.warning(self, tr("Error", "DataTable"), tr("pandas or openpyxl not installed.\nCannot export to Excel.", "DataTable"))
        except Exception as e:
            QMessageBox.critical(self, tr("Error", "DataTable"), tr(f"Export failed: {str(e)}", "DataTable"))

    def _copy_all_to_clipboard(self):
        """Copy all table data to clipboard in tab-separated format"""
        if self.table.rowCount() == 0 or self.table.columnCount() == 0:
            return
        
        from PyQt5.QtWidgets import QApplication
        
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text() if self.table.horizontalHeaderItem(col) else "")
        
        text_lines = ["\t".join(headers)]
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            text_lines.append("\t".join(row_data))
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(text_lines))
        self.info_label.setText(tr(f"Copied {self.table.rowCount()} rows to clipboard", "DataTable"))

    def clear(self):
        """Clear the viewer"""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self._current_data = None
        self._current_headers = []
        self._current_title = ""
        self.title_label.setText(tr("Plot Data", "DataTable"))
        self.info_label.setText(tr("No data loaded", "DataTable"))


class PlotDataViewer(QWidget):
    __doc__ = "\n    Standalone dialog-style widget for plot data preview\n    (kept for backward compatibility)\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Plot Data Viewer", "PlotDataViewer"))
        self.setMinimumSize(600, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        self.data_table = DataTableWidget()
        layout.addWidget(self.data_table)

    def show_lissajous_data(self, file_number, data):
        self.data_table.show_lissajous_data(file_number, data)
        self.show()

    def show_st_values(self, strain, S, T, G_l=None, G_m=None, eta_l=None, eta_m=None):
        self.data_table.show_st_values(strain, S, T, G_l, G_m, eta_l, eta_m)
        self.show()

    def show_spp_data(self, file_number, data):
        self.data_table.show_spp_data(file_number, data)
        self.show()

    def show_spp_circular_data(self, file_number, component, components, mean, residual):
        self.data_table.show_spp_circular_data(file_number, component, components, mean, residual)
        self.show()

    def show_contact_stress(self, file_number, strain, stress, sigma_H, sigma_C):
        self.data_table.show_contact_stress(file_number, strain, stress, sigma_H, sigma_C)
        self.show()

    def show_stress_bifurcation(self, sigma_0, gamma_0, gamma_dot_0, gamma_sigma_0, sigma_gamma_0, sigma_gamma_dot_0, gamma_dot_sigma_0):
        self.data_table.show_stress_bifurcation(sigma_0, gamma_0, gamma_dot_0, gamma_sigma_0, sigma_gamma_0, sigma_gamma_dot_0, gamma_dot_sigma_0)
        self.show()

    def show_fourier_multi(self, file_list, max_harmonic, folder_path):
        self.data_table.show_fourier_multi(file_list, max_harmonic, folder_path)
        self.show()

    def show_fourier_ratio(self, strain_values, ratio_values, harmonics):
        self.data_table.show_fourier_ratio(strain_values, ratio_values, harmonics)
        self.show()

    def show_spp_multi_data(self, file_numbers, folder_path):
        self.data_table.show_spp_multi_data(file_numbers, folder_path)
        self.show()

    def clear(self):
        self.data_table.clear()