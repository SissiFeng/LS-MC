from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import logging

class DataValidator:
    """Validate data integrity and validity"""

    def __init__(self):
        self.logger = logging.getLogger('DataValidator')

    def validate_peaks(self, peaks_df: pd.DataFrame) -> Dict[str, bool]:
        """Validate peak data validity"""
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
        """Validate if mzML file is readable"""
        try:
            from pymzml import run
            run.Reader(str(mzml_path))
            return True
        except Exception as e:
            self.logger.error(f"Invalid mzML file: {str(e)}")
            return False 