import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_widths
from typing import Dict, List, Tuple, Optional
import logging

class PeakDetector:
    """
    Handles peak detection and analysis for MS data
    """
    
    def __init__(self):
        self.logger = logging.getLogger('PeakDetector')
        
    def detect_peaks(self, 
                    intensity: np.ndarray,
                    rt: np.ndarray,
                    height: Optional[float] = None,
                    distance: Optional[int] = None,
                    prominence: Optional[float] = None,
                    width: Optional[float] = None
                    ) -> pd.DataFrame:
        """
        Detect peaks in chromatogram data
        
        Args:
            intensity: Intensity array
            rt: Retention time array
            height: Required height of peaks
            distance: Required minimal horizontal distance in samples between peaks
            prominence: Required prominence of peaks
            width: Required width of peaks in points
            
        Returns:
            DataFrame containing peak information
        """
        # Find peaks using scipy
        peaks, properties = find_peaks(
            intensity,
            height=height,
            distance=distance,
            prominence=prominence,
            width=width
        )
        
        # Calculate peak widths at different heights
        widths, width_heights, left_ips, right_ips = peak_widths(
            intensity, peaks, rel_height=0.5
        )
        
        # Create peak data
        peak_data = {
            'retention_time': rt[peaks],
            'intensity': intensity[peaks],
            'prominence': properties['prominences'],
            'width': widths,
            'width_start': rt[left_ips.astype(int)],
            'width_end': rt[right_ips.astype(int)],
            'area': self._calculate_peak_areas(intensity, peaks, left_ips.astype(int), right_ips.astype(int))
        }
        
        return pd.DataFrame(peak_data)
    
    def _calculate_peak_areas(self, 
                            intensity: np.ndarray, 
                            peaks: np.ndarray,
                            left_bounds: np.ndarray,
                            right_bounds: np.ndarray
                            ) -> np.ndarray:
        """Calculate areas under peaks using trapezoidal integration"""
        areas = []
        for peak, left, right in zip(peaks, left_bounds, right_bounds):
            area = np.trapz(intensity[left:right])
            areas.append(area)
        return np.array(areas) 