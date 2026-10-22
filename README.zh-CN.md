# LAOS Analysis Software

**v1.01，Windows x64 桌面软件，用于 LAOS 非线性流变数据分析**

[English README](README.md) | [下载 Windows 软件](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.01) | [查看源码](src/) | [示例数据](examples/Test%20Data/) | [中文说明书](docs/User-Manual-ZH.pdf)

## 概述

LAOS Analysis Software 是用于大振幅振荡剪切实验数据处理和分析的桌面软件。它把原始数据预处理、非线性黏弹性分析和图形导出放在一个本地工作流程中，适合软物质和复杂流体研究。

软件支持 Fourier 流变分析、Chebyshev 分析、应力分岔、物理过程序列分析、Lissajous 曲线、耗散比和笼模量等功能。

## 功能特点

| 模块 | 主要功能 |
| --- | --- |
| 数据预处理 | HAAKE 和 TA 数据流程、数据分段、周期选择、去噪、相位校正和 Fourier 分析 |
| 波形可视化 | Lissajous 曲线、归一化图和多测试点叠加 |
| 谐波分析 | 单阶和多阶 Fourier 系数，Chebyshev 的 S 值和 T 值 |
| 屈服与耗散 | 应力分岔、耗散比和笼模量 |
| 周期内分析 | SPP 图、解析和数值计算模式、圆分解 |
| 输出 | 交互式图形、样式调整、图片导出和多语言界面 |

## 下载和使用

常见使用方式分为三种。

| 需求 | 推荐方式 |
| --- | --- |
| 直接运行软件 | 从 [v1.01 Release](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.01) 下载 `LAOS-Analysis-V1.01-Windows-x64.zip`。这个包包含 `LAOS_Analysis.exe`、运行库、说明书和示例数据。 |
| 查看或修改源码 | 直接浏览 [`src/`](src/)，克隆仓库，或使用 GitHub 页面上的绿色 **Code** 按钮下载仓库。 |
| 使用示例数据 | 直接浏览 [`examples/Test Data/`](examples/Test%20Data/)，克隆仓库，或从 Release 页面下载单独的示例数据包。 |

GitHub 自动生成的 **Source code** 压缩包包含本仓库中的源码和示例数据，但不包含完整 Windows 运行库。想直接运行软件，请下载 Release 页面中的 Windows 软件包。

## 安装

普通 Windows 用户建议使用打包版本：

1. 下载 [LAOS-Analysis-V1.01-Windows-x64.zip](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.01/LAOS-Analysis-V1.01-Windows-x64.zip)。
2. 将整个 ZIP 解压到可写的本地文件夹。
3. 打开解压后的 `LAOS-Analysis-V1.01` 文件夹。
4. 运行 `LAOS_Analysis.exe`。
5. 保持 `_internal` 文件夹和可执行文件在同一目录下。

Windows 包已经包含 Python 和运行依赖，不需要另外安装 Python。

如果要从源码运行，请安装 Python 3.8 或兼容的 Python 3 版本，然后安装依赖：

```bash
pip install -r requirements.txt
python src/main.py
```

源码主要用于查看、复现和二次开发。面向普通用户的稳定入口仍然是 Release 页面中的 Windows 软件包。

## 入门

1. 启动打包后的软件。
2. 从 `examples/Test Data/` 或 Windows 软件包里的 `Test Data` 中复制一个示例文件夹。
3. 选择一个直接包含编号 TXT 文件的样品文件夹，例如 `Test Data HAAKE/2%`。
4. 选择一个测试点。
5. 生成 Lissajous 图，检查坐标轴、单位和图形样式，然后导出图片。
6. 参考 [视频教程](videos/README.md) 学习 Fourier 系数、耗散比、应力分岔、SPP 图和笼模量分析。

仓库中的编号 TXT 文件是已经处理过的示例数据。如果要从原始实验数据开始，请复制 HAAKE TXT 或 TA Excel 文件到新的工作目录，然后按说明书操作。

## 数据格式

| 输入类型 | 要求 |
| --- | --- |
| HAAKE 原始导出 | 包含 `Datapoint no.:` 标记和导出信号列的 TXT 数据块 |
| TA 原始导出 | 工作目录中放一个 `.xls` 或 `.xlsx` 文件，工作表名形如 `Sine Strain -<number>` |
| 已处理信号 | 形如 `000.txt` 或 `01.txt` 的编号文件 |
| Fourier 系数 | 放在 `fourier_coefficients/` 中，与编号信号文件对应 |

更多细节见 [docs/DATA-FORMATS.md](docs/DATA-FORMATS.md)。数据布局和单位很重要，普通 CSV 或任意 Excel 表格不能直接等同于支持格式。

## 项目结构

```text
LAOS-Analysis-Software/
  src/                    源代码和程序资源
  examples/
    Test Data/            HAAKE 和 TA 示例数据
    data-manifest.csv     文件清单和 SHA-256 校验值
  docs/                   说明书和技术文档
  videos/                 示例视频下载入口
  README.md               英文说明
  README.zh-CN.md         中文说明
  requirements.txt        源码运行依赖
  CITATION.cff            引用信息
  LICENSE                 CC BY 4.0 许可说明
```

完整 Windows 可执行软件没有直接放在 Git 仓库里，而是放在 GitHub Releases 中。这样更适合发布包含运行库的大文件。

## 许可和引用

本仓库使用 Creative Commons Attribution 4.0 International License，见 [LICENSE](LICENSE)。

如果你在论文、报告或其他学术工作中使用本软件、源码、文档或示例数据，请引用 **LAOS Analysis Software, v1.01**。引用格式见 [CITATION.cff](CITATION.cff)，也可以使用 GitHub 的 **Cite this repository** 功能。

## 作者和单位

- Ziyu Zhou，[GitHub: ZhouZiyuMizar](https://github.com/ZhouZiyuMizar)
- Hongbin Zhang

Advanced Rheology Institute, Shanghai Jiao Tong University.

## 反馈

问题反馈请使用 [GitHub Issues](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/issues)。建议同时提供软件版本、Windows 环境、所用分析方法和参数、报错信息，以及可复现的小型输入文件。
