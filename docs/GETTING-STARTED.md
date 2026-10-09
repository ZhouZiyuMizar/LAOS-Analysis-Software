# Getting started

## Tutorial 1 — Plot an included processed example

1. Extract the full application package and make a working copy of `Test Data/Test Data HAAKE/2%`.
2. Run `LAOS_Analysis.exe`. Use the folder-selection/import control to choose the copied `2%` sample folder.
3. Confirm that numbered files such as `000.txt` appear in the file list. The matching `fourier_coefficients` subfolder should remain inside this sample folder.
4. Select one test point. Choose the Lissajous plotting function and generate the plot.
5. Inspect the stress–strain representation; check the labels, units, and selected file. Change the plot style if needed and export the figure using the application's export controls.
6. Compare your operation with video 01 in the [video index](../videos/README.md). Videos 02–10 introduce overlays, dissipation, Fourier coefficients, S/T measures, stress bifurcation, SPP, and cage modulus.

The included numbered signals have already been processed. Keep an untouched copy so that subsequent processing does not replace your reference files. There is no universal expected curve shape across the six sample folders or their test points.

## Tutorial 2 — Preprocess a HAAKE raw export

1. Copy the original `2%.txt` from the HAAKE `2%` sample into a new working directory. This named raw export is different from the numbered `000.txt`–`059.txt` signals.
2. Select the new folder and choose the HAAKE preprocessing workflow.
3. Review the detected test points and choose the cycle selection/processing settings described in Chapter 3 of the English manual.
4. Set the actual experimental frequency and check the stress and strain units. Do not substitute a guessed frequency based on the sample label.
5. Perform the required preprocessing stages, including phase alignment and strain-rate/Fourier processing as appropriate to the selected analysis.
6. Inspect the generated numbered signals and matching coefficient files, then plot a selected test point.

## Tutorial 3 — Preprocess a TA workbook

1. Copy one original workbook, such as `1 (10) mosha.xls` from `Test Data TA/Sample 1`, into an otherwise empty working folder.
2. Choose the TA preprocessing workflow and scan the workbook sheets.
3. Check that the required `Sine Strain -<number>` sheets are found. The expected `Stress` and `Strain` headers are on the second Excel row.
4. Enter the acquisition frequency and select the desired cycles or available automatic cycle-selection option.
5. Complete the remaining preprocessing stages and inspect the generated numeric TXT files before plotting.

See [Data formats](DATA-FORMATS.md) for the exact layout and [the dataset guide](../examples/README.md) for all six samples.

## Choosing a method

- Use Lissajous curves to inspect the waveform geometry.
- Use Fourier and Chebyshev outputs to examine harmonic content and nonlinear elastic/viscous measures.
- Use stress bifurcation and dissipation outputs for their respective yielding and energy-based descriptions.
- Use SPP for intra-cycle trajectories; record whether the analytical/Fourier or numerical/gradient mode was selected. The modes use different differentiation routes and should not be assumed to produce identical results under every condition.
- Use circular decomposition to inspect rotating components of an SPP trajectory.

For a reproducible report, record the source file, instrument/export format, units, frequency, selected cycles, preprocessing choices, method, harmonic settings, and software version. Full method explanations and references are in the [English manual](User-Manual-EN.pdf).
