from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

class ChromatogramViewer:
    """Multi-channel chromatogram and spectrum viewer"""
    
    def __init__(self):
        self.logger = logging.getLogger('ChromatogramViewer')
        
    def plot_multi_channel(self, data: Dict) -> Figure:
        """
        Plot multi-channel data in a single figure
        
        Args:
            data: Dictionary containing:
                - pda_data: PDA chromatogram
                - ms_pos_tic: Positive MS TIC
                - ms_pos_spectrum: Positive MS spectrum
                - ms_neg_tic: Negative MS TIC
                - ms_neg_spectrum: Negative MS spectrum
                - uv_spectrum: UV spectrum
        """
        # Create figure with GridSpec
        fig = plt.figure(figsize=(12, 10))
        gs = GridSpec(6, 1, figure=fig, height_ratios=[1, 1, 1, 1, 1, 1])
        
        # 1. PDA Chromatogram
        ax1 = fig.add_subplot(gs[0])
        self._plot_pda_chromatogram(ax1, data['pda_data'])
        
        # 2. MS ES+ TIC
        ax2 = fig.add_subplot(gs[1])
        self._plot_ms_tic(ax2, data['ms_pos_tic'], polarity='positive')
        
        # 3. MS ES+ Spectrum
        ax3 = fig.add_subplot(gs[2])
        self._plot_ms_spectrum(ax3, data['ms_pos_spectrum'])
        
        # 4. MS ES- TIC
        ax4 = fig.add_subplot(gs[3])
        self._plot_ms_tic(ax4, data['ms_neg_tic'], polarity='negative')
        
        # 5. MS ES- Spectrum
        ax5 = fig.add_subplot(gs[4])
        self._plot_ms_spectrum(ax5, data['ms_neg_spectrum'])
        
        # 6. UV Spectrum
        ax6 = fig.add_subplot(gs[5])
        self._plot_uv_spectrum(ax6, data['uv_spectrum'])
        
        plt.tight_layout()
        return fig
        
    def _plot_pda_chromatogram(self, ax, data):
        """Plot PDA chromatogram"""
        ax.plot(data['time'], data['intensity'])
        ax.set_xlabel('Retention Time (min)')
        ax.set_ylabel('AU')
        ax.set_title('PDA - Total Absorbance Chromatogram')
        
    def _plot_ms_tic(self, ax, data, polarity):
        """Plot MS TIC"""
        ax.plot(data['time'], data['intensity'])
        ax.set_xlabel('Retention Time (min)')
        ax.set_ylabel('Intensity')
        ax.set_title(f'MS ES{"+") if polarity == "positive" else "-"} TIC')
        
    def _plot_ms_spectrum(self, ax, data):
        """Plot mass spectrum"""
        ax.vlines(data['mz'], 0, data['intensity'])
        ax.set_xlabel('m/z')
        ax.set_ylabel('Intensity')
        
    def _plot_uv_spectrum(self, ax, data):
        """Plot UV spectrum"""
        ax.plot(data['wavelength'], data['absorbance'])
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Absorbance') 