# LAOS Analysis Software

**v1.01，Windows x64 桌面软件，用于 LAOS 非线性流变数据分析**

[English README](README.md) | [v1.01 发布页](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.01) | [查看源代码](src/) | [查看示例数据](examples/Test%20Data/) | [中文说明书](docs/User-Manual-ZH.pdf)

## 软件概述

LAOS Analysis Software 用于大振幅振荡剪切实验的数据预处理、非线性黏弹性分析和图形导出，适合聚合物溶液、悬浮液、凝胶和食品材料等软物质体系。

主要功能包括傅里叶流变学、切比雪夫分析、应力分岔、物理过程序列（SPP）、Lissajous 曲线、耗散比和笼模量计算。

## 下载与安装

Windows 软件包较大，v1.01 Release 将其分为 12 个分卷。请下载全部分卷以及 `JOIN-Windows-Package.cmd`，放在同一个文件夹中，然后运行 CMD 文件合并完整 ZIP，再解压运行。

1. 打开 [v1.01 发布页](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/tag/v1.01)。
2. 下载 `LAOS-Analysis-V1.01-Windows-x64.zip.001` 至 `.012` 和 `JOIN-Windows-Package.cmd`。
3. 运行 `JOIN-Windows-Package.cmd`，生成 `LAOS-Analysis-V1.01-Windows-x64.zip`。
4. 完整解压 ZIP，打开 `LAOS-Analysis-V1.01` 文件夹，运行 `LAOS_Analysis.exe`。
5. 保留与可执行文件同级的 `_internal` 文件夹。

软件包已包含 Python 运行环境和依赖，不需要另外安装 Python。GitHub 自动生成的 Source code 压缩包包含源代码和仓库示例数据，但不包含 Windows 运行环境。

## 示例数据与说明书

- 仓库中的 [`examples/Test Data/`](examples/Test%20Data/) 可直接浏览或克隆。
- Release 中的 `LAOS-Analysis-V1.01-Examples.zip` 是 v1.01 软件包对应的原始 HAAKE 和 TA 示例数据。
- [中文使用说明书](docs/User-Manual-ZH.pdf)
- [英文使用说明书](docs/User-Manual-EN.pdf)
- [示例视频目录](videos/README.md)
- [SHA-256 校验文件](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/releases/download/v1.01/SHA256SUMS.txt)

## 从源代码运行

```bash
pip install -r requirements.txt
python src/main.py
```

## 版本与引用

当前公开版本为 **v1.01**。如果在论文、报告或其他学术工作中使用本软件、源代码、文档或示例数据，请按照 [CITATION.cff](CITATION.cff) 引用 **LAOS Analysis Software, v1.01**。

软件和仓库采用 CC BY 4.0，具体说明见 [LICENSE](LICENSE)。

## 作者与单位

- Ziyu Zhou
- Hongbin Zhang

Advanced Rheology Institute, Shanghai Jiao Tong University.

问题反馈请提交到 [GitHub Issues](https://github.com/ZhouZiyuMizar/LAOS-Analysis-Software/issues)。
