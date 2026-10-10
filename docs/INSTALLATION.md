# Installation and Troubleshooting

## Recommended Windows Package

Download [the v1.0 Windows ZIP](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip), extract it fully, and run `LAOS_Analysis.exe`.

Keep `_internal` in the same folder as the executable. Do not run the software
from inside an archive viewer. Choose a writable location for working data and
results.

The Windows package includes Python and the required runtime libraries.

## Source Code

The source code is available in [`src/`](../src/). To run from source:

```bash
pip install -r requirements.txt
python src/main.py
```

The source route is useful for inspection and development. For normal use, the
Windows package is simpler and more stable.

## Example Data

Example data are available in two places:

- directly in [`examples/Test Data/`](../examples/Test%20Data/);
- inside the Windows package under `Test Data`.

A standalone examples ZIP is also provided on the release page for users who
want to download the data without the full application.

## Language

Repository documentation is in English by default, with Chinese materials also
provided. The application has a language setting; select English there if saved
preferences or system language choose another language.

## Common Problems

| Symptom | Check |
| --- | --- |
| Missing DLL or runtime error | Extract the full Windows ZIP again and ensure `_internal` remains beside the EXE |
| No EXE in the download | Use `LAOS-Analysis-V1.0-Windows-x64.zip`, not GitHub's automatic source archive |
| No files shown | Select one sample folder containing numbered TXT files, rather than the parent `Test Data` folder |
| TA worksheet not recognized | Keep one workbook in the working folder and check the worksheet/header layout in [Data formats](DATA-FORMATS.md) |
| Export or processing cannot write files | Move the working data to a writable folder and confirm the output is not open in another program |
| Unexpected units or amplitudes | Check stress/strain units, experimental frequency, selected test point, and preprocessing parameters |
| SPP or harmonic workflow lacks inputs | Retain the matching `fourier_coefficients` directory and complete the required preprocessing stages |

## Verify a Download

Compare the ZIP's SHA-256 hash with [SHA256SUMS.txt](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/SHA256SUMS.txt).

In PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '.\LAOS-Analysis-V1.0-Windows-x64.zip'
```
