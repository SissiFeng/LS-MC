import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Optional, Tuple
from matplotlib.figure import Figure

class HeatmapViewer:
    """Enhanced heatmap visualization with multiple display options"""
    
    def __init__(self):
        self.default_figsize = (12, 8)
        self.default_cmap = 'viridis'
        
    def create_analysis_figure(self,
                             data: Dict,
                             smiles: str = None,
                             structure_viewer = None) -> Figure:
        """Create comprehensive analysis figure with heatmap and structure"""
        fig = plt.figure(figsize=(15, 10))
        
        if smiles and structure_viewer:
            # Create 2x2 grid with structure in top right
            gs = plt.GridSpec(2, 2, figure=fig)
            heatmap_ax = fig.add_subplot(gs[:, 0])  # Left column
            structure_ax = fig.add_subplot(gs[0, 1])  # Top right
            intensity_ax = fig.add_subplot(gs[1, 1])  # Bottom right
            
            # Plot structure
            structure_viewer.plot_structure(smiles, structure_ax)
            structure_ax.set_title("Molecular Structure")
        else:
            # Use full width for heatmap
            heatmap_ax = fig.add_subplot(111)
            
        # Plot main heatmap
        self.plot_intensity_heatmap(
            data['rt_array'],
            data['mz_array'],
            data['intensity_matrix'],
            ax=heatmap_ax,
            title="RT vs m/z Intensity Heatmap"
        )
        
        if 'intensity_profile' in data:
            # Plot intensity profile
            self._plot_intensity_profile(
                data['rt_array'],
                data['intensity_profile'],
                ax=intensity_ax
            )
            
        plt.tight_layout()
        return fig
        
    def plot_intensity_heatmap(self,
                             rt_array: np.ndarray,
                             mz_array: np.ndarray,
                             intensity_matrix: np.ndarray,
                             ax: Optional[plt.Axes] = None,
                             title: str = None,
                             log_scale: bool = True,
                             show_colorbar: bool = True) -> plt.Axes:
        """Plot enhanced RT vs m/z intensity heatmap"""
        if ax is None:
            _, ax = plt.subplots(figsize=self.default_figsize)
            
        # Apply log scale if requested
        if log_scale:
            intensity_matrix = np.log1p(intensity_matrix)
            
        # Create heatmap with improved visualization
        heatmap = sns.heatmap(
            intensity_matrix,
            xticklabels=np.round(rt_array, 2),
            yticklabels=np.round(mz_array, 2),
            ax=ax,
            cmap=self.default_cmap,
            cbar=show_colorbar,
            robust=True
        )
        
        # Customize appearance
        ax.set_xlabel('Retention Time (min)')
        ax.set_ylabel('m/z')
        if title:
            ax.set_title(title)
            
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        return ax
        
    def _plot_intensity_profile(self,
                              rt_array: np.ndarray,
                              intensity_profile: np.ndarray,
                              ax: plt.Axes) -> None:
        """Plot total ion intensity profile"""
        ax.plot(rt_array, intensity_profile, 'b-')
        ax.set_xlabel('Retention Time (min)')
        ax.set_ylabel('Total Ion Intensity')
        ax.set_title('Intensity Profile') 