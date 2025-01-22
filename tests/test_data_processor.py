import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.data_processor import DataProcessor
from src.models.analysis_result import AnalysisResult, PeakInfo, MassInfo

class TestDataProcessor:
    @pytest.fixture
    def processor(self):
        return DataProcessor()
    
    @pytest.fixture
    def sample_peaks_data(self):
        return pd.DataFrame({
            'retention_time': [1.2, 1.8, 2.3],
            'mass': [410.1828, 432.1647, 408.1677],
            'intensity': [1000000, 500000, 250000],
            'area': [2000000, 1000000, 500000],
            'width': [0.1, 0.15, 0.12]
        })
    
    def test_process_sample(self, processor, tmp_path):
        # 创建模拟的raw文件
        raw_file = tmp_path / "test.raw"
        raw_file.touch()
        
        sample_id = "TEST001"
        smiles = "NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O"
        
        result = processor.process_sample(
            raw_file=raw_file,
            sample_id=sample_id,
            smiles=smiles
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.sample_id == sample_id
        assert result.smiles == smiles
        assert isinstance(result.mass_info, MassInfo)
        assert isinstance(result.major_peaks, list)
        
    def test_calculate_purity(self, processor, sample_peaks_data):
        purity = processor.calculate_purity(sample_peaks_data)
        assert 0 <= purity <= 100
        
    def test_get_major_peaks(self, processor, sample_peaks_data):
        major_peaks = processor.get_major_peaks(sample_peaks_data)
        assert len(major_peaks) <= 3
        assert all(isinstance(peak, PeakInfo) for peak in major_peaks)
        assert major_peaks[0].intensity >= major_peaks[1].intensity 