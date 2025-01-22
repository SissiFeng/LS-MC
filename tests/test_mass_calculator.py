import pytest
from src.analysis.mass_calculator import MassCalculator
from src.models.analysis_result import MassInfo

class TestMassCalculator:
    @pytest.fixture
    def calculator(self):
        return MassCalculator()
    
    @pytest.fixture
    def test_smiles(self):
        # 使用README中提供的SMILES
        return "NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O"
    
    def test_calculate_masses(self, calculator, test_smiles):
        result = calculator.calculate_masses(test_smiles)
        
        assert isinstance(result, MassInfo)
        assert result.molecular_formula == "C21H23N5O4"
        assert pytest.approx(result.monoisotopic_mass, abs=0.001) == 409.1750
        assert pytest.approx(result.mh_mass, abs=0.001) == 410.1828
        assert pytest.approx(result.mna_mass, abs=0.001) == 432.1647
        assert pytest.approx(result.mh_negative_mass, abs=0.001) == 408.1677

    def test_invalid_smiles(self, calculator):
        result = calculator.calculate_masses("invalid_smiles")
        assert result is None

    def test_validate_mass_match(self, calculator):
        assert calculator.validate_mass_match(410.18, 410.1828, tolerance=0.5)
        assert not calculator.validate_mass_match(411.0, 410.1828, tolerance=0.5) 