# v1.0 Packaging Details

The Windows ZIP contains `LAOS_Analysis.exe` and its required `_internal`
runtime. The package also includes the selected example data and both PDF
manuals.

The repository contains the cleaned source code in `src/`, the example data in
`examples/Test Data/`, documentation, citation metadata, and the CC BY 4.0
license notice.

The selected `Test Data` folders retain raw TXT and Excel inputs, numbered TXT
files, Fourier-coefficient folders, existing reconstruction and SPP outputs,
ST/stress-bifurcation tables, and relevant preprocessing markers.

Instrument-native RWD/RWR files, Origin projects, a separate KDR/model-fitting
subtree, duplicate normalized-result folders, incidental images, cache files,
logs, and temporary backup files are omitted from the repository source/data
tree.

For direct compatibility with the packaged harmonic plotting reader, legacy
whitespace-delimited Fourier coefficient examples were normalized to
comma-delimited text while preserving all numeric values.

The ten MP4 tutorials are provided as release assets and linked from
[`videos/README.md`](../videos/README.md). A SHA-256 file accompanies the
release assets.
