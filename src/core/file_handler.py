# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: core\file_handler.py
"""
File Handler - Handles file operations for ChemicalStrain GUI
"""
import os, re, glob
from typing import List, Tuple, Optional

class FileHandler:
    __doc__ = "\n    File handling class for folder selection, file listing, and format validation\n    "

    def __init__(self):
        self.folder_path = ""
        self.txt_files = []
        self.numbers_txt_files = []
        self.excel_file = None

    def set_folder_path(self, folder_path: str) -> bool:
        """
        Set the working folder path and scan for files

        Args:
            folder_path: Path to the folder containing data files

        Returns:
            bool: True if folder exists and contains valid files
        """
        if not os.path.exists(folder_path):
            return False
        self.folder_path = folder_path
        self._scan_files()
        return True

    def _scan_files(self):
        """Scan folder for txt and excel files"""
        self.txt_files = []
        self.numbers_txt_files = []
        self.excel_file = None
        txt_pattern = os.path.join(self.folder_path, "*.txt")
        self.txt_files = glob.glob(txt_pattern)
        for file_path in self.txt_files:
            basename = os.path.basename(file_path)
            if self.check_txt_digital_path(basename):
                self.numbers_txt_files.append(file_path)
        else:
            self.numbers_txt_files.sort(key=(lambda x: int(os.path.basename(x).replace(".txt", ""))))
            for file in os.listdir(self.folder_path):
                if file.endswith(".xlsx") or file.endswith(".xls"):
                    if not file.startswith("~"):
                        self.excel_file = os.path.join(self.folder_path, file)
                        break

    def get_folder_path(self) -> str:
        """Get current folder path"""
        return self.folder_path

    def get_txt_files(self) -> List[str]:
        """Get all txt files in folder"""
        return self.txt_files

    def get_numbers_txt_files(self) -> List[str]:
        """Get numbered txt files (e.g., 00.txt, 01.txt)"""
        return self.numbers_txt_files

    def get_file_count(self) -> int:
        """Get count of numbered txt files"""
        return len(self.numbers_txt_files)

    def get_excel_file(self) -> Optional[str]:
        """Get Excel file path if exists"""
        return self.excel_file

    def has_excel_file(self) -> bool:
        """Check if Excel file exists"""
        return self.excel_file is not None

    @staticmethod
    def check_txt_digital_path(filename: str) -> bool:
        """
        Check if filename matches pattern: number.txt

        Args:
            filename: The filename to check

        Returns:
            bool: True if filename is like "00.txt", "01.txt", etc.
        """
        return bool(re.match("^\\d+\\.txt$", filename))

    @staticmethod
    def check_file_exists(filepath: str) -> bool:
        """
        Check if file exists

        Args:
            filepath: Full path to file

        Returns:
            bool: True if file exists
        """
        return os.path.exists(filepath)

    def get_file_info(self, file_index: int) -> dict:
        """
        Get information about a specific file

        Args:
            file_index: Index in numbers_txt_files list

        Returns:
            dict: File information including path, size, modification time
        """
        if file_index < 0 or file_index >= len(self.numbers_txt_files):
            return {}
        file_path = self.numbers_txt_files[file_index]
        stat = os.stat(file_path)
        return {'path':file_path, 
         'name':(os.path.basename)(file_path), 
         'size':stat.st_size, 
         'modified':stat.st_mtime}

    def get_fourier_files(self) -> List[str]:
        """Get Fourier coefficient files from subfolder"""
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            return []
        files = glob.glob(os.path.join(fourier_folder, "*.txt"))
        files.sort(key=(lambda x: int(os.path.basename(x).replace(".txt", ""))))
        return files

    def get_spp_data_files(self) -> List[str]:
        """Get SPP data files from subfolder"""
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            return []
        files = glob.glob(os.path.join(spp_folder, "*.txt"))
        return files

    def get_rebuild_files(self) -> List[str]:
        """Get rebuild files from subfolder"""
        rebuild_folder = os.path.join(self.folder_path, "rebuild")
        if not os.path.exists(rebuild_folder):
            return []
        return glob.glob(os.path.join(rebuild_folder, "*.txt"))

    def create_subfolder(self, subfolder_name: str) -> str:
        """
        Create a subfolder in the current working directory

        Args:
            subfolder_name: Name of subfolder to create

        Returns:
            str: Path to created subfolder
        """
        subfolder_path = os.path.join(self.folder_path, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def validate_folder(self) -> Tuple[(bool, str)]:
        """
        Validate the current folder for LAOS analysis

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not self.folder_path:
            return (False, 'No folder selected')
        if not os.path.exists(self.folder_path):
            return (False, 'Folder does not exist')
        if len(self.numbers_txt_files) == 0:
            return (False, 'No numbered txt files found (e.g., 00.txt, 01.txt)')
        return (True, f"Found {len(self.numbers_txt_files)} data files")
