# Dependencies and Runtime

## Packaged Windows Application

The Windows ZIP includes its Python runtime and dependencies. Users should keep
the supplied `_internal` directory intact and beside `LAOS_Analysis.exe`.

No separate Python, Conda, compiler, or package-manager setup is needed for the
packaged application.

## Running from Source

The cleaned source code is available in [`src/`](../src/). To run it, install
Python 3.8 or a compatible Python 3 version, then install:

```bash
pip install -r requirements.txt
python src/main.py
```

The source tree is provided for transparency, review, and further development.
The packaged Windows release remains the recommended route for normal use.

## Component Overview

| Component | Role |
| --- | --- |
| Python | Application execution |
| PyQt5 and Qt | Desktop interface and widgets |
| PyQtGraph and PyOpenGL | Interactive plotting and graphics support |
| NumPy | Numeric arrays and Fourier operations |
| pandas | Tabular data and workbook handling |
| SciPy | Signal processing, numerical routines, and optimization |
| Matplotlib | Scientific plots and figure export |
| Plotly | Plotly-based visualization and export support |
| openpyxl and xlrd | Excel-reading engines used for XLSX and XLS workflows |
| PyInstaller | Tool used to assemble the Windows distribution |

Third-party packages remain under their own licenses. The repository license is
described in [LICENSE](../LICENSE).
