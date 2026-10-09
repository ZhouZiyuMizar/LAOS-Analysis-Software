# Example data / 示例数据

[Download examples ZIP](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Examples.zip). The same examples are included in the complete Windows ZIP under `Test Data`.

| Folder under Test Data | Raw input / accompanying workbook | Numbered data files |
| --- | --- | --- |
| `Test Data HAAKE/2%` | `2%.txt`; `2%.xlsx` | 60 |
| `Test Data HAAKE/20260508/1% CNF` | `1% CNF-1.txt` | 120 |
| `Test Data HAAKE/20260508/CNC` | `CNC.txt` | 120 |
| `Test Data HAAKE/20260508/XG` | `xg.txt` | 60 |
| `Test Data TA/Sample 1` | `1 (10) mosha.xls` | 63 |
| `Test Data TA/Sample 2` | `1 up mosha.xls` | 61 |

## Use the examples

1. Extract the examples and make a working copy before processing: the application may write results into the selected folder.
2. To explore existing processed signals, select one sample folder (such as `Test Data HAAKE/2%` or `Test Data TA/Sample 1`) that directly contains the numbered TXT files. Keep its `fourier_coefficients` folder next to them.
3. To repeat preprocessing, use a separate working folder containing the chosen original HAAKE TXT export or TA Excel workbook, then follow the instrument-specific instructions in the manual. Set frequency and processing parameters according to the acquisition settings; they are not inferred from a sample name.
4. Compare the supplied plotting workflows with the [video tutorials](../videos/README.md).

The numbered TXT files and accompanying coefficients are processed example files. Other included output tables are reference outputs, not newly recalculated results. The 2% HAAKE example also includes its accompanying summary workbook. Sample names are retained as supplied; no additional material identity or composition is inferred. Fourier coefficient examples in this release are comma-delimited for direct loading by the software; legacy whitespace-delimited examples were converted with numeric values unchanged. Fourier coefficient examples in this release are comma-delimited for direct loading by the software; legacy whitespace-delimited examples were converted with numeric values unchanged. Fourier coefficient examples in this release are comma-delimited for direct loading by the software; legacy whitespace-delimited examples were converted with numeric values unchanged.

中文：首次使用建议直接选择包含编号 TXT 文件的单个样品文件夹，保留同级傅里叶系数目录。重新预处理时，将原始 HAAKE TXT 或 TA Excel 复制到新的工作目录，再按说明书选择对应仪器流程并设置实际实验频率等参数。示例中的已有结果仅作为随附参考，不代表本次重新计算或验证。

See [data-manifest.csv](data-manifest.csv) for every included file and its SHA-256 checksum.
