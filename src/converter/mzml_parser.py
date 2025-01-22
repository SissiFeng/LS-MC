from pathlib import Path
import pymzml
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

class MzMLParser:
    """mzML 文件解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger('MzMLParser')
        
    def parse_mzml(self, mzml_file: Path) -> Dict:
        """解析 mzML 文件，提取所需数据"""
        try:
            run = pymzml.run.Reader(str(mzml_file))
            
            # 存储不同类型的数据
            chromatograms = []  # TIC和BPC
            ms1_spectra = []    # MS1谱图
            pda_data = []       # PDA数据
            wavelengths = None  # PDA波长
            
            for spec in run:
                if spec.ms_level == 1:
                    # 处理MS1谱图
                    ms1_spectra.append({
                        'retention_time': spec.scan_time_in_minutes(),
                        'mz_array': spec.mz,
                        'intensity_array': spec.i,
                        'total_ion_current': spec.TIC,
                        'base_peak_intensity': max(spec.i) if len(spec.i) > 0 else 0
                    })
                    
                    # 添加色谱图数据点
                    chromatograms.append({
                        'retention_time': spec.scan_time_in_minutes(),
                        'tic_intensity': spec.TIC,
                        'base_peak_intensity': max(spec.i) if len(spec.i) > 0 else 0
                    })
                    
                elif hasattr(spec, 'wavelength'):  # PDA数据
                    if wavelengths is None:
                        wavelengths = spec.wavelength
                    pda_data.append({
                        'retention_time': spec.scan_time_in_minutes(),
                        'intensities': spec.i
                    })
            
            # 转换为DataFrame和numpy数组
            chromatogram_df = pd.DataFrame(chromatograms)
            ms1_df = pd.DataFrame(ms1_spectra)
            
            # 处理PDA数据
            if pda_data:
                pda_array = np.array([d['intensities'] for d in pda_data])
                pda_times = np.array([d['retention_time'] for d in pda_data])
            else:
                pda_array = np.array([])
                wavelengths = np.array([])
            
            return {
                'chromatogram': chromatogram_df,
                'ms1_spectra': ms1_df,
                'pda_data': pda_array,
                'wavelengths': wavelengths,
                'pda_times': pda_times if pda_data else np.array([])
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing mzML file: {str(e)}")
            raise 