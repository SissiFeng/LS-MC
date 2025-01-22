from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
from typing import Dict

class MolecularCalculator:
    """Calculate molecular parameters from SMILES"""
    
    def calculate_masses(self, smiles: str) -> Dict[str, float]:
        """Calculate molecular masses and related parameters"""
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            raise ValueError("Invalid SMILES string")
            
        mono_mass = Descriptors.ExactMolWt(mol)
        
        return {
            'formula': AllChem.rdMolDescriptors.CalcMolFormula(mol),
            'monoisotopic_mass': mono_mass,
            'mh_mass': mono_mass + 1.0078,  # [M+H]+
            'mna_mass': mono_mass + 22.9897,  # [M+Na]+
            'mh_minus_mass': mono_mass - 1.0073  # [M-H]-
        } 