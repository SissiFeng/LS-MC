from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import logging

class DataValidator:
    """验证数据的完整性和有效性"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataValidator')
        
    def validate_peaks(self, peaks_df: pd.DataFrame) -> Dict[str, bool]:
        """验证峰数据的有效性"""
        checks = {
            'has_data': len(peaks_df) > 0,
            'has_required_columns': all(col in peaks_df.columns for col in [
                'retention_time', 'intensity', 'area', 'width'
            ]),
            'valid_values': (
                peaks_df['retention_time'].notna().all() and
                peaks_df['intensity'].notna().all() and
                (peaks_df['intensity'] >= 0).all()
            )
        }
        return checks

    def validate_mzml_file(self, mzml_path: Path) -> bool:
        """验证mzML文件是否可读"""
        try:
            from pymzml import run
            run.Reader(str(mzml_path))
            return True
        except Exception as e:
            self.logger.error(f"Invalid mzML file: {str(e)}")
            return False 