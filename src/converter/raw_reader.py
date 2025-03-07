from typing import Dict, Optional, List, Generator
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from pymsfilereader import MSFileReader
from dataclasses import dataclass
import gc

@dataclass
class RawScanInfo:
    scan_number: int
    retention_time: float
    ms_level: int
    polarity: str
    tic: float
    base_peak_intensity: float
    base_peak_mz: float

class RawFileReader:
    """直接读取Waters .raw文件的解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger('RawFileReader')
        self.chunk_size = 1000  # 每次处理的扫描数
        
    def read_raw_file(self, raw_file: Path, memory_efficient: bool = True) -> Dict:
        """
        直接读取.raw文件，使用分块处理减少内存占用
        
        Args:
            raw_file: .raw文件路径
            memory_efficient: 是否使用内存优化模式
        """
        try:
            reader = MSFileReader(str(raw_file))
            num_scans = reader.GetNumSpectra()
            
            if memory_efficient:
                return self._read_by_chunks(reader, num_scans)
            else:
                return self._read_all_at_once(reader, num_scans)
                
    def _read_by_chunks(self, reader: MSFileReader, num_scans: int) -> Dict:
        """分块读取数据"""
        ms_data_chunks = []
        pda_data_chunks = []
        
        for chunk_start in range(0, num_scans, self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, num_scans)
            
            # 处理当前块
            chunk_data = self._process_scan_chunk(reader, chunk_start + 1, chunk_end + 1)
            
            ms_data_chunks.extend(chunk_data['ms_data'])
            if chunk_data['pda_data']:
                pda_data_chunks.extend(chunk_data['pda_data'])
                
            # 强制垃圾回收
            gc.collect()
            
        # 合并所有块的数据
        ms_df = pd.DataFrame(ms_data_chunks)
        
        if pda_data_chunks:
            pda_array = np.vstack([d['intensities'] for d in pda_data_chunks])
            wavelengths = pda_data_chunks[0]['wavelengths']
            pda_times = np.array([d['retention_time'] for d in pda_data_chunks])
        else:
            pda_array = np.array([])
            wavelengths = np.array([])
            pda_times = np.array([])
            
        return {
            'ms_data': ms_df,
            'chromatogram': ms_df[['scan_number', 'retention_time', 'tic', 'base_peak_intensity']],
            'pda_data': pda_array,
            'wavelengths': wavelengths,
            'pda_times': pda_times
        }
            
    def _get_scan_info(self, reader: MSFileReader, scan_num: int) -> RawScanInfo:
        """获取扫描信息"""
        try:
            header = reader.GetScanHeaderInfoForScanNum(scan_num)
            return RawScanInfo(
                scan_number=scan_num,
                retention_time=header.RetentionTime,
                ms_level=header.MSOrder,
                polarity=header.Polarity,
                tic=header.TIC,
                base_peak_intensity=header.BasePeakIntensity,
                base_peak_mz=header.BasePeakMass
            )
        except Exception as e:
            self.logger.error(f"Error getting scan info for scan {scan_num}: {str(e)}")
            raise
            
    def _get_spectrum(self, reader: MSFileReader, scan_num: int) -> Dict:
        """获取质谱数据"""
        try:
            mz_array, intensity_array = reader.GetMassListFromScanNum(scan_num)
            return {
                'mz': np.array(mz_array),
                'intensity': np.array(intensity_array)
            }
        except Exception as e:
            self.logger.error(f"Error getting spectrum for scan {scan_num}: {str(e)}")
            raise
            
    def _get_pda_spectrum(self, reader: MSFileReader, scan_num: int) -> Optional[Dict]:
        """获取PDA光谱数据"""
        try:
            if hasattr(reader, 'GetPDASpectrum'):
                wavelengths, intensities = reader.GetPDASpectrum(scan_num)
                return {
                    'wavelengths': np.array(wavelengths),
                    'intensities': np.array(intensities)
                }
            return None
        except Exception as e:
            self.logger.error(f"Error getting PDA spectrum for scan {scan_num}: {str(e)}")
            return None 