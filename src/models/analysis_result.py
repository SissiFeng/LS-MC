from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class AnalysisResult:
    """Analysis result data model"""
    
    # Sample information
    sample_id: str
    smiles: str
    well: Optional[str] = None
    
    # Mass calculations
    formula: str
    monoisotopic_mass: float
    mh_mass: float
    mna_mass: float
    mh_minus_mass: float
    
    # Chromatogram analysis
    product_detected: bool
    retention_time: Optional[float]
    detected_mass: Optional[float]
    purity: float
    
    # Major peaks
    peak1_rt: Optional[float]
    peak1_mass: Optional[float]
    peak2_rt: Optional[float]
    peak2_mass: Optional[float]
    peak3_rt: Optional[float]
    peak3_mass: Optional[float]
    
    # Raw data
    pda_time: np.ndarray
    pda_intensity: np.ndarray
    ms_time: np.ndarray
    ms_pos_tic: np.ndarray
    ms_pos_mz: np.ndarray
    ms_pos_intensity: np.ndarray
    ms_neg_tic: np.ndarray
    ms_neg_mz: np.ndarray
    ms_neg_intensity: np.ndarray
    uv_wavelength: np.ndarray
    uv_absorbance: np.ndarray 