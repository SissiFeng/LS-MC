import pytest
import numpy as np
from src.analysis.pda_processor import PDAProcessor

class TestPDAProcessor:
    @pytest.fixture
    def processor(self):
        return PDAProcessor()
        
    @pytest.fixture
    def sample_pda_data(self):
        # 创建模拟的PDA数据 (时间点 x 波长)
        time_points = 300  # 5分钟，每秒一个点
        wavelengths = 200  # 200-400nm
        
        # 生成模拟数据
        data = np.random.normal(0.1, 0.02, (time_points, wavelengths))
        # 添加一个高斯峰
        peak_time = 150  # 2.5分钟处的峰
        peak_wavelength = 100  # 300nm处的吸收
        for t in range(time_points):
            for w in range(wavelengths):
                data[t, w] += 0.5 * np.exp(-(t - peak_time)**2/100) * \
                             np.exp(-(w - peak_wavelength)**2/50)
        
        return data
        
    @pytest.fixture
    def wavelengths(self):
        return np.linspace(200, 400, 200)
        
    def test_process_pda_data(self, processor, sample_pda_data, wavelengths):
        results = processor.process_pda_data(
            sample_pda_data,
            wavelengths,
            retention_time=2.5  # 峰的位置
        )
        
        assert 'wavelengths' in results
        assert 'raw_spectrum' in results
        assert 'processed_spectrum' in results
        assert 'max_wavelength' in results
        
        # 检查最大吸收波长是否在预期范围内
        assert 290 <= results['max_wavelength'] <= 310
        
    def test_blank_subtraction(self, processor, sample_pda_data, wavelengths):
        # 设置空白光谱
        blank = np.ones_like(sample_pda_data[0]) * 0.1
        processor.set_blank_spectrum(blank)
        
        results = processor.process_pda_data(
            sample_pda_data,
            wavelengths,
            retention_time=2.5
        )
        
        # 检查处理后的光谱是否小于原始光谱
        assert np.all(results['processed_spectrum'] <= results['raw_spectrum'])
        
    def test_baseline_correction(self, processor):
        # 测试基线校正
        test_spectrum = np.array([0.1, 0.2, 0.15, 0.5, 0.3, 0.1])
        corrected = processor._baseline_correction(test_spectrum)
        assert np.all(corrected >= 0)
        assert np.min(corrected) < 0.01  # 基线应该接近0
        
    def test_smooth_spectrum(self, processor):
        # 测试光谱平滑
        noisy_spectrum = np.array([0.1, 0.3, 0.15, 0.5, 0.2, 0.4])
        smoothed = processor._smooth_spectrum(noisy_spectrum, window_size=3)
        
        # 检查平滑后的光谱是否比原始光谱更平滑
        original_variation = np.std(np.diff(noisy_spectrum))
        smoothed_variation = np.std(np.diff(smoothed))
        assert smoothed_variation < original_variation 