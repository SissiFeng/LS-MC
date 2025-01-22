from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from rdkit.Chem.Draw import IPythonConsole
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Union
import numpy as np

class StructureViewer:
    """Enhanced molecule structure visualization"""
    
    def __init__(self):
        self.default_size = (300, 300)
        self.default_colors = {
            'C': (0.2, 0.2, 0.2),  # Dark gray
            'N': (0, 0, 1),        # Blue
            'O': (1, 0, 0),        # Red
            'S': (1, 0.8, 0),      # Yellow
            'F': (0, 1, 0),        # Green
            'Cl': (0, 0.8, 0),     # Dark green
            'Br': (0.6, 0, 0),     # Dark red
            'I': (0.4, 0, 0.4)     # Purple
        }
        
    def plot_structure(self,
                      smiles: str,
                      ax: Optional[plt.Axes] = None,
                      size: Tuple[int, int] = None,
                      show_atoms: bool = True,
                      show_bonds: bool = True,
                      highlight_atoms: Optional[list] = None) -> Union[plt.Axes, None]:
        """
        Plot molecular structure with enhanced visualization options
        
        Args:
            smiles: SMILES string of the molecule
            ax: Matplotlib axes for plotting
            size: Image size (width, height)
            show_atoms: Whether to show atom labels
            show_bonds: Whether to show bond labels
            highlight_atoms: List of atom indices to highlight
        """
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            raise ValueError("Invalid SMILES string")
            
        # Generate 2D coordinates if not present
        if not mol.GetNumConformers():
            AllChem.Compute2DCoords(mol)
            
        # Prepare drawing options
        drawer = Draw.rdDepictor.PrepareMolForDrawing(mol)
        
        # Create drawing options
        opts = Draw.DrawingOptions()
        opts.atomLabelFontSize = 12
        opts.bondLineWidth = 2
        opts.atomLabelsDist = 0.25
        
        # Generate image
        size = size or self.default_size
        img = Draw.MolToImage(
            mol,
            size=size,
            options=opts,
            highlightAtoms=highlight_atoms
        )
        
        if ax:
            ax.imshow(img)
            ax.axis('off')
            return ax
        else:
            return img
            
    def create_structure_grid(self,
                            smiles_list: list,
                            labels: Optional[list] = None,
                            ncols: int = 3,
                            figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
        """Create a grid of multiple structures"""
        n = len(smiles_list)
        nrows = (n + ncols - 1) // ncols
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        if nrows == 1:
            axes = [axes]
        axes = np.array(axes).flatten()
        
        for i, (ax, smiles) in enumerate(zip(axes, smiles_list)):
            self.plot_structure(smiles, ax)
            if labels and i < len(labels):
                ax.set_title(labels[i])
                
        # Hide empty subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis('off')
            
        plt.tight_layout()
        return fig 