# Example Data

This folder contains the example datasets distributed with LAOS Analysis
Software v1.0.

You can use the examples in two ways:

- Browse the files directly in [`Test Data/`](Test%20Data/).
- Download the standalone examples package from the
  [v1.0 release](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.0).

The same example data are also included in the complete Windows application
package.

## Included Datasets

| Folder under `Test Data` | Raw input or workbook | Numbered data files |
| --- | --- | --- |
| `Test Data HAAKE/2%` | `2%.txt`, `2%.xlsx` | 60 |
| `Test Data HAAKE/20260508/1% CNF` | `1% CNF-1.txt` | 120 |
| `Test Data HAAKE/20260508/CNC` | `CNC.txt` | 120 |
| `Test Data HAAKE/20260508/XG` | `xg.txt` | 60 |
| `Test Data TA/Sample 1` | `1 (10) mosha.xls` | 63 |
| `Test Data TA/Sample 2` | `1 up mosha.xls` | 61 |

## How to Use the Examples

1. Make a working copy before processing, because the application may write
   result files into the selected folder.
2. Select a sample folder that directly contains numbered TXT files.
3. Keep the matching `fourier_coefficients` folder next to the numbered files.
4. For raw preprocessing, copy the original HAAKE TXT export or TA Excel workbook
   into a separate working folder and follow the manual.

The numbered TXT files and accompanying coefficients are processed example
files. Other included output tables are reference outputs, not newly
recalculated results.

Fourier coefficient examples in this release are comma-delimited so they can be
loaded directly by the harmonic plotting workflow. Some original legacy exports
used whitespace delimiters; those files were normalized for the release package
with numeric values unchanged.

See [data-manifest.csv](data-manifest.csv) for the included file list and
SHA-256 checksums.
