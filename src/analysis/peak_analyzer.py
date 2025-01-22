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
    """峰检测和分析模块"""
    
    def __init__(self):
        self.logger = logging.getLogger('PeakAnalyzer')
        
    def detect_product(self,
                      peaks_data: pd.DataFrame,
                      target_mass: float,
                      tolerance: float = 0.5
                      ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        检测目标产物峰
        
        Args:
            peaks_data: 包含峰信息的DataFrame
            target_mass: 目标质量
            tolerance: 质量匹配容差 (Da)
            
        Returns:
            Tuple[bool, Optional[float], Optional[float]]:
                - 是否检测到产物
                - 检测到的质量 (如果检测到)
                - 保留时间 (如果检测到)
        """
        try:
            # 在质量容差范围内查找匹配的峰
            mass_matches = peaks_data[
                (peaks_data['mass'] >= target_mass - tolerance) &
                (peaks_data['mass'] <= target_mass + tolerance)
            ]
            
            if mass_matches.empty:
                return False, None, None
                
            # 选择强度最高的峰
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
        计算纯度 (指定时间窗口内主峰面积占比)
        
        Args:
            chromatogram: 色谱图数据
            time_range: 时间窗口 (min, max)
            
        Returns:
            float: 纯度百分比 (0-100)
        """
        try:
            # 提取时间窗口内的数据
            window_data = chromatogram[
                (chromatogram['retention_time'] >= time_range[0]) &
                (chromatogram['retention_time'] <= time_range[1])
            ]
            
            if window_data.empty:
                return 0.0
                
            # 计算主峰面积占比
            total_area = window_data['area'].sum()
            if total_area == 0:
                return 0.0
                
            main_peak_area = window_data['area'].max()
            purity = (main_peak_area / total_area) * 100
            
            return min(purity, 100.0)  # 确保不超过100%
            
        except Exception as e:
            self.logger.error(f"Error calculating purity: {str(e)}")
            raise
            
    def get_major_peaks(self,
                       chromatogram: pd.DataFrame,
                       max_peaks: int = 3
                       ) -> List[PeakInfo]:
        """
        获取主要峰的信息 (按强度排序)
        
        Args:
            chromatogram: 色谱图数据
            max_peaks: 返回的最大峰数量
            
        Returns:
            List[PeakInfo]: 主要峰的信息列表
        """
        try:
            # 按强度排序并获取前N个峰
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
        在光谱/色谱图中查找峰
        
        Args:
            time: 时间数组
            intensity: 强度数组
            height_threshold: 峰高阈值（相对最大强度）
            distance: 峰之间的最小距离（数据点）
            
        Returns:
            pd.DataFrame: 包含峰信息的DataFrame
        """
        try:
            # 归一化强度
            normalized_intensity = intensity / np.max(intensity)
            
            # 查找峰
            peaks, properties = find_peaks(
                normalized_intensity,
                height=height_threshold,
                distance=distance
            )
            
            # 计算峰宽
            widths, width_heights, left_ips, right_ips = peak_widths(
                normalized_intensity, peaks, rel_height=0.5
            )
            
            # 计算峰面积（使用梯形积分）
            areas = []
            for i, peak in enumerate(peaks):
                left_idx = int(left_ips[i])
                right_idx = int(right_ips[i])
                peak_area = np.trapz(
                    intensity[left_idx:right_idx],
                    time[left_idx:right_idx]
                )
                areas.append(peak_area)
            
            # 创建结果DataFrame
            return pd.DataFrame({
                'retention_time': time[peaks],
                'intensity': intensity[peaks],
                'area': areas,
                'width': widths * (time[1] - time[0])  # 转换为时间单位
            })
            
        except Exception as e:
            self.logger.error(f"Error finding peaks: {str(e)}")
            raise 