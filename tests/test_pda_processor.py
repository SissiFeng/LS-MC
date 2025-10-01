import pytest
import numpy as np
from src.analysis.pda_processor import PDAProcessor

class TestPDAProcessor:
    @pytest.fixture
    def processor(self):
        return PDAProcessor()
        
    @pytest.fixture
    def sample_pda_data(self):
        # Create mock PDA data (time points x wavelengths)
        time_points = 300  # 5 minutes, one point per second
        wavelengths = 200  # 200-400nm

        # Generate mock data
        data = np.random.normal(0.1, 0.02, (time_points, wavelengths))
        # Add a Gaussian peak
        peak_time = 150  # Peak at 2.5 minutes
        peak_wavelength = 100  # Absorption at 300nm
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
            retention_time=2.5  # Peak position
        )
        
        assert 'wavelengths' in results
        assert 'raw_spectrum' in results
        assert 'processed_spectrum' in results
        assert 'max_wavelength' in results
        
        # Check if maximum absorption wavelength is within expected range
        assert 290 <= results['max_wavelength'] <= 310
        
    def test_blank_subtraction(self, processor, sample_pda_data, wavelengths):
        # Set blank spectrum
        blank = np.ones_like(sample_pda_data[0]) * 0.1
        processor.set_blank_spectrum(blank)
        
        results = processor.process_pda_data(
            sample_pda_data,
            wavelengths,
            retention_time=2.5
        )
        
        # Check if processed spectrum is smaller than original spectrum
        assert np.all(results['processed_spectrum'] <= results['raw_spectrum'])
        
    def test_baseline_correction(self, processor):
        # Test baseline correction
        test_spectrum = np.array([0.1, 0.2, 0.15, 0.5, 0.3, 0.1])
        corrected = processor._baseline_correction(test_spectrum)
        assert np.all(corrected >= 0)
        assert np.min(corrected) < 0.01  # Baseline should be close to 0

    def test_smooth_spectrum(self, processor):
        # Test spectrum smoothing
        noisy_spectrum = np.array([0.1, 0.3, 0.15, 0.5, 0.2, 0.4])
        smoothed = processor._smooth_spectrum(noisy_spectrum, window_size=3)
        
        # Check if smoothed spectrum is smoother than original spectrum
        original_variation = np.std(np.diff(noisy_spectrum))
        smoothed_variation = np.std(np.diff(smoothed))
        assert smoothed_variation < original_variation 