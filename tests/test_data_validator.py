import pytest
import pandas as pd
from pathlib import Path
from src.analysis.data_validator import DataValidator

class TestDataValidator:
    @pytest.fixture
    def validator(self):
        return DataValidator()
    
    @pytest.fixture
    def valid_peaks_df(self):
        return pd.DataFrame({
            'retention_time': [1.2, 1.8, 2.3],
            'intensity': [1000000, 500000, 250000],
            'area': [2000000, 1000000, 500000],
            'width': [0.1, 0.15, 0.12]
        })
    
    def test_validate_peaks_valid_data(self, validator, valid_peaks_df):
        checks = validator.validate_peaks(valid_peaks_df)
        assert all(checks.values())
        
    def test_validate_peaks_missing_columns(self, validator):
        invalid_df = pd.DataFrame({
            'retention_time': [1.2],
            'intensity': [1000000]
        })
        checks = validator.validate_peaks(invalid_df)
        assert not checks['has_required_columns']
        
    def test_validate_peaks_negative_intensity(self, validator, valid_peaks_df):
        valid_peaks_df.loc[0, 'intensity'] = -1000
        checks = validator.validate_peaks(valid_peaks_df)
        assert not checks['valid_values']
        
    def test_validate_mzml_file(self, validator, tmp_path):
        # 创建一个无效的mzML文件
        invalid_file = tmp_path / "invalid.mzML"
        invalid_file.write_text("invalid content")
        assert not validator.validate_mzml_file(invalid_file) 