# LAOS Analysis Software

**v1.0 · Windows x64 · Desktop application for nonlinear rheology**

[Download v1.0](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.0) · [Getting started](docs/GETTING-STARTED.md) · [English manual](docs/User-Manual-EN.pdf) · [中文说明](README.zh-CN.md) · [Video tutorials](videos/README.md)

## Overview

LAOS Analysis is a graphical desktop application for processing and interpreting large-amplitude oscillatory shear (LAOS) measurements. It brings raw-data preparation, nonlinear viscoelastic analysis, and figure export into one local workflow, helping researchers compare complementary descriptions of a material's response within and across oscillation cycles.

The application is intended for researchers working with soft materials and complex fluids, including polymer solutions, suspensions, gels, and food materials. It combines Fourier rheology, Chebyshev analysis, stress bifurcation, sequence of physical processes (SPP), Lissajous curves, dissipation analysis, and cage-modulus calculations. Results should be interpreted together with experimental conditions and the assumptions of each method.

## Features

| Area | Capabilities |
| --- | --- |
| Data preparation | Instrument-specific HAAKE/TA workflows, data segmentation, cycle selection, denoising, phase alignment, and Fourier analysis |
| Waveform visualization | Lissajous curves, normalized representations, and overlays across selected test points |
| Harmonic analysis | Single- and multiple-order Fourier coefficients; Chebyshev-based S and T measures |
| Yielding and dissipation | Stress-bifurcation analysis, dissipation ratio, and cage modulus |
| Intra-cycle analysis | SPP plots and overlays; analytical (Fourier) and numerical (gradient) calculation modes; circular decomposition |
| Presentation | Interactive plots, adjustable styles, figure export, and multilingual interface |
| Learning materials | Six example datasets, English and Chinese manuals, and ten demonstration videos |

## Installation

1. Download [LAOS-Analysis-V1.0-Windows-x64.zip](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip).
2. Extract the **entire ZIP** into a writable local directory.
3. Open the extracted `LAOS-Analysis-V1.0` folder and launch `LAOS_Analysis.exe`.
4. Keep `_internal` in the same directory as the executable.

This is a portable **64-bit Windows** distribution. Python and the runtime dependencies are bundled, so no separate Python installation or `pip install` step is required. Allow roughly 2 GB of free space for the extracted application and additional space for working data and results. This is a storage allowance, not a measured minimum system requirement.

Use the named **Windows ZIP** above. GitHub's automatically generated **Source code** archives contain this documentation repository and do not contain the complete Windows application. See [installation and troubleshooting](docs/INSTALLATION.md).

## Quick start

1. Make a working copy of `Test Data/Test Data HAAKE/2%` from the application package.
2. Open the application and select that sample folder, which contains numbered TXT files and its `fourier_coefficients` subfolder.
3. Select one of the available numbered test points and choose the Lissajous plotting function.
4. Generate the plot, inspect axis labels and units, then adjust the style and export a figure.
5. Follow the [Lissajous demonstration](videos/README.md) and try the harmonic, dissipation, or SPP workflows using the same sample.

The bundled numbered files are already processed examples. To start from raw measurements, copy the original HAAKE TXT or TA Excel input into a separate working folder and follow [the preprocessing tutorial](docs/GETTING-STARTED.md). Enter the actual acquisition frequency and use consistent stress and strain units.

## Data formats

| Input | Expected organization |
| --- | --- |
| HAAKE raw export | TXT blocks containing `Datapoint no.:` markers and the exported signal columns; retain the instrument export structure |
| TA raw export | One `.xls` or `.xlsx` workbook in the working folder; sheets named `Sine Strain -<number>` with `Stress` and `Strain` columns on Excel row 2 |
| Processed signal | Numerically named files such as `000.txt` or `01.txt`, with whitespace-separated numeric columns: index/time coordinate, stress, strain, and strain rate when available |
| Fourier coefficients | Matching numbered files in `fourier_coefficients/`; preserve the generated column order and names |

File layout and units matter. A generic CSV or arbitrary Excel table is not automatically equivalent to one of these layouts. Read the [data-format reference](docs/DATA-FORMATS.md) before preparing your own files.

## Examples, manuals, and videos

| Resource | Link |
| --- | --- |
| Complete Windows application, examples, and manuals | [Windows ZIP](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip) |
| Six HAAKE/TA example datasets separately | [Examples ZIP](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Examples.zip) · [Dataset guide](examples/README.md) |
| English user manual | [PDF](docs/User-Manual-EN.pdf) |
| Chinese user manual | [PDF](docs/User-Manual-ZH.pdf) |
| Ten original demonstration videos | [Video index](videos/README.md) |
| Download integrity | [SHA256SUMS.txt](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/SHA256SUMS.txt) |

## Project structure

```text
LAOS-Analysis-Software/
├── README.md                 English project homepage
├── README.zh-CN.md           Chinese introduction
├── CHANGELOG.md              Release history
├── CITATION.cff              Software citation metadata
├── COPYRIGHT.md             Copyright and existing notices
├── docs/
│   ├── INSTALLATION.md       Installation and troubleshooting
│   ├── GETTING-STARTED.md    First plot and preprocessing workflow
│   ├── DATA-FORMATS.md       Input layouts and units
│   ├── DEPENDENCIES.md       Runtime component overview
│   ├── RELEASE-CONTENTS.md  Distribution contents
│   ├── User-Manual-EN.pdf
│   └── User-Manual-ZH.pdf
├── examples/
│   ├── README.md             Dataset descriptions and download link
│   └── data-manifest.csv     File list and individual checksums
└── videos/
    └── README.md             Ten video download links
```

The extracted Windows ZIP contains `LAOS_Analysis.exe`, `_internal/`, `Test Data/`, and the documentation. Large application and video files are provided as release assets. This repository is the distribution and documentation home; it does not currently provide a supported source-build workflow.

## Dependencies

The packaged application uses Python, PyQt5/Qt, PyQtGraph, NumPy, pandas, SciPy, Matplotlib, Plotly, and supporting libraries for graphics, Excel reading, and export. These components are shipped with the Windows package. Users do not need to install them independently. See [the dependency overview](docs/DEPENDENCIES.md) for their roles.

## Authors and affiliation

- **Ziyu Zhou** — [GitHub: ZhouZiyuMizar](https://github.com/ZhouZiyuMizar)
- **Hongbin Zhang**

**Advanced Institute of Rheology, Shanghai Jiao Tong University.** Author names and institutional attribution follow the supplied English user manual.

## Citation

If you use the software in research, please cite **LAOS Analysis Software, v1.0** using [CITATION.cff](CITATION.cff) or GitHub's **Cite this repository** feature. Cite the original methodological literature relevant to your analysis as well; references are available in the manuals.

## Support and reproducibility

Please report issues through [GitHub Issues](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/issues). Include the software version, Windows environment, selected method and parameters, error message, and a small reproducible input when possible. Record acquisition frequency, units, selected cycles, preprocessing choices, and harmonic settings when reporting analysis results.

Existing example outputs are supplied as reference files; they are not a new validation dataset generated for this release. See [release history](CHANGELOG.md).

## Copyright

See [COPYRIGHT.md](COPYRIGHT.md). Existing copyright and third-party notices are retained. This distribution does not introduce a new open-source license.
