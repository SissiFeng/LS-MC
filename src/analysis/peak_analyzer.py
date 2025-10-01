from typing import List, Tuple, Optional, Dict
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_widths
import logging
from dataclasses import dataclass

@dataclass
class PeakInfo:
    retention_time: float
    mass: float
    intensity: float
    area: float
    width: float

class PeakAnalyzer:
    """Peak detection and analysis module"""
    
    def __init__(self):
        self.logger = logging.getLogger('PeakAnalyzer')
        
    def detect_product(self,
                      peaks_data: pd.DataFrame,
                      target_mass: float,
                      tolerance: float = 0.5
                      ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Detect target product peak

        Args:
            peaks_data: DataFrame containing peak information
            target_mass: Target mass
            tolerance: Mass matching tolerance (Da)

        Returns:
            Tuple[bool, Optional[float], Optional[float]]:
                - Whether product is detected
                - Detected mass (if detected)
                - Retention time (if detected)
        """
        try:
            # Find matching peaks within mass tolerance range
            mass_matches = peaks_data[
                (peaks_data['mass'] >= target_mass - tolerance) &
                (peaks_data['mass'] <= target_mass + tolerance)
            ]

            if mass_matches.empty:
                return False, None, None

            # Select the peak with highest intensity
            best_match = mass_matches.loc[mass_matches['intensity'].idxmax()]
            
            return True, best_match['mass'], best_match['retention_time']
            
        except Exception as e:
            self.logger.error(f"Error detecting product: {str(e)}")
            raise
            
    def calculate_purity(self,
                        chromatogram: pd.DataFrame,
                        time_range: Tuple[float, float] = (0.2, 2.5)
                        ) -> float:
        """
        Calculate purity (main peak area ratio within specified time window)

        Args:
            chromatogram: Chromatogram data
            time_range: Time window (min, max)

        Returns:
            float: Purity percentage (0-100)
        """
        try:
            # Extract data within time window
            window_data = chromatogram[
                (chromatogram['retention_time'] >= time_range[0]) &
                (chromatogram['retention_time'] <= time_range[1])
            ]

            if window_data.empty:
                return 0.0

            # Calculate main peak area ratio
            total_area = window_data['area'].sum()
            if total_area == 0:
                return 0.0

            main_peak_area = window_data['area'].max()
            purity = (main_peak_area / total_area) * 100

            return min(purity, 100.0)  # Ensure not exceeding 100%
            
        except Exception as e:
            self.logger.error(f"Error calculating purity: {str(e)}")
            raise
            
    def get_major_peaks(self,
                       chromatogram: pd.DataFrame,
                       max_peaks: int = 3
                       ) -> List[PeakInfo]:
        """
        Get information of major peaks (sorted by intensity)

        Args:
            chromatogram: Chromatogram data
            max_peaks: Maximum number of peaks to return

        Returns:
            List[PeakInfo]: List of major peak information
        """
        try:
            # Sort by intensity and get top N peaks
            top_peaks = chromatogram.nlargest(max_peaks, 'intensity')
            
            return [
                PeakInfo(
                    retention_time=row['retention_time'],
                    mass=row['mass'],
                    intensity=row['intensity'],
                    area=row['area'],
                    width=row['width']
                )
                for _, row in top_peaks.iterrows()
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting major peaks: {str(e)}")
            raise
            
    def find_peaks_in_spectrum(self,
                             time: np.ndarray,
                             intensity: np.ndarray,
                             height_threshold: float = 0.1,
                             distance: int = 10
                             ) -> pd.DataFrame:
        """
        Find peaks in spectrum/chromatogram

        Args:
            time: Time array
            intensity: Intensity array
            height_threshold: Peak height threshold (relative to maximum intensity)
            distance: Minimum distance between peaks (data points)

        Returns:
            pd.DataFrame: DataFrame containing peak information
        """
        try:
            # Normalize intensity
            normalized_intensity = intensity / np.max(intensity)

            # Find peaks
            peaks, properties = find_peaks(
                normalized_intensity,
                height=height_threshold,
                distance=distance
            )

            # Calculate peak widths
            widths, width_heights, left_ips, right_ips = peak_widths(
                normalized_intensity, peaks, rel_height=0.5
            )

            # Calculate peak areas (using trapezoidal integration)
            areas = []
            for i, peak in enumerate(peaks):
                left_idx = int(left_ips[i])
                right_idx = int(right_ips[i])
                peak_area = np.trapz(
                    intensity[left_idx:right_idx],
                    time[left_idx:right_idx]
                )
                areas.append(peak_area)

            # Create result DataFrame
            return pd.DataFrame({
                'retention_time': time[peaks],
                'intensity': intensity[peaks],
                'area': areas,
                'width': widths * (time[1] - time[0])  # Convert to time units
            })
            
        except Exception as e:
            self.logger.error(f"Error finding peaks: {str(e)}")
            raise 