import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from ..converter.mzml_parser import MzMLParser
from ..converter.raw_converter import RawConverter
from .peak_analyzer import PeakAnalyzer
from .mass_calculator import MassCalculator
from ..models.analysis_result import AnalysisResult, PeakInfo
import logging
from ..visualization.plate_heatmap import PlateHeatmap
from .pda_processor import PDAProcessor
from matplotlib.figure import Figure
from ..utils.memory_monitor import MemoryMonitor
import gc

class DataProcessor:
    """
    Processes MS data and combines information from different channels
    """
    
    def __init__(self):
        self.logger = logging.getLogger('DataProcessor')
        self.converter = RawConverter()
        self.peak_analyzer = PeakAnalyzer()
        self.pda_processor = PDAProcessor()
        self.mass_calculator = MassCalculator()
        self.memory_monitor = MemoryMonitor()
        
    def get_multi_channel_data(self, result: AnalysisResult) -> Dict:
        """Get data for multi-channel visualization"""
        try:
            return {
                'pda_data': {
                    'time': result.pda_time,
                    'intensity': result.pda_intensity
                },
                'ms_pos_tic': {
                    'time': result.ms_time,
                    'intensity': result.ms_pos_tic
                },
                'ms_pos_spectrum': {
                    'mz': result.ms_pos_mz,
                    'intensity': result.ms_pos_intensity
                },
                'ms_neg_tic': {
                    'time': result.ms_time,
                    'intensity': result.ms_neg_tic
                },
                'ms_neg_spectrum': {
                    'mz': result.ms_neg_mz,
                    'intensity': result.ms_neg_intensity
                },
                'uv_spectrum': {
                    'wavelength': result.uv_wavelength,
                    'absorbance': result.uv_absorbance
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting multi-channel data: {str(e)}")
            raise 

    def process_sample(self, raw_file: Path, sample_id: str, smiles: str) -> Dict:
        """Process sample data"""
        try:
            self.memory_monitor.log_memory_usage('Before processing')

            # Read data using memory-optimized mode
            raw_data = self.converter.read_raw_file(
                raw_file,
                memory_efficient=True
            )

            self.memory_monitor.log_memory_usage('After reading raw file')

            # 2. Calculate mass-related parameters
            mass_results = self.mass_calculator.calculate_masses(smiles)
            
            # 3. 检测产物和计算纯度
            product_detected, detected_mass, retention_time = self.peak_analyzer.detect_product(
                raw_data['ms_data'],
                target_mass=mass_results['mh_mass'],
                tolerance=0.5
            )
            
            purity = self.peak_analyzer.calculate_purity(
                raw_data['pda_data'],
                time_range=(0.2, 2.5)
            )
            
            result = AnalysisResult(
                sample_id=sample_id,
                smiles=smiles,
                formula=mass_results['formula'],
                monoisotopic_mass=mass_results['monoisotopic_mass'],
                mh_mass=mass_results['mh_mass'],
                mna_mass=mass_results['mna_mass'],
                mh_minus_mass=mass_results['mh_minus_mass'],
                product_detected=product_detected,
                retention_time=retention_time,
                detected_mass=detected_mass,
                purity=purity,
                # ... other data
            )
            
            # 清理不需要的数据
            gc.collect()
            self.memory_monitor.log_memory_usage('After processing')
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing sample: {str(e)}")
            raise 

    def export_results(self, results: List[AnalysisResult], output_path: Path, format: str = 'csv'):
        """Export analysis results"""
        try:
            data = []
            for result in results:
                data.append({
                    'Sample ID': result.sample_id,
                    'Formula': result.formula,
                    'Monoisotopic Mass': result.monoisotopic_mass,
                    'M+H Mass': result.mh_mass,
                    'M+Na Mass': result.mna_mass,
                    'M-H Mass': result.mh_minus_mass,
                    'Product Detected': result.product_detected,
                    'Retention Time': result.retention_time,
                    'Mass Detected': result.detected_mass,
                    'Purity': result.purity,
                    'Peak1 RT': result.peak1_rt,
                    'Peak1 Mass': result.peak1_mass,
                    'Peak2 RT': result.peak2_rt,
                    'Peak2 Mass': result.peak2_mass,
                    'Peak3 RT': result.peak3_rt,
                    'Peak3 Mass': result.peak3_mass
                })
            
            df = pd.DataFrame(data)
            
            if format == 'csv':
                df.to_csv(output_path, index=False)
            elif format == 'excel':
                df.to_excel(output_path, index=False)
            elif format == 'json':
                df.to_json(output_path, orient='records')
                
        except Exception as e:
            self.logger.error(f"Error exporting results: {str(e)}")
            raise 