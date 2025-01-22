from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from rdkit import Chem
from rdkit.Chem import Draw
import logging

class PlateHeatmap:
    """Plate heatmap visualization with structure display"""
    
    PLATE_ROWS = 8  # Standard 96-well plate rows (A-H)
    PLATE_COLS = 12  # Standard 96-well plate columns (1-12)
    STRUCTURE_SIZE = (300, 300)  # Size of structure images
    
    def __init__(self):
        self.logger = logging.getLogger('PlateHeatmap')
        self.data_types = {
            'purity': 'Sample Purity (%)',
            'yield': 'Product Yield (%)',
            'peak_area': 'Peak Area',
            'retention_time': 'Retention Time (min)'
        }
    
    def generate_heatmap(self, 
                        data: List[Dict], 
                        data_type: str = 'purity',
                        show_structures: bool = True,
                        title: Optional[str] = None) -> Figure:
        """
        Generate a plate heatmap with optional structure display
        
        Args:
            data: List of sample data dictionaries
            data_type: Type of data to display ('purity', 'yield', etc.)
            show_structures: Whether to show structure images
            title: Optional title for the plot
            
        Returns:
            matplotlib Figure object
        """
        # Create figure with appropriate size and layout
        fig = plt.figure(figsize=(15, 8))
        
        if show_structures:
            # Create two subplots: heatmap and structures
            gs = fig.add_gridspec(1, 2, width_ratios=[2, 1])
            ax_heat = fig.add_subplot(gs[0])
            ax_struct = fig.add_subplot(gs[1])
        else:
            ax_heat = fig.add_subplot(111)
            ax_struct = None
            
        # Prepare plate data
        plate_data = self._prepare_plate_data(data, data_type)
        
        # Generate heatmap
        im = ax_heat.imshow(plate_data, cmap='YlOrRd')
        
        # Add colorbar with label
        cbar = plt.colorbar(im, ax=ax_heat)
        cbar.set_label(self.data_types.get(data_type, data_type))
        
        # Configure heatmap axes
        self._setup_heatmap_axes(ax_heat)
        
        # Add structures if requested
        if show_structures and ax_struct:
            self._add_structures(ax_struct, data)
            
        # Add title if provided
        if title:
            fig.suptitle(title, fontsize=14)
            
        return fig
        
    def save_heatmap(self, 
                     figure: Figure, 
                     filepath: str,
                     dpi: int = 300):
        """
        Save heatmap figure to file
        
        Args:
            figure: matplotlib Figure object
            filepath: Path to save the file
            dpi: Resolution for the output image
        """
        try:
            figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
            self.logger.info(f"Heatmap saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save heatmap: {str(e)}")
            raise
        
    def _prepare_plate_data(self, 
                           data: List[Dict],
                           value_key: str
                           ) -> np.ndarray:
        """准备板式数据矩阵"""
        plate_data = np.zeros((self.PLATE_ROWS, self.PLATE_COLS))
        plate_data.fill(np.nan)  # 使用NaN表示空孔
        
        for sample in data:
            if 'well' in sample:
                row, col = self._parse_well_position(sample['well'])
                if 0 <= row < self.PLATE_ROWS and 0 <= col < self.PLATE_COLS:
                    plate_data[row, col] = sample.get(value_key, 0)
                    
        return plate_data
        
    def _parse_well_position(self, well: str) -> tuple:
        """解析孔位标识（如'A1'）为行列索引"""
        if len(well) < 2:
            raise ValueError(f"Invalid well format: {well}")
            
        row = ord(well[0].upper()) - ord('A')
        col = int(well[1:]) - 1
        return row, col
        
    def _add_plate_labels(self, ax):
        """添加板式标签"""
        # 添加行标签 (A-H)
        ax.set_yticks(range(self.PLATE_ROWS))
        ax.set_yticklabels([chr(ord('A') + i) for i in range(self.PLATE_ROWS)])
        
        # 添加列标签 (1-12)
        ax.set_xticks(range(self.PLATE_COLS))
        ax.set_xticklabels([str(i+1) for i in range(self.PLATE_COLS)])
        
    def _add_structures(self, ax, data: List[Dict]):
        """添加化合物结构图"""
        # 清除坐标轴
        ax.axis('off')
        
        # 获取唯一的SMILES
        unique_smiles = set(sample['smiles'] for sample in data if 'smiles' in sample)
        
        # 为每个化合物生成结构图
        for i, smiles in enumerate(unique_smiles):
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    img = Draw.MolToImage(mol, size=self.STRUCTURE_SIZE)
                    # 在右侧面板添加结构图
                    ax.imshow(img, extent=[i, i+1, 0, 1])
            except Exception as e:
                self.logger.error(f"Error drawing structure for SMILES {smiles}: {str(e)}") 