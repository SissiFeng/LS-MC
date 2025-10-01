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

## Waters Data Conversion Tool

### Current Development Approach:

#### 1. File Format Conversion (raw → mzML)
- Use ProteoWizard's MSConvert to convert .raw files to .mzML format
- Conversion can be executed directly via command line or embedded in Python subprocess
- Data parsing and information extraction

#### 2. Data Processing
- Use pymzML to read mzML files and extract scan spectra, peak data, and other information
- Organize extracted data into pandas DataFrame for convenient downstream processing
- Data analysis and visualization

#### 3. Parameter Extraction and Analysis
- Extract required experimental parameters (peaks, intensity, retention time)
- Analyze correspondence between mass spectra and other channels (UV/Vis)
- Generate visualization charts such as heatmaps and spectra
- Generate laboratory-required outputs

#### 4. Output Generation
- Provide peak tables, heatmaps, and multi-channel correspondence relationships
- Output formats include CSV, Excel, or JSON to meet laboratory analysis and archival needs

### Software Workflow:
**User Interface:** Users upload .raw files/folders through the UI interface

**Backend Processing:**
- Software calls MSConvert to convert .raw files to .mzML files
- Uses pymzML to read .mzML files and extract scan spectra, peak data, and other information
- Organizes extracted data into pandas DataFrame for convenient processing
- Extracts required experimental parameters (peaks, intensity, retention time)
- Analyzes correspondence between mass spectra and other channels (UV/Vis)
- Generates visualization charts such as heatmaps and spectra
- Generates laboratory-required outputs including peak tables, heatmaps, and multi-channel relationships

**Final Output:** User interface displays a list/table containing various parameters needed by users, with export capabilities to CSV, Excel, or JSON formats for laboratory analysis and archival requirements.

## Requirements (January 13th Update):

### Input Parameters:
- Sample unique identifier (text)
- Structure (SMILES)
- Raw data file (Waters .raw)

### Output Parameters:

#### A. Mass-Related Calculations (Must be calculated):
- Molecular Formula (calculated from SMILES)
- Monoisotopic mass (calculated from molecular formula)
- M+H mass (monoisotopic mass + 1.0078)
- M+Na mass (monoisotopic mass + 22.9897)
- M-H mass (monoisotopic mass - 1.0073)

#### B. Chromatographic Data Analysis:
- Processed chromatogram (.mzML/.csv/.rpt format)
- Product detected? (Yes/No, based on m/z matching with 0.5Da tolerance)
- Retention time (peak retention time in minutes)
- Mass detected (matched mass)
- Purity (peak integration between 0.2-2.5 minutes)

#### C. Major Peak Information (for top three largest peaks):
- Peak 1/2/3 - RT (retention time)
- Mass - Peak 1/2/3 (strongest ion mass for each peak)

### Additional Feature Requirements:
- Generate sample matrix/plate format heatmaps
- Display structure alongside heatmap
- Support definition and subtraction of blank PDA spectra
- Add support for .rpt format
- Optimize PDA data integration calculation methods

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
│   │   └── "AC P1 E3.raw"    # Test file
│   ├── mzml/
│   └── output/
├── requirements.txt
├── setup.py
└── README.md