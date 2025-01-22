import pytest
import pandas as pd
import numpy as np
from src.analysis.peak_analyzer import PeakAnalyzer
from src.models.analysis_result import PeakInfo

class TestPeakAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return PeakAnalyzer()
        
    @pytest.fixture
    def sample_peaks(self):
        return pd.DataFrame({
            'retention_time': [0.5, 1.2, 1.8, 2.3],
            'mass': [410.1828, 432.1647, 408.1677, 411.0],
            'intensity': [1000000, 500000, 250000, 100000],
            'area': [2000000, 1000000, 500000, 200000],
            'width': [0.1, 0.15, 0.12, 0.08]
        })
        
    def test_detect_product(self, analyzer, sample_peaks):
        # 测试成功检测
        detected, mass, rt = analyzer.detect_product(
            sample_peaks, 
            target_mass=410.18,
            tolerance=0.5
        )
        assert detected
        assert pytest.approx(mass, abs=0.001) == 410.1828
        assert pytest.approx(rt, abs=0.001) == 0.5
        
        # 测试未检测到
        detected, mass, rt = analyzer.detect_product(
            sample_peaks,
            target_mass=415.0,
            tolerance=0.1
        )
        assert not detected
        assert mass is None
        assert rt is None
        
    def test_calculate_purity(self, analyzer, sample_peaks):
        purity = analyzer.calculate_purity(sample_peaks)
        assert 0 <= purity <= 100
        
        # 测试时间窗口内的纯度计算
        window_peaks = sample_peaks[
            (sample_peaks['retention_time'] >= 0.2) &
            (sample_peaks['retention_time'] <= 2.5)
        ]
        expected_purity = (window_peaks['area'].max() / window_peaks['area'].sum()) * 100
        assert pytest.approx(purity, abs=0.001) == expected_purity
        
    def test_get_major_peaks(self, analyzer, sample_peaks):
        peaks = analyzer.get_major_peaks(sample_peaks, top_n=2)
        assert len(peaks) == 2
        assert all(isinstance(peak, PeakInfo) for peak in peaks)
        assert peaks[0].intensity > peaks[1].intensity
        assert pytest.approx(peaks[0].mass, abs=0.001) == 410.1828 
        
    def test_find_major_peaks(self, analyzer):
        # Create sample PDA data with three peaks
        time_points = 600  # 10 minutes
        pda_data = np.zeros(time_points)
        
        # Add three Gaussian peaks
        peak_times = [120, 240, 360]  # 2, 4, and 6 minutes
        peak_heights = [1.0, 0.7, 0.4]
        
        for time, height in zip(peak_times, peak_heights):
            pda_data += height * np.exp(-(np.arange(time_points) - time)**2 / 100)
        
        # Create matching MS data
        ms_data = pd.DataFrame({
            'retention_time': [2.0, 4.0, 6.0],
            'mass': [410.1828, 432.1647, 408.1677],
            'intensity': [1000000, 700000, 400000]
        })
        
        # Get major peaks
        peaks = analyzer.get_major_peaks(pda_data, ms_data)
        
        # Verify results
        assert len(peaks) == 3
        assert all(isinstance(peak, PeakInfo) for peak in peaks)
        
        # Check peak order (by area)
        assert peaks[0].intensity > peaks[1].intensity > peaks[2].intensity
        
        # Check retention times
        assert pytest.approx(peaks[0].retention_time, abs=0.1) == 2.0
        assert pytest.approx(peaks[1].retention_time, abs=0.1) == 4.0
        assert pytest.approx(peaks[2].retention_time, abs=0.1) == 6.0
        
        # Check masses
        assert pytest.approx(peaks[0].mass, abs=0.001) == 410.1828
        assert pytest.approx(peaks[1].mass, abs=0.001) == 432.1647
        assert pytest.approx(peaks[2].mass, abs=0.001) == 408.1677 