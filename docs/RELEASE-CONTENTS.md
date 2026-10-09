# v1.0 packaging details

The Windows ZIP contains `LAOS_Analysis.exe` and its required `_internal` runtime. Only existing `.log` diagnostic files are omitted from the runtime. Runtime bytecode, DLLs, Qt plugins, fonts, resources, and third-party license notices are retained.

The selected `Test Data` folders retain raw TXT/Excel inputs, numeric TXT files, Fourier-coefficient folders, existing reconstruction/SPP outputs, ST/stress-bifurcation tables, and relevant preprocessing markers. Original sample folder and data file names are preserved. Instrument-native RWD/RWR files, Origin projects, a separate KDR/model-fitting subtree, duplicate normalized-result folders, and incidental images are omitted.
For direct compatibility with the packaged harmonic plotting reader, legacy whitespace-delimited Fourier coefficient examples were normalized to comma-delimited text while preserving all numeric values.
For direct compatibility with the packaged harmonic plotting reader, legacy whitespace-delimited Fourier coefficient examples were normalized to comma-delimited text while preserving all numeric values.

The two PDF manuals and ten MP4 tutorials are unchanged in content; download file names are normalized. A SHA-256 file accompanies the assets. The Windows ZIP includes the examples and both manuals; examples and manuals are also offered separately.

This release packages the supplied executable; it does not claim a fresh numerical benchmark or compatibility test on every Windows system. The repository contains distribution documentation, rather than a newly selected development-source tree.
