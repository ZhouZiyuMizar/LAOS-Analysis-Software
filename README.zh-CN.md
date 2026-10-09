# LAOS Analysis Software

[English](README.md) · [下载 v1.0](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.0) · [中文说明书](docs/User-Manual-ZH.pdf) · [英文说明书](docs/User-Manual-EN.pdf)

LAOS Analysis 是面向大振幅振荡剪切（LAOS）实验的 Windows 桌面分析软件，集成数据预处理、傅里叶流变学、切比雪夫分析、应力分岔、物理过程序列（SPP）、Lissajous 曲线、耗散比和笼模量计算与可视化。

## 下载与运行

1. 下载 [Windows 完整软件包](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Windows-x64.zip)。
2. 完整解压到可写的本地文件夹。
3. 打开 `LAOS-Analysis-V1.0` 文件夹，运行 `LAOS_Analysis.exe`，保留同级 `_internal` 文件夹。
4. 按照 `docs` 中的说明书，使用 `Test Data` 中的示例数据开始分析。

软件包自带 Python 运行环境和依赖，无需另外安装 Python。GitHub 自动生成的 **Source code** 压缩包仅包含本仓库文档，不包含完整 Windows 软件，请下载上述完整软件包。

## 示例与教程

- [示例数据说明](examples/README.md)及[独立示例数据包](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/LAOS-Analysis-V1.0-Examples.zip)：包含 4 组 HAAKE 和 2 组 TA 数据，保留原始输入及配套编号数据、傅里叶系数等文件。
- [中文 PDF 使用说明书](docs/User-Manual-ZH.pdf)。
- [英文 PDF 使用说明书](docs/User-Manual-EN.pdf)。
- [10 个功能演示视频](videos/README.md)。
- [文件校验值](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.0/SHA256SUMS.txt)。

## 版本说明

当前发布版本为 **v1.0**，GitHub 标签为 `v1.0`。

本仓库提供软件分发、文档和示例入口。详见[版本记录](CHANGELOG.md)与[打包说明](docs/RELEASE-CONTENTS.md)。

## 引用与反馈

英文说明书署名作者为 Ziyu Zhou、Hongbin Zhang。引用格式见 [CITATION.cff](CITATION.cff)，此版本不填写尚未确认的论文 DOI。问题反馈请使用 [Issues](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/issues)。版权说明见 [COPYRIGHT.md](COPYRIGHT.md)。

## 详细文档（英文）

- [安装与故障排查](docs/INSTALLATION.md)
- [入门教程](docs/GETTING-STARTED.md)
- [数据格式](docs/DATA-FORMATS.md)
- [依赖关系](docs/DEPENDENCIES.md)
- [完整英文概述、特点、项目结构和作者](README.md)
