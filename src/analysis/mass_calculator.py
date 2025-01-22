from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import logging
from typing import Dict

class MassCalculator:
    """Mass calculation module"""
    
    def __init__(self):
        self.logger = logging.getLogger('MassCalculator')
        
    def calculate_masses(self, smiles: str) -> Dict[str, float]:
        """Calculate all required masses from SMILES"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol:
                raise ValueError("Invalid SMILES string")
                
            # Calculate molecular formula
            formula = rdMolDescriptors.CalcMolFormula(mol)
            
            # Calculate monoisotopic mass
            mono_mass = rdMolDescriptors.CalcExactMolWt(mol)
            
            return {
                'formula': formula,
                'monoisotopic_mass': mono_mass,
                'mh_mass': mono_mass + 1.0078,  # [M+H]+
                'mna_mass': mono_mass + 22.9897,  # [M+Na]+
                'mh_minus_mass': mono_mass - 1.0073  # [M-H]-
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating masses: {str(e)}")
            raise 