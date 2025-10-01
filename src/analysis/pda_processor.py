from typing import Dict, Optional, Tuple, List
import numpy as np
import pandas as pd
from pathlib import Path
import logging

class PDAProcessor:
    """PDA spectral data processing module"""

    def __init__(self):
        self.logger = logging.getLogger('PDAProcessor')
        self.wavelength_range = (200, 400)  # Default wavelength range (nm)
        self._blank_spectrum = None

    def process_pda_data(self,
                        pda_data: np.ndarray,
                        wavelengths: np.ndarray,
                        retention_time: float,
                        rt_window: float = 0.1
                        ) -> Dict[str, np.ndarray]:
        """
        Process PDA spectral data

        Args:
            pda_data: PDA spectral data matrix (time x wavelength)
            wavelengths: Wavelength array
            retention_time: Target retention time
            rt_window: Retention time window (minutes)

        Returns:
            Dict: Processed spectral data
        """
        try:
            # 1. Extract spectrum at target time window
            target_spectrum = self._extract_spectrum_at_rt(
                pda_data,
                retention_time,
                rt_window
            )

            # 2. Subtract blank spectrum (if available)
            if self._blank_spectrum is not None:
                target_spectrum = self._subtract_blank(target_spectrum)

            # 3. Baseline correction
            corrected_spectrum = self._baseline_correction(target_spectrum)

            # 4. Spectrum smoothing
            smoothed_spectrum = self._smooth_spectrum(corrected_spectrum)
            
            return {
                'wavelengths': wavelengths,
                'raw_spectrum': target_spectrum,
                'processed_spectrum': smoothed_spectrum,
                'max_wavelength': wavelengths[np.argmax(smoothed_spectrum)]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDA data: {str(e)}")
            raise
            
    def set_blank_spectrum(self, blank_data: np.ndarray):
        """Set blank spectrum for baseline correction"""
        self._blank_spectrum = blank_data
        self.logger.info("Blank spectrum set for baseline correction")
        
    def _extract_spectrum_at_rt(self,
                              pda_data: np.ndarray,
                              retention_time: float,
                              rt_window: float
                              ) -> np.ndarray:
        """Extract spectrum at specified retention time"""
        # Assuming pda_data time axis is already aligned
        rt_index = int(retention_time * 60)  # Convert to data point index
        window = int(rt_window * 60)

        start_idx = max(0, rt_index - window)
        end_idx = min(pda_data.shape[0], rt_index + window)

        # Return average spectrum within time window
        return np.mean(pda_data[start_idx:end_idx], axis=0)
        
    def _subtract_blank(self, spectrum: np.ndarray) -> np.ndarray:
        """Subtract blank spectrum from data"""
        if self._blank_spectrum is None:
            return spectrum
        return spectrum - self._blank_spectrum
        
    def _baseline_correction(self, spectrum: np.ndarray) -> np.ndarray:
        """Baseline correction"""
        # Use simple minimum subtraction for baseline correction
        baseline = np.percentile(spectrum, 5)  # Use 5th percentile as baseline
        return np.maximum(spectrum - baseline, 0)

    def _smooth_spectrum(self,
                        spectrum: np.ndarray,
                        window_size: int = 5
                        ) -> np.ndarray:
        """Spectrum smoothing processing"""
        # Use simple moving average for smoothing
        kernel = np.ones(window_size) / window_size
        return np.convolve(spectrum, kernel, mode='same')
        
    def calculate_peak_area(self,
                          pda_data: np.ndarray,
                          time_array: np.ndarray,
                          rt_range: Tuple[float, float] = (0.2, 2.5),
                          baseline_correction: bool = True
                          ) -> Dict[str, float]:
        """
        Calculate PDA peak area

        Args:
            pda_data: PDA data matrix (time x wavelength)
            time_array: Time array (minutes)
            rt_range: Integration time range (min, max)
            baseline_correction: Whether to perform baseline correction

        Returns:
            Dict: Contains total area and individual peak area information
        """
        try:
            # 1. Extract data within time window
            mask = (time_array >= rt_range[0]) & (time_array <= rt_range[1])
            window_data = pda_data[mask]
            window_time = time_array[mask]

            # 2. Calculate total absorption curve (sum of all wavelengths)
            total_absorption = np.sum(window_data, axis=1)

            # 3. Baseline correction
            if baseline_correction:
                total_absorption = self._correct_baseline(total_absorption)

            # 4. Calculate area using trapezoidal rule
            total_area = np.trapz(total_absorption, window_time)

            # 5. Find and integrate individual peaks
            peaks_info = self._integrate_individual_peaks(
                total_absorption,
                window_time
            )
            
            return {
                'total_area': total_area,
                'peaks': peaks_info
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating peak area: {str(e)}")
            raise
            
    def _correct_baseline(self, signal: np.ndarray) -> np.ndarray:
        """
        Improved baseline correction method
        Use iterative polynomial fitting for baseline correction
        """
        try:
            # 1. Initial estimation of baseline points
            window_size = len(signal) // 20  # 5% window size
            baseline_points = []
            for i in range(0, len(signal), window_size):
                segment = signal[i:i + window_size]
                baseline_points.append(np.percentile(segment, 5))

            # 2. Polynomial fitting
            x = np.linspace(0, len(signal)-1, len(baseline_points))
            x_full = np.arange(len(signal))
            coeffs = np.polyfit(x, baseline_points, deg=3)
            baseline = np.polyval(coeffs, x_full)

            # 3. Ensure baseline does not exceed signal
            baseline = np.minimum(baseline, signal)

            # 4. Subtract baseline and ensure non-negative
            return np.maximum(signal - baseline, 0)
            
        except Exception as e:
            self.logger.error(f"Error in baseline correction: {str(e)}")
            raise
            
    def _integrate_individual_peaks(self,
                                 signal: np.ndarray,
                                 time_array: np.ndarray,
                                 min_peak_height: float = 0.1,
                                 min_peak_width: float = 0.05  # minutes
                                 ) -> List[Dict]:
        """
        Identify and integrate individual peaks
        """
        try:
            from scipy.signal import find_peaks, peak_widths

            # 1. Find peaks
            peaks, properties = find_peaks(
                signal,
                height=min_peak_height * np.max(signal),
                distance=int(min_peak_width / (time_array[1] - time_array[0]))
            )

            # 2. Calculate peak widths
            widths, width_heights, left_ips, right_ips = peak_widths(
                signal, peaks, rel_height=0.5
            )

            # 3. Integrate each peak
            peak_results = []
            for i, peak_idx in enumerate(peaks):
                left_idx = int(left_ips[i])
                right_idx = int(right_ips[i])

                # Calculate peak area
                peak_area = np.trapz(
                    signal[left_idx:right_idx],
                    time_array[left_idx:right_idx]
                )

                peak_results.append({
                    'retention_time': time_array[peak_idx],
                    'area': peak_area,
                    'height': signal[peak_idx],
                    'width': widths[i] * (time_array[1] - time_array[0]),  # Convert to minutes
                    'left_rt': time_array[left_idx],
                    'right_rt': time_array[right_idx]
                })

            # Sort by area
            peak_results.sort(key=lambda x: x['area'], reverse=True)
            return peak_results
            
        except Exception as e:
            self.logger.error(f"Error integrating peaks: {str(e)}")
            raise 