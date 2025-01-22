from typing import Dict, Optional, Tuple, List
import numpy as np
import pandas as pd
from pathlib import Path
import logging

class PDAProcessor:
    """PDA光谱数据处理模块"""
    
    def __init__(self):
        self.logger = logging.getLogger('PDAProcessor')
        self.wavelength_range = (200, 400)  # 默认波长范围(nm)
        self._blank_spectrum = None
        
    def process_pda_data(self,
                        pda_data: np.ndarray,
                        wavelengths: np.ndarray,
                        retention_time: float,
                        rt_window: float = 0.1
                        ) -> Dict[str, np.ndarray]:
        """
        处理PDA光谱数据
        
        Args:
            pda_data: PDA光谱数据矩阵 (时间 x 波长)
            wavelengths: 波长数组
            retention_time: 目标保留时间
            rt_window: 保留时间窗口(分钟)
            
        Returns:
            Dict: 处理后的光谱数据
        """
        try:
            # 1. 提取目标时间窗口的光谱
            target_spectrum = self._extract_spectrum_at_rt(
                pda_data, 
                retention_time,
                rt_window
            )
            
            # 2. 减去空白光谱(如果有)
            if self._blank_spectrum is not None:
                target_spectrum = self._subtract_blank(target_spectrum)
            
            # 3. 基线校正
            corrected_spectrum = self._baseline_correction(target_spectrum)
            
            # 4. 光谱平滑
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
        """提取指定保留时间的光谱"""
        # 这里假设pda_data的时间轴已经对齐
        rt_index = int(retention_time * 60)  # 转换为数据点索引
        window = int(rt_window * 60)
        
        start_idx = max(0, rt_index - window)
        end_idx = min(pda_data.shape[0], rt_index + window)
        
        # 返回时间窗口内的平均光谱
        return np.mean(pda_data[start_idx:end_idx], axis=0)
        
    def _subtract_blank(self, spectrum: np.ndarray) -> np.ndarray:
        """Subtract blank spectrum from data"""
        if self._blank_spectrum is None:
            return spectrum
        return spectrum - self._blank_spectrum
        
    def _baseline_correction(self, spectrum: np.ndarray) -> np.ndarray:
        """基线校正"""
        # 使用简单的最小值减法进行基线校正
        baseline = np.percentile(spectrum, 5)  # 使用5%分位数作为基线
        return np.maximum(spectrum - baseline, 0)
        
    def _smooth_spectrum(self, 
                        spectrum: np.ndarray,
                        window_size: int = 5
                        ) -> np.ndarray:
        """光谱平滑处理"""
        # 使用简单的移动平均进行平滑
        kernel = np.ones(window_size) / window_size
        return np.convolve(spectrum, kernel, mode='same') 
        
    def calculate_peak_area(self,
                          pda_data: np.ndarray,
                          time_array: np.ndarray,
                          rt_range: Tuple[float, float] = (0.2, 2.5),
                          baseline_correction: bool = True
                          ) -> Dict[str, float]:
        """
        计算PDA峰面积
        
        Args:
            pda_data: PDA数据矩阵 (时间 x 波长)
            time_array: 时间数组 (分钟)
            rt_range: 积分时间范围 (min, max)
            baseline_correction: 是否进行基线校正
            
        Returns:
            Dict: 包含总面积和各个峰的面积信息
        """
        try:
            # 1. 提取时间窗口内的数据
            mask = (time_array >= rt_range[0]) & (time_array <= rt_range[1])
            window_data = pda_data[mask]
            window_time = time_array[mask]
            
            # 2. 计算总吸收曲线 (所有波长的和)
            total_absorption = np.sum(window_data, axis=1)
            
            # 3. 基线校正
            if baseline_correction:
                total_absorption = self._correct_baseline(total_absorption)
            
            # 4. 使用梯形法则计算面积
            total_area = np.trapz(total_absorption, window_time)
            
            # 5. 查找并积分各个峰
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
        改进的基线校正方法
        使用迭代多项式拟合进行基线校正
        """
        try:
            # 1. 初始估计基线点
            window_size = len(signal) // 20  # 5%窗口大小
            baseline_points = []
            for i in range(0, len(signal), window_size):
                segment = signal[i:i + window_size]
                baseline_points.append(np.percentile(segment, 5))
            
            # 2. 多项式拟合
            x = np.linspace(0, len(signal)-1, len(baseline_points))
            x_full = np.arange(len(signal))
            coeffs = np.polyfit(x, baseline_points, deg=3)
            baseline = np.polyval(coeffs, x_full)
            
            # 3. 确保基线不会超过信号
            baseline = np.minimum(baseline, signal)
            
            # 4. 减去基线并确保非负
            return np.maximum(signal - baseline, 0)
            
        except Exception as e:
            self.logger.error(f"Error in baseline correction: {str(e)}")
            raise
            
    def _integrate_individual_peaks(self,
                                 signal: np.ndarray,
                                 time_array: np.ndarray,
                                 min_peak_height: float = 0.1,
                                 min_peak_width: float = 0.05  # 分钟
                                 ) -> List[Dict]:
        """
        识别并积分单个峰
        """
        try:
            from scipy.signal import find_peaks, peak_widths
            
            # 1. 查找峰
            peaks, properties = find_peaks(
                signal,
                height=min_peak_height * np.max(signal),
                distance=int(min_peak_width / (time_array[1] - time_array[0]))
            )
            
            # 2. 计算峰宽
            widths, width_heights, left_ips, right_ips = peak_widths(
                signal, peaks, rel_height=0.5
            )
            
            # 3. 积分每个峰
            peak_results = []
            for i, peak_idx in enumerate(peaks):
                left_idx = int(left_ips[i])
                right_idx = int(right_ips[i])
                
                # 计算峰面积
                peak_area = np.trapz(
                    signal[left_idx:right_idx],
                    time_array[left_idx:right_idx]
                )
                
                peak_results.append({
                    'retention_time': time_array[peak_idx],
                    'area': peak_area,
                    'height': signal[peak_idx],
                    'width': widths[i] * (time_array[1] - time_array[0]),  # 转换为分钟
                    'left_rt': time_array[left_idx],
                    'right_rt': time_array[right_idx]
                })
            
            # 按面积排序
            peak_results.sort(key=lambda x: x['area'], reverse=True)
            return peak_results
            
        except Exception as e:
            self.logger.error(f"Error integrating peaks: {str(e)}")
            raise 