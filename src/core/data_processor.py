"""
Data Processor - Complete implementation matching original LAOS数据处理0606.py
Handles full preprocessing pipeline: split, noise reduction, phase correction, shear rate, Fourier
Includes TA instrument preprocessing with FFT cycle detection
"""
import os
import glob
import re
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from typing import List, Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal

class DataProcessor(QObject):
    """Data processing class with PyQt signals for progress updates"""
    progress_updated = pyqtSignal(int, str)
    processing_finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.txt_files = []
        self.omega = 2 * np.pi
        self.frequency = 1.0
        self._is_cancelled = False
        self.instrument_type = "haake"
    
    def set_folder_path(self, folder_path: str):
        """Set the working folder path"""
        self.folder_path = folder_path
    
    def set_instrument_type(self, instrument_type: str):
        """Set the instrument type"""
        self.instrument_type = instrument_type
    
    def set_frequency(self, frequency: float):
        """Set the oscillation frequency (Hz)"""
        if frequency > 0:
            self.frequency = frequency
        else:
            self.log_message.emit("Frequency must be positive, using default 1.0 Hz")
            self.frequency = 1.0
    
    def cancel_processing(self):
        """Cancel current processing operation"""
        self._is_cancelled = True
    
    def get_omega(self) -> float:
        """Get the calculated angular frequency"""
        return self.omega
    
    def run_full_preprocess(self) -> bool:
        """Run full preprocessing pipeline - matching original script"""
        if not self.folder_path:
            self.log_message.emit("No folder path set")
            return False
        
        self._is_cancelled = False
        self.log_message.emit("Starting full preprocessing...")
        
        try:
            # Step 1: Split files (10%)
            self.progress_updated.emit(5, "Step 1: Splitting files...")
            self.log_message.emit("=== Step 1: File Splitting ===")
            if not self.split_txt_files():
                self.log_message.emit("File splitting failed or skipped")
            
            # Step 2: Noise reduction (30%)
            self.progress_updated.emit(15, "Step 2: Noise reduction...")
            self.log_message.emit("=== Step 2: Noise Reduction ===")
            if not self.apply_noise_reduction():
                return False
            
            # Step 3: Phase correction (50%)
            self.progress_updated.emit(35, "Step 3: Phase correction...")
            self.log_message.emit("=== Step 3: Phase Correction ===")
            if not self.phase_correction():
                return False
            
            # Step 4: Shear rate calculation (70%)
            self.progress_updated.emit(55, "Step 4: Shear rate calculation...")
            self.log_message.emit("=== Step 4: Shear Rate Calculation ===")
            if not self.calculate_shear_rate():
                return False
            
            # Step 5: Fourier transform (90%)
            self.progress_updated.emit(75, "Step 5: Fourier transform...")
            self.log_message.emit("=== Step 5: Fourier Transform ===")
            if not self.fourier_transform():
                return False
            
            # Calculate omega (100%)
            self.progress_updated.emit(95, "Calculating omega...")
            self._calculate_omega()
            
            self.progress_updated.emit(100, "Preprocessing complete")
            self.log_message.emit("Full preprocessing completed successfully")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Preprocessing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def split_txt_files(self) -> bool:
        """Split original txt files - matching original script step 1"""
        if self._is_cancelled:
            return False
        
        try:
            split_count = 0
            for filename in os.listdir(self.folder_path):
                if self._is_cancelled:
                    return False
                
                if filename.endswith(".txt"):
                    file_path = os.path.join(self.folder_path, filename)
                    
                    # Skip already processed numbered files
                    if re.match(r'^\d+\.txt$', filename):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()
                        
                        # Find "Datapoint no.: " indices
                        datapoint_indices = [i for i, line in enumerate(lines) 
                                            if line.startswith("Datapoint no.:")]
                        
                        if not datapoint_indices:
                            continue
                        
                        for i, index in enumerate(datapoint_indices):
                            # Find data start: search for first line with '#' (column
                            # header), data starts after it. Old format has a unit line
                            # ("- s Pa -") after header; new format doesn't. This
                            # approach handles both.
                            header_idx = None
                            for j in range(index + 1, min(index + 10, len(lines))):
                                if lines[j].strip().startswith("#"):
                                    header_idx = j
                                    break
                            if header_idx is None:
                                continue
                            # Skip header line(s): some formats have a unit line
                            # like "- s Pa -" between the # line and data.
                            data_start = header_idx + 1
                            if data_start < len(lines) and lines[data_start].strip().startswith("-"):
                                data_start += 1

                            if i == len(datapoint_indices) - 1:
                                data_lines = lines[data_start:]
                            else:
                                next_index = datapoint_indices[i + 1]
                                data_lines = lines[data_start:next_index]
                            
                            # Create new filename
                            datapoint_number = lines[index].strip().split(":")[-1].strip()
                            new_filename = f"{datapoint_number.zfill(3)}.txt"
                            new_file_path = os.path.join(self.folder_path, new_filename)
                            
                            # Write data: columns are index(0), stress(2), strain(3)
                            with open(new_file_path, 'w') as new_file:
                                for line in data_lines:
                                    parts = line.strip().split()
                                    if len(parts) >= 4:
                                        new_line = ' '.join([parts[0], parts[2], parts[3]]) + '\n'
                                        new_file.write(new_line)
                            
                            split_count += 1
                    
                    except Exception as e:
                        self.log_message.emit(f"Error splitting {filename}: {str(e)}")
            
            self.log_message.emit(f"Split {split_count} files successfully")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Split files error: {str(e)}")
            return False
    
    def apply_noise_reduction(self) -> bool:
        """Apply background noise reduction - matching original script step 2"""
        if self._is_cancelled:
            return False
        
        try:
            txt_files = glob.glob(os.path.join(self.folder_path, '*.txt'))
            processed_count = 0
            
            for file_path in txt_files:
                if self._is_cancelled:
                    return False
                
                # Only process numbered files
                file_name = os.path.basename(file_path)
                if not file_name[:-4].isdigit():
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Find max/min for column 2 (stress) and column 3 (strain)
                    max_col2 = None
                    min_col2 = None
                    max_col3 = None
                    min_col3 = None
                    
                    for line in lines:
                        data = line.strip().split()
                        if len(data) >= 3:
                            val_col2 = float(data[1])  # stress
                            val_col3 = float(data[2])  # strain
                            
                            if max_col2 is None or val_col2 > max_col2:
                                max_col2 = val_col2
                            if min_col2 is None or val_col2 < min_col2:
                                min_col2 = val_col2
                            if max_col3 is None or val_col3 > max_col3:
                                max_col3 = val_col3
                            if min_col3 is None or val_col3 < min_col3:
                                min_col3 = val_col3
                    
                    # Calculate average (a value)
                    a_col2 = (max_col2 + min_col2) / 2 if max_col2 is not None else 0
                    a_col3 = (max_col3 + min_col3) / 2 if max_col3 is not None else 0
                    
                    # Process and overwrite
                    processed_lines = []
                    for line in lines:
                        data = line.strip().split()
                        if len(data) >= 3:
                            val_col1 = float(data[0])
                            val_col2 = float(data[1])
                            val_col3 = float(data[2])
                            new_val_col2 = val_col2 - a_col2
                            new_val_col3 = val_col3 - a_col3
                            processed_lines.append(f'{val_col1}\t{new_val_col2}\t{new_val_col3}\n')
                    
                    with open(file_path, 'w') as f:
                        f.writelines(processed_lines)
                    
                    processed_count += 1
                    
                except Exception as e:
                    if "Permission denied" not in str(e):
                        self.log_message.emit(f"Error processing {file_name}: {str(e)}")
            
            self.log_message.emit(f"Noise reduction completed: {processed_count} files")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Noise reduction error: {str(e)}")
            return False
    
    def phase_correction(self) -> bool:
        """Phase correction - matching original script step 3"""
        if self._is_cancelled:
            return False
        
        try:
            processed_count = 0
            
            for filename in os.listdir(self.folder_path):
                if self._is_cancelled:
                    return False
                
                if not re.match(r'^\d+\.txt$', filename):
                    continue
                
                file_path = os.path.join(self.folder_path, filename)
                
                data = []
                with open(file_path, 'r') as file:
                    for line in file:
                        values = line.strip().split()
                        if len(values) >= 3:
                            data.append([float(values[0]), float(values[1]), float(values[2])])
                
                if not data:
                    continue
                
                n_points = len(data)
                
                # Find max strain index (column 2, which is strain after preprocessing)
                max_strain_index = max(range(len(data)), key=lambda i: data[i][2])
                
                # Target position: 1/4 of data length
                target_index = n_points // 4
                shift_amount = target_index - max_strain_index
                
                # Shift data
                shifted_data = []
                for i in range(n_points):
                    source_index = (i - shift_amount) % n_points
                    shifted_data.append([i, data[source_index][1], data[source_index][2]])
                
                # Write corrected data
                with open(file_path, 'w') as output_file:
                    for row in shifted_data:
                        output_file.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")
                
                processed_count += 1
            
            self.log_message.emit(f"Phase correction completed: {processed_count} files")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Phase correction error: {str(e)}")
            return False
    
    def calculate_shear_rate(self) -> bool:
        """Calculate shear rate using user-provided frequency - matching LAOS数据处理0606.py"""
        if self._is_cancelled:
            return False
        
        freq = self.frequency
        self.log_message.emit(f"Using frequency: {freq} Hz")
        
        def sin_func(t, A, phi, C):
            return A * np.sin(2 * np.pi * freq * t + phi) + C
        
        def derivative(t, A, phi, C):
            return 2 * np.pi * freq * A * np.cos(2 * np.pi * freq * t + phi)
        
        try:
            txt_files = [f for f in os.listdir(self.folder_path) 
                        if f.endswith('.txt') and f[:-4].isdigit()]
            
            processed_count = 0
            
            for txt_file in txt_files:
                if self._is_cancelled:
                    return False
                
                file_path = os.path.join(self.folder_path, txt_file)
                
                try:
                    data = np.loadtxt(file_path)
                    n_points = len(data)
                    
                    t = data[:, 0] / (freq * n_points)
                    y = data[:, 2]
                    
                    A0 = (np.max(y) - np.min(y)) / 2
                    C0 = np.mean(y)
                    
                    try:
                        params, covariance = curve_fit(sin_func, t, y, p0=[A0, 0, C0])
                        A, phi, C = params
                        
                        new_y = sin_func(t, A, phi, C)
                        derivatives = derivative(t, A, phi, C)
                        
                        data[:, 2] = new_y
                        data_with_derivatives = np.column_stack((data, derivatives))
                        
                        np.savetxt(file_path, data_with_derivatives, delimiter='\t', fmt='%f')
                        
                        processed_count += 1
                        
                    except Exception as fit_error:
                        self.log_message.emit(f"Fit error for {txt_file}, using gradient method: {str(fit_error)}")
                        
                        delta_t = 1.0 / (freq * n_points)
                        derivatives = np.gradient(y, delta_t)
                        data_with_derivatives = np.column_stack((data, derivatives))
                        np.savetxt(file_path, data_with_derivatives, delimiter='\t', fmt='%f')
                        
                        processed_count += 1
                
                except Exception as e:
                    self.log_message.emit(f"Error processing {txt_file}: {str(e)}")
            
            self.log_message.emit(f"Shear rate calculation completed: {processed_count} files")
            self.omega = 2 * np.pi * freq
            self.log_message.emit(f"Calculated omega: {self.omega:.4f} rad/s")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Shear rate calculation error: {str(e)}")
            return False
    
    def fourier_transform(self) -> bool:
        """Fourier transform - matching original script step 6"""
        if self._is_cancelled:
            return False
        
        try:
            # Create output folder
            output_folder = os.path.join(self.folder_path, "fourier_coefficients")
            os.makedirs(output_folder, exist_ok=True)
            
            txt_files = [file for file in glob.glob(os.path.join(self.folder_path, '*.txt'))
                        if re.match(r'^\d+\.txt$', os.path.basename(file))]
            
            processed_count = 0
            
            for txt_file in txt_files:
                if self._is_cancelled:
                    return False
                
                try:
                    with open(txt_file, 'r') as file:
                        lines = file.readlines()
                    
                    stress_data = []
                    strain_data = []
                    
                    for line in lines:
                        columns = line.split()
                        if len(columns) >= 3:
                            stress_data.append(float(columns[1]))
                            strain_data.append(float(columns[2]))
                    
                    # FFT
                    data_array = np.array(stress_data, dtype=float)
                    fourier_coefficients = np.fft.fft(data_array) * 2 / len(data_array)
                    
                    # Calculate I_n for first 30 harmonics
                    result = []
                    for n in range(1, 31):
                        C_n = fourier_coefficients[n]
                        I_n = np.sqrt(np.abs(C_n.real)**2 + np.abs(C_n.imag)**2)
                        result.append((I_n, C_n.real, -C_n.imag))
                    
                    # Save to fourier_coefficients folder
                    output_filepath = os.path.join(output_folder, os.path.basename(txt_file))
                    
                    with open(output_filepath, 'w') as output_file:
                        for i, (I_n, real_part, imag_part) in enumerate(result):
                            output_file.write(f" {I_n}, {real_part},{imag_part}\n")
                    
                    processed_count += 1
                    
                except Exception as e:
                    self.log_message.emit(f"FFT error for {os.path.basename(txt_file)}: {str(e)}")
            
            self.log_message.emit(f"Fourier transform completed: {processed_count} files")
            return True
            
        except Exception as e:
            self.log_message.emit(f"Fourier transform error: {str(e)}")
            return False
    
    def _calculate_omega(self):
        """Calculate angular frequency from user-set frequency"""
        # Use user-provided frequency instead of auto-calculating
        self.omega = 2 * np.pi * self.frequency
        self.log_message.emit(f"Using user-set frequency: {self.frequency:.2f} Hz, omega: {self.omega:.4f} rad/s")
    
    def load_txt_data(self, filepath: str) -> Optional[np.ndarray]:
        """Load txt data from file"""
        try:
            return np.loadtxt(filepath)
        except:
            return None
    
    def scan_ta_excel_sheets(self) -> List[Dict]:
        """Scan TA Excel sheets and return sheet information"""
        if not self.folder_path:
            return []
        
        excel_files = glob.glob(os.path.join(self.folder_path, "*.xls")) + \
                      glob.glob(os.path.join(self.folder_path, "*.xlsx"))
        
        if not excel_files:
            self.log_message.emit("未找到Excel文件")
            return []
        elif len(excel_files) > 1:
            self.log_message.emit("找到多个Excel文件，请确保文件夹中只有一个Excel文件")
            return []
        
        excel_path = excel_files[0]
        file_ext = os.path.splitext(excel_path)[1].lower()
        engine = 'xlrd' if file_ext == '.xls' else 'openpyxl'
        
        self.log_message.emit(f"正在扫描文件: {excel_path}")
        
        sheets_info = []
        try:
            xls = pd.ExcelFile(excel_path, engine=engine)
            
            for sheet_name in xls.sheet_names:
                if sheet_name.startswith("Sine Strain -"):
                    suffix = sheet_name.split(" -")[-1].strip()
                    if suffix.isdigit():
                        sheets_info.append({
                            'sheet_name': sheet_name,
                            'suffix': int(suffix),
                            'suffix_str': f"{int(suffix):02d}"
                        })
            
            self.log_message.emit(f"找到 {len(sheets_info)} 个有效工作表")
            return sheets_info
            
        except Exception as e:
            self.log_message.emit(f"扫描Excel文件出错: {str(e)}")
            return []
    
    def split_ta_excel_files(self, sheets_info, cycle_ranges, frequency) -> bool:
        """
        Split TA Excel files with FFT cycle detection
        Based on LAOS数据处理-yu 0606.py process_sine_strain_sheets
        
        Args:
            sheets_info: List of sheet info dicts
            cycle_ranges: Dict of {suffix: (start_cycle, end_cycle)} or None for auto
            frequency: Oscillation frequency in Hz
        """
        if self._is_cancelled:
            return False
        
        if not self.folder_path:
            self.log_message.emit("No folder path set")
            return False
        
        excel_files = glob.glob(os.path.join(self.folder_path, "*.xls")) + \
                      glob.glob(os.path.join(self.folder_path, "*.xlsx"))
        
        if not excel_files:
            self.log_message.emit("未找到Excel文件")
            return False
        
        excel_path = excel_files[0]
        file_ext = os.path.splitext(excel_path)[1].lower()
        engine = 'xlrd' if file_ext == '.xls' else 'openpyxl'
        
        self.log_message.emit(f"正在处理TA Excel文件: {excel_path}")
        self.log_message.emit(f"频率: {frequency} Hz")
        self.progress_updated.emit(0, "Step 1: Reading Excel sheets...")
        
        try:
            xls = pd.ExcelFile(excel_path, engine=engine)
            processed_count = 0
            total_sheets = len(sheets_info)
            
            for idx, sheet_info in enumerate(sheets_info):
                if self._is_cancelled:
                    return False
                
                progress_pct = int(10 * (idx + 1) / total_sheets) if total_sheets > 0 else 10
                self.progress_updated.emit(progress_pct, f"Step 1: Processing sheet {idx+1}/{total_sheets}...")
                
                sheet_name = sheet_info['sheet_name']
                suffix_str = sheet_info['suffix_str']
                suffix = sheet_info['suffix']
                
                self.log_message.emit(f"--- 处理工作表: '{sheet_name}' ---")
                
                try:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1, 
                                      usecols=["Stress", "Strain"])
                except ValueError as e:
                    self.log_message.emit(f"未找到 'Stress' 或 'Strain' 列，跳过: {str(e)}")
                    continue
                
                df = df.apply(pd.to_numeric, errors='coerce').dropna()
                total_rows = len(df)
                
                if total_rows < 10:
                    self.log_message.emit("数据过少，无法分析周期，跳过")
                    continue
                
                strain_data = df["Strain"].values
                
                # ========== FFT确定主周期长度 ==========
                n = len(strain_data)
                if n < 20:
                    self.log_message.emit("数据点太少，无法进行FFT分析，跳过")
                    continue
                
                try:
                    fft_vals = np.fft.fft(strain_data - np.mean(strain_data))
                    fft_mag = np.abs(fft_vals[:n // 2])
                    freqs = np.fft.fftfreq(n, d=1.0)[:n // 2]
                    
                    if len(fft_mag) > 1:
                        dominant_idx = np.argmax(fft_mag[1:]) + 1
                        freq_value = freqs[dominant_idx]
                        dominant_freq = freq_value if freq_value > 0.001 else None
                        cycle_length_fft = int(round(1.0 / dominant_freq)) if dominant_freq and dominant_freq > 0.001 else None
                    else:
                        cycle_length_fft = None
                except Exception as e:
                    self.log_message.emit(f"FFT计算出错: {str(e)}")
                    cycle_length_fft = None
                
                if cycle_length_fft:
                    self.log_message.emit(f"FFT检测周期长度: {cycle_length_fft}")
                else:
                    self.log_message.emit("FFT未检测到有效周期")
                
                # ========== 波峰中位数辅助验证 ==========
                peaks, _ = find_peaks(strain_data, distance=10)
                
                if len(peaks) < 2 and cycle_length_fft is None:
                    self.log_message.emit("未检测到足够的波峰且FFT未找到周期，跳过")
                    continue
                
                if len(peaks) >= 2:
                    cycle_lengths_arr = np.diff(peaks)
                    cycle_length_median = int(round(np.median(cycle_lengths_arr)))
                    self.log_message.emit(f"波峰中位数周期长度: {cycle_length_median}")
                else:
                    cycle_length_median = None
                
                # 综合确定周期长度
                if cycle_length_fft and cycle_length_median:
                    if abs(cycle_length_fft - cycle_length_median) <= 2:
                        candidates = [cycle_length_fft, cycle_length_median]
                        even_candidates = [c for c in candidates if c % 2 == 0]
                        cycle_length = even_candidates[0] if even_candidates else cycle_length_fft
                    else:
                        cycle_length = cycle_length_fft
                elif cycle_length_fft:
                    cycle_length = cycle_length_fft
                else:
                    cycle_length = cycle_length_median
                
                if cycle_length is None or cycle_length < 5:
                    self.log_message.emit("无法确定有效的周期长度，跳过")
                    continue
                
                self.log_message.emit(f"确定标准周期长度为: {cycle_length} 个数据点")
                
                # ========== 基于相位确定周期边界 ==========
                mean_strain = np.mean(strain_data)
                cycle_start = 0
                
                if len(peaks) >= 1:
                    first_peak = peaks[0]
                    for j in range(1, min(first_peak + 1, len(strain_data))):
                        if strain_data[j - 1] <= mean_strain and strain_data[j] > mean_strain:
                            cycle_start = j
                            break
                
                if cycle_start == 0 and len(peaks) >= 1:
                    for j in range(1, len(strain_data)):
                        if strain_data[j - 1] <= mean_strain and strain_data[j] > mean_strain:
                            cycle_start = j
                            break
                
                self.log_message.emit(f"估算第一个周期的起始索引: {cycle_start}")
                
                # ========== 分割周期 ==========
                valid_cycles = []
                cycle_idx = 0
                
                while True:
                    start_idx = cycle_start + cycle_idx * cycle_length
                    end_idx = start_idx + cycle_length
                    if end_idx > len(df):
                        break
                    cycle_df = df.iloc[start_idx:end_idx].copy()
                    valid_cycles.append(cycle_df)
                    cycle_idx += 1
                
                num_cycles = len(valid_cycles)
                if num_cycles == 0:
                    self.log_message.emit("没有完整的有效周期，跳过")
                    continue
                
                self.log_message.emit(f"共找到 {num_cycles} 个完整的标准周期")
                
                # ========== 选择周期范围 ==========
                if cycle_ranges and suffix in cycle_ranges:
                    x, y = cycle_ranges[suffix]
                    self.log_message.emit(f"使用自定义周期范围: 第 {x} 到第 {y} 周期")
                    selected_indices = list(range(x - 1, y))
                else:
                    # 自动选择相对误差小于阈值的周期
                    error_threshold = 0.05  # 5% 相对误差阈值
                    
                    # 计算每个周期的应力振幅和应变振幅
                    cycle_amplitudes = []
                    for cycle_df in valid_cycles:
                        stress = cycle_df["Stress"].values
                        strain = cycle_df["Strain"].values
                        stress_amp = (stress.max() - stress.min()) / 2
                        strain_amp = (strain.max() - strain.min()) / 2
                        cycle_amplitudes.append((stress_amp, strain_amp))
                    
                    # 计算平均振幅作为参考
                    if len(cycle_amplitudes) > 0:
                        avg_stress_amp = np.mean([amp[0] for amp in cycle_amplitudes])
                        avg_strain_amp = np.mean([amp[1] for amp in cycle_amplitudes])
                        
                        # 计算每个周期的相对误差
                        selected_indices = []
                        for i, (stress_amp, strain_amp) in enumerate(cycle_amplitudes):
                            stress_error = abs(stress_amp - avg_stress_amp) / avg_stress_amp if avg_stress_amp > 0 else 0
                            strain_error = abs(strain_amp - avg_strain_amp) / avg_strain_amp if avg_strain_amp > 0 else 0
                            max_error = max(stress_error, strain_error)
                            
                            if max_error < error_threshold:
                                selected_indices.append(i)
                        
                        if len(selected_indices) == 0:
                            # 如果没有符合条件的周期，放宽阈值或使用后半段
                            self.log_message.emit(f"没有周期满足相对误差<{error_threshold*100}%阈值，放宽阈值至10%")
                            error_threshold = 0.10
                            for i, (stress_amp, strain_amp) in enumerate(cycle_amplitudes):
                                stress_error = abs(stress_amp - avg_stress_amp) / avg_stress_amp if avg_stress_amp > 0 else 0
                                strain_error = abs(strain_amp - avg_strain_amp) / avg_strain_amp if avg_strain_amp > 0 else 0
                                max_error = max(stress_error, strain_error)
                                if max_error < error_threshold:
                                    selected_indices.append(i)
                            
                            if len(selected_indices) == 0:
                                # 仍然没有，使用后半段
                                self.log_message.emit("仍无符合条件的周期，使用后半段数据")
                                selected_indices = list(range(num_cycles // 2, num_cycles))
                        else:
                            self.log_message.emit(f"自动选择: {len(selected_indices)}个周期满足相对误差<{error_threshold*100}%阈值")
                            self.log_message.emit(f"选中的周期: 第{selected_indices[0]+1}到第{selected_indices[-1]+1}周期")
                    else:
                        selected_indices = list(range(num_cycles // 2, num_cycles))
                
                if len(selected_indices) == 0:
                    self.log_message.emit(f"周期范围无效，跳过")
                    continue
                
                try:
                    selected_cycles = [valid_cycles[i] for i in selected_indices]
                    if len(selected_cycles) == 0:
                        self.log_message.emit("选择的周期数为0，跳过")
                        continue
                    
                    selected_values = np.stack([cycle.values for cycle in selected_cycles])
                    averaged_values = selected_values.mean(axis=0)
                    
                    result_df = pd.DataFrame(averaged_values, columns=["Stress", "Strain"])
                    result_df.insert(0, "Index", range(1, cycle_length + 1))
                    result_df = result_df[["Index", "Stress", "Strain"]]
                    
                    output_path = os.path.join(self.folder_path, f"{suffix_str}.txt")
                    result_df.to_csv(output_path, sep='\t', index=False, header=False)
                    
                    cycle_info = f"第{selected_indices[0]+1}到第{selected_indices[-1]+1}周期 (共{len(selected_indices)}个周期)"
                    self.log_message.emit(f"已创建: {output_path} ({cycle_info}的平均值)")
                    processed_count += 1
                except Exception as e:
                    self.log_message.emit(f"周期平均计算出错: {str(e)}")
                    continue
            
            if processed_count > 0:
                self.log_message.emit(f"TA Excel处理完成: {processed_count} 个工作表")
                
                # Continue with full preprocessing pipeline
                self.log_message.emit("继续执行预处理步骤...")
                
                # Step 2: Noise reduction
                self.progress_updated.emit(15, "Step 2: Noise reduction...")
                if not self.apply_noise_reduction():
                    return False
                
                # Step 3: Phase correction
                self.progress_updated.emit(35, "Step 3: Phase correction...")
                if not self.phase_correction():
                    return False
                
                # Step 4: Shear rate (use provided frequency)
                self.progress_updated.emit(55, "Step 4: Shear rate calculation...")
                self.set_frequency(frequency)
                if not self.calculate_shear_rate():
                    return False
                
                # Step 5: Fourier transform
                self.progress_updated.emit(75, "Step 5: Fourier transform...")
                if not self.fourier_transform():
                    return False
                
                self.progress_updated.emit(100, "TA preprocessing complete")
                self.log_message.emit("TA Excel预处理全部完成")
                return True
            else:
                self.log_message.emit("没有处理任何工作表")
                return False
            
        except Exception as e:
            self.log_message.emit(f"处理出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_ta_already_processed(self) -> bool:
        """Check if TA data has already been processed"""
        processed_files = [f for f in os.listdir(self.folder_path) 
                          if re.match(r'^\d+\.txt$', f)]
        
        if not processed_files:
            return False
        
        sample_file = os.path.join(self.folder_path, processed_files[0])
        try:
            with open(sample_file, 'r') as f:
                first_line = f.readline()
                if len(first_line.strip().split()) >= 4:
                    fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
                    if os.path.exists(fourier_folder):
                        return True
        except:
            pass
        
        return False