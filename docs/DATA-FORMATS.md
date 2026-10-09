# Data formats

This reference describes the layouts used by the supplied examples and application readers. Preserve an untouched copy of raw instrument exports and process a separate working copy.

## HAAKE raw TXT

HAAKE examples contain repeated test-point blocks introduced by `Datapoint no.:`. The raw export includes a column-label line and instrument metadata before the numeric rows. One supplied file begins with this structure:

```text
Datapoint no.: 0
 #  Time [s]  Stress [Pa]  Strain [-]
TorqueRatio ...
AngleRatio ...
0 0.000000e+00 ... ...
1 1.953125e-03 ... ...
```

Ellipses are explanatory placeholders, not valid data. Use the unedited example export as the reference. Preserve test-point markers and the original column ordering. The instrument export is not the same format as the processed numbered TXT files.

## TA Excel workbooks

- Extensions: `.xls` and `.xlsx`.
- Place **one workbook** in the working folder for the TA scan.
- Recognized sheet names begin with `Sine Strain -` followed by a numeric suffix, for example `Sine Strain -1`.
- The reader uses the **second Excel row** as the header (`header=1`) and selects columns named exactly `Stress` and `Strain`.
- The processing workflow requires the experimental frequency in Hz.

Adding arbitrary column names or renaming a generic spreadsheet to `.xls` does not create a compatible export. Confirm the original units, especially fractional strain versus percent strain; the labels alone do not establish the scale.

## Processed numbered signals

Files use numeric names such as `000.txt`, `01.txt`, or `62.txt`. They contain whitespace-separated numeric values, preferably without a header for compatibility across processing stages.

| Column | Meaning |
| --- | --- |
| 1 | Sample index or time-like coordinate produced by preprocessing |
| 2 | Stress |
| 3 | Strain |
| 4, when present | Strain rate |

Do not assume column 1 is elapsed seconds: supplied processed files may contain sample indices. The TA splitting stage initially writes index/stress/strain; later processing can add strain rate. Workflows requiring strain rate need the appropriate processed input. Keep units consistent with the instrument and selected analysis, and avoid blank or nonnumeric rows in signal files.

## Fourier-coefficient files

Matching files live in `fourier_coefficients/` and retain the parent signal's numeric filename. The Fourier-generation routine writes rows for increasing harmonic order with three values: amplitude, real component, and negative imaginary component under its FFT convention. Released example coefficient files are comma-delimited so they can be loaded by the harmonic plotting workflow. Some original legacy exports used whitespace delimiters; those files were normalized for the release package with numeric values unchanged. Preserve the generated layout rather than editing signs or column order manually.

The first row corresponds to the first harmonic. These stress coefficient values are not automatically interchangeable with strain-normalized storage/loss moduli. Normalization and sign/phase conventions must follow the selected method.

## Other accompanying files

`rebuild/`, `SPP Data/`, `ST.txt`, and `stress_bifurcation.txt` contain existing reconstruction or analysis outputs where supplied. `file_titles.txt` stores plotting labels. `.laos_preprocessed.json`, where present, is an application preprocessing marker. Keep the sample's associated files together when exploring the processed examples.

## Example selection

The release includes four HAAKE sample folders and two TA sample folders. See the [dataset guide](../examples/README.md) and its file-level SHA-256 manifest. Instrument-native RWD/RWR files, Origin projects, and separate model-fitting/normalized-result folders are not required for these example workflows and are not included.
