import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy.signal import correlate
from scipy.stats import pearsonr
import logging

class ChannelAnalyzer:
    """
    Analyzes relationships between different channels (MS and UV/Vis)
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ChannelAnalyzer')
        
    def align_channels(self,
                      ms_data: pd.DataFrame,
                      uv_data: pd.DataFrame,
                      rt_tolerance: float = 0.1  # retention time tolerance in minutes
                      ) -> pd.DataFrame:
        """
        Align MS and UV/Vis data based on retention time
        
        Args:
            ms_data: DataFrame with MS channel data (must have 'retention_time' column)
            uv_data: DataFrame with UV/Vis channel data (must have 'retention_time' column)
            rt_tolerance: Retention time tolerance for matching peaks
            
        Returns:
            DataFrame with aligned channel data
        """
        aligned_data = []
        
        for ms_idx, ms_row in ms_data.iterrows():
            ms_rt = ms_row['retention_time']
            
            # Find matching UV/Vis data points within tolerance
            matching_uv = uv_data[
                (uv_data['retention_time'] >= ms_rt - rt_tolerance) &
                (uv_data['retention_time'] <= ms_rt + rt_tolerance)
            ]
            
            if not matching_uv.empty:
                # Get closest UV/Vis point
                closest_uv = matching_uv.iloc[
                    (matching_uv['retention_time'] - ms_rt).abs().argmin()
                ]
                
                # Combine MS and UV data
                combined = {
                    'retention_time': ms_rt,
                    'ms_intensity': ms_row['intensity'],
                    'uv_intensity': closest_uv['intensity'],
                    'rt_difference': abs(ms_rt - closest_uv['retention_time'])
                }
                aligned_data.append(combined)
        
        return pd.DataFrame(aligned_data)
    
    def analyze_peak_correlation(self,
                               aligned_data: pd.DataFrame,
                               window_size: int = 5
                               ) -> Dict[str, pd.DataFrame]:
        """
        Analyze correlation between MS and UV/Vis peaks
        
        Args:
            aligned_data: DataFrame with aligned channel data
            window_size: Size of the moving window for local correlation
            
        Returns:
            Dictionary containing correlation analysis results
        """
        # Calculate global correlation
        global_corr, p_value = pearsonr(
            aligned_data['ms_intensity'],
            aligned_data['uv_intensity']
        )
        
        # Calculate moving window correlation
        window_corrs = []
        for i in range(len(aligned_data) - window_size + 1):
            window = aligned_data.iloc[i:i + window_size]
            corr, _ = pearsonr(window['ms_intensity'], window['uv_intensity'])
            window_corrs.append({
                'retention_time': window['retention_time'].mean(),
                'correlation': corr
            })
        
        # Identify corresponding peaks
        peak_pairs = self._find_corresponding_peaks(aligned_data)
        
        return {
            'global_correlation': pd.DataFrame({
                'correlation': [global_corr],
                'p_value': [p_value]
            }),
            'local_correlation': pd.DataFrame(window_corrs),
            'peak_pairs': pd.DataFrame(peak_pairs)
        }
    
    def _find_corresponding_peaks(self,
                                aligned_data: pd.DataFrame,
                                intensity_threshold: float = 0.5
                                ) -> List[Dict]:
        """
        Find corresponding peaks between MS and UV/Vis channels
        
        Args:
            aligned_data: DataFrame with aligned channel data
            intensity_threshold: Relative intensity threshold for peak detection
            
        Returns:
            List of dictionaries containing corresponding peak information
        """
        # Normalize intensities
        ms_norm = aligned_data['ms_intensity'] / aligned_data['ms_intensity'].max()
        uv_norm = aligned_data['uv_intensity'] / aligned_data['uv_intensity'].max()
        
        peak_pairs = []
        
        # Find points where both channels show high intensity
        high_intensity_points = (ms_norm > intensity_threshold) & (uv_norm > intensity_threshold)
        
        for rt, ms_int, uv_int in zip(
            aligned_data.loc[high_intensity_points, 'retention_time'],
            aligned_data.loc[high_intensity_points, 'ms_intensity'],
            aligned_data.loc[high_intensity_points, 'uv_intensity']
        ):
            peak_pairs.append({
                'retention_time': rt,
                'ms_intensity': ms_int,
                'uv_intensity': uv_int,
                'ms_normalized': ms_int / aligned_data['ms_intensity'].max(),
                'uv_normalized': uv_int / aligned_data['uv_intensity'].max()
            })
        
        return peak_pairs
    
    def export_channel_analysis(self,
                              analysis_results: Dict[str, pd.DataFrame],
                              output_dir: Path,
                              base_name: str
                              ) -> Dict[str, Path]:
        """
        Export channel analysis results
        
        Args:
            analysis_results: Dictionary containing analysis results
            output_dir: Directory for output files
            base_name: Base name for output files
            
        Returns:
            Dictionary mapping result type to output file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_files = {}
        
        for result_type, df in analysis_results.items():
            file_path = output_dir / f"{base_name}_channel_{result_type}.csv"
            df.to_csv(file_path, index=False)
            output_files[result_type] = file_path
            
        return output_files 