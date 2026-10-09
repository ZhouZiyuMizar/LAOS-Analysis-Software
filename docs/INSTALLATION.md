# Installation and troubleshooting

## Windows package

Download [the v1.0 Windows ZIP](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip), extract it fully, and open `LAOS_Analysis.exe`. The executable is built for Windows x64. Keep its `_internal` directory intact and adjacent to the EXE. No Python, Conda, compiler, or package-manager setup is needed for the portable package.

Choose a writable location for working data and results. Do not start the application from inside an archive viewer. Allow roughly 2 GB for the extracted application, with additional space for your data and exported figures. A precise minimum CPU/RAM requirement has not been established for this release; workload depends on dataset size and analysis settings.

## Language

Repository documentation is in English by default, with Chinese materials also provided. The application has a language setting; select English there if your saved preferences or system language select another language. Repository language does not override existing application preferences.

## Common problems

| Symptom | Check |
| --- | --- |
| Missing DLL or runtime error | Extract the full Windows ZIP again and ensure `_internal` remains beside the EXE |
| No EXE in the download | Use `LAOS-Analysis-V1.0-Windows-x64.zip`, not the automatic Source code archive |
| No files shown | Select one sample folder containing numeric TXT filenames, rather than the parent `Test Data` folder |
| TA worksheet not recognized | Keep one workbook in the working folder and check the worksheet/header layout in [Data formats](DATA-FORMATS.md) |
| Export or processing cannot write files | Move the working data to a writable folder and confirm the output is not open in another program |
| Unexpected units or amplitudes | Check stress/strain units, experimental frequency, selected test point, and preprocessing parameters |
| SPP or harmonic workflow lacks inputs | Retain the matching `fourier_coefficients` directory and complete the required preprocessing stages |

For further troubleshooting, consult Chapter 5 of the [English manual](User-Manual-EN.pdf). When reporting an issue, include the exact message and a minimal reproducible example.

## Verify a download

Compare the ZIP's SHA-256 hash with [SHA256SUMS.txt](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/SHA256SUMS.txt). In PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '.\LAOS-Analysis-V1.0-Windows-x64.zip'
```
