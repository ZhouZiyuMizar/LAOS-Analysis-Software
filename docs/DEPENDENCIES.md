# Dependencies and runtime

## For application users

The Windows ZIP includes its Python runtime and dependencies. Do not install a separate Python environment or replace individual bundled libraries to run this package. Keep the supplied `_internal` directory intact.

## Component overview

| Component | Role |
| --- | --- |
| Python runtime | Application execution |
| PyQt5 / Qt and Qt plugins | Desktop interface, widgets, and supporting display components |
| PyQtGraph / PyOpenGL | Interactive plotting and graphics support |
| NumPy | Numeric arrays and Fourier operations |
| pandas | Tabular data and workbook handling |
| SciPy | Signal processing, numerical routines, and optimization |
| Matplotlib | Scientific plots and figure export |
| Plotly / Kaleido | Plotly-based visualization and export support |
| openpyxl / xlrd | Excel-reading engines used for XLSX / XLS workflows |
| Pillow and supporting libraries | Image handling and supporting runtime functions |
| PyInstaller | Tool used to assemble the Windows distribution; not an installation requirement for users |

The release also contains platform libraries, Qt resources, fonts, translations, and existing third-party notices. Some Python modules may be bundled inside application archives rather than visible as individual folders.

## Source-build status

This repository currently distributes the application, documentation, examples, and tutorial links. It does not provide a supported source-build workflow or a verified environment lockfile. The table describes component roles, not independently installable version constraints. A generic `pip install` list would not reproduce the supplied binary reliably, so no unverified requirements file is presented as a build recipe.

Existing third-party licenses remain applicable; bundled notices are retained. See [Copyright](../COPYRIGHT.md).
