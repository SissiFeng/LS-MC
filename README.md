# Waters Data Processing Tool

A comprehensive tool for processing Waters LC-MS data files.

## Features

- Direct Waters .raw file processing
- Automated molecular analysis
- Peak detection and purity analysis
- Advanced visualization tools
- Flexible workflow integration

## Installation

1. Install Python 3.8 or higher
2. Install ProteoWizard MSConvert
3. Install Waters Raw File Reader
4. Install the package:

Waters 数据转换工具：
目前暂定的开发思路：
1. 文件格式转换（raw → mzML）

使用 ProteoWizard 的 MSConvert 将 .raw 文件转换为 .mzML。
转换可以直接通过命令行调用 MSConvert，也可以嵌入 Python 的子进程（subprocess）中执行。
数据解析与信息提取

2. 使用 pymzML 读取 mzML 文件，从中提取扫描谱图、峰值数据等信息。
将提取的数据组织为 pandas DataFrame，方便后续处理。
数据分析与可视化

3. 提取需要的实验参数（如峰值、强度、保留时间）。
4. 分析质谱与其他通道（如 UV/Vis）的对应关系。
5. 生成可视化图表，如热图、谱图等。
6. 生成实验室所需的输出

7. 提供峰值表格、热图，以及多通道对应关系。
8. 输出格式可以是 CSV、Excel 或 JSON，满足实验室的分析和存档需求。

这个软件：
用户通过ui界面从本地上传 .raw 文件/文件夹，
软件后台：
软件调用 MSConvert 将 .raw 文件转换为 .mzML 文件，并使用 pymzML 读取 .mzML 文件，从中提取扫描谱图、峰值数据等信息。
软件将提取的数据组织为 pandas DataFrame，方便后续处理。
软件提取需要的实验参数（如峰值、强度、保留时间）。
软件分析质谱与其他通道（如 UV/Vis）的对应关系。
软件生成可视化图表，如热图、谱图等。
软件生成实验室所需的输出，提供峰值表格、热图，以及多通道对应关系。
最终用户界面就是能看到一个list/table，其中有用户需要的各种参数。并且可以输出 CSV、Excel 或 JSON，满足实验室的分析和存档需求。

0113 新需求：
输入参数:
Sample unique identifier (text)
Structure (SMILES)
Raw data file (Waters .raw)
输出参数:
A. 质量相关计算 (Must be calculated):
Molecular Formula (从SMILES计算)
Monoisotopic mass (从分子式计算)
M+H mass (monoisotopic mass + 1.0078)
M+Na mass (monoisotopic mass + 22.9897)
M-H mass (monoisotopic mass - 1.0073)
B. 色谱数据分析:
Processed chromatogram (.mzML/.csv/.rpt格式)
Product detected? (Yes/No，基于m/z匹配，容差0.5Da)
Retention time (峰的保留时间，分钟)
Mass detected (匹配到的质量)
Purity (0.2-2.5min之间峰的积分)
C. 主要峰的信息 (对前三个最大峰):
Peak 1/2/3 - RT (保留时间)
Mass - Peak 1/2/3 (每个峰的最强离子质量)
其他功能需求:
生成样品矩阵/板式格式的热图
在热图旁显示结构
支持定义和减去空白PDA光谱

添加对 .rpt 格式的支持
优化 PDA 数据的积分计算方法

SMILES for the expected product is NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O. 

LS-MS/
├── src/
│   ├── __init__.py
│   ├── converter/
│   │   ├── __init__.py
│   │   ├── raw_converter.py
│   │   └── mzml_parser.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── peak_detector.py
│   │   ├── data_processor.py
│   │   └── channel_analyzer.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plot_spectrum.py
│   │   └── plot_heatmap.py
│   └── ui/
│       ├── __init__.py
│       ├── main.py
│       ├── qml/
│       │   ├── main.qml
│       │   ├── components/
│       │   │   ├── FileUploader.qml
│       │   │   ├── DataTable.qml
│       │   │   └── ChartView.qml
│       │   └── style/
│       │       ├── Colors.qml
│       │       └── Typography.qml
│       └── resources.qrc
├── tests/
├── data/
│   ├── raw/
│   │   └── "AC P1 E3.raw"    # 测试文件
│   ├── mzml/
│   └── output/
├── requirements.txt
├── setup.py
└── README.md