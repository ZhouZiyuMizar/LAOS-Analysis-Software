# LAOS Analysis Software

**v1.0, Windows x64 desktop software for nonlinear rheology**

[Download the Windows app](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.0) | [Source code](src/) | [Example data](examples/Test%20Data/) | [English manual](docs/User-Manual-EN.pdf) | [Chinese README](README.zh-CN.md)

## Overview

LAOS Analysis Software is a desktop application for processing and interpreting large-amplitude oscillatory shear measurements. It supports raw-data preparation, nonlinear viscoelastic analysis, and figure export in one local workflow.

The software is designed for researchers working with soft materials and complex fluids, including polymer solutions, suspensions, gels, and food materials. It includes Fourier rheology, Chebyshev analysis, stress bifurcation, sequence of physical processes analysis, Lissajous curves, dissipation analysis, and cage-modulus calculations.

## Features

| Area | Main functions |
| --- | --- |
| Data preparation | HAAKE and TA workflows, data segmentation, cycle selection, denoising, phase alignment, and Fourier analysis |
| Waveform visualization | Lissajous curves, normalized plots, and overlays across selected test points |
| Harmonic analysis | Single-order and multi-order Fourier coefficients, plus Chebyshev-based S and T values |
| Yielding and dissipation | Stress bifurcation, dissipation ratio, and cage modulus |
| Intra-cycle analysis | SPP plots, analytical and numerical calculation modes, and circular decomposition |
| Output | Interactive plots, adjustable styles, figure export, and multilingual interface |

## Download

There are three common ways to use this repository.

| Need | Recommended route |
| --- | --- |
| Run the software directly | Download `LAOS-Analysis-V1.0-Windows-x64.zip` from the [v1.0 release](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.0). This package contains `LAOS_Analysis.exe`, the required runtime, manuals, and example data. |
| Read or modify the source code | Browse the [`src/`](src/) folder, clone the repository, or use GitHub's green **Code** button. |
| Use the example data | Browse [`examples/Test Data/`](examples/Test%20Data/) in the repository, clone the repository, or download `LAOS-Analysis-V1.0-Examples.zip` from the release page. |

GitHub's automatically generated **Source code** archives contain the repository files, including the source code and example data. They do not contain the full Windows runtime package. To run the packaged application, use the Windows ZIP from the release page.

## Installation

For normal use on Windows:

1. Download [LAOS-Analysis-V1.0-Windows-x64.zip](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip).
2. Extract the entire ZIP into a writable local folder.
3. Open the extracted `LAOS-Analysis-V1.0` folder.
4. Run `LAOS_Analysis.exe`.
5. Keep `_internal` in the same folder as the executable.

The Windows package includes Python and the required runtime libraries. Users do not need to install Python separately.

To run from source, install Python 3.8 or a compatible Python 3 version, install the packages in [`requirements.txt`](requirements.txt), then run:

```bash
python src/main.py
```

The source tree is provided for transparency, review, and further development. The tested end-user distribution is the Windows package on the release page.

## Quick Start

1. Start the packaged application.
2. Copy one sample folder from `examples/Test Data/` or from the `Test Data` folder inside the Windows package.
3. Select a folder that directly contains numbered TXT files, such as `Test Data HAAKE/2%`.
4. Choose one numbered test point.
5. Generate a Lissajous plot, inspect the axis labels and units, then export the figure.
6. Follow the [video tutorials](videos/README.md) for Fourier coefficients, dissipation ratio, stress bifurcation, SPP plotting, and cage modulus.

The included numbered TXT files are processed examples. To start from raw measurements, copy the original HAAKE TXT export or TA Excel workbook into a separate working folder and follow the manual.

## Data Formats

| Input | Expected organization |
| --- | --- |
| HAAKE raw export | TXT blocks containing `Datapoint no.:` markers and the exported signal columns |
| TA raw export | One `.xls` or `.xlsx` workbook in the working folder, with sheets named `Sine Strain -<number>` |
| Processed signal | Numbered files such as `000.txt` or `01.txt`, with numeric columns for the processed waveform |
| Fourier coefficients | Matching numbered files in `fourier_coefficients/`, using the generated coefficient layout |

See [docs/DATA-FORMATS.md](docs/DATA-FORMATS.md) for details. File layout and units matter. A generic CSV or arbitrary Excel table is not automatically equivalent to one of the supported formats.

## Project Structure

```text
LAOS-Analysis-Software/
  src/                    source code and application resources
  examples/
    Test Data/            bundled HAAKE and TA example datasets
    data-manifest.csv     file list and SHA-256 checksums
  docs/                   manuals and technical notes
  videos/                 links to the demonstration videos
  README.md               English project guide
  README.zh-CN.md         Chinese project guide
  requirements.txt        source-run dependencies
  CITATION.cff            citation metadata
  LICENSE                 CC BY 4.0 license notice
```

The executable Windows package is not stored directly in the Git tree. It is provided through GitHub Releases because it contains the runtime environment and is much larger than normal source files.

## Dependencies

The source code uses PyQt5, PyQtGraph, NumPy, pandas, SciPy, Matplotlib, Plotly, and PyOpenGL. See [`requirements.txt`](requirements.txt) and [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md).

The packaged Windows application already includes its runtime dependencies.

## License and Citation

This repository is released under the Creative Commons Attribution 4.0 International License. See [LICENSE](LICENSE).

If you use this software, source code, documentation, or example data in academic work, please cite **LAOS Analysis Software, v1.0** using [CITATION.cff](CITATION.cff) or GitHub's **Cite this repository** feature.

## Authors and Affiliation

- Ziyu Zhou, [GitHub: ZhouZiyuMizar](https://github.com/ZhouZiyuMizar)
- Hongbin Zhang, hbzhang@sjtu.edu.cn

Advanced Rheology Institute, Shanghai Jiao Tong University.

## Support

Please report issues through [GitHub Issues](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/issues). Include the software version, Windows environment, selected method and parameters, error message, and a small reproducible input when possible.
