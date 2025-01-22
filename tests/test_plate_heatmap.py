import pytest
import numpy as np
from pathlib import Path
from src.visualization.plate_heatmap import PlateHeatmap

class TestPlateHeatmap:
    @pytest.fixture
    def heatmap_generator(self):
        return PlateHeatmap()
        
    @pytest.fixture
    def sample_data(self):
        return [
            {
                'well': 'A1',
                'smiles': 'NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O',
                'purity': 95.5,
                'sample_id': 'SAMPLE001'
            },
            {
                'well': 'B2',
                'smiles': 'NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O',
                'purity': 87.3,
                'sample_id': 'SAMPLE002'
            }
        ]
        
    def test_generate_heatmap(self, heatmap_generator, sample_data, tmp_path):
        # 测试基本热图生成
        fig = heatmap_generator.generate_heatmap(sample_data)
        assert fig is not None
        
        # 测试带结构的热图生成
        fig_with_struct = heatmap_generator.generate_heatmap(
            sample_data,
            show_structures=True
        )
        assert fig_with_struct is not None
        
        # 测试保存热图
        output_path = tmp_path / "test_heatmap.png"
        fig = heatmap_generator.generate_heatmap(
            sample_data,
            output_path=output_path
        )
        assert output_path.exists()
        
    def test_parse_well_position(self, heatmap_generator):
        # 测试正常孔位解析
        row, col = heatmap_generator._parse_well_position('A1')
        assert row == 0
        assert col == 0
        
        row, col = heatmap_generator._parse_well_position('H12')
        assert row == 7
        assert col == 11
        
        # 测试无效孔位
        with pytest.raises(ValueError):
            heatmap_generator._parse_well_position('X')
            
    def test_prepare_plate_data(self, heatmap_generator, sample_data):
        plate_data = heatmap_generator._prepare_plate_data(sample_data, 'purity')
        assert isinstance(plate_data, np.ndarray)
        assert plate_data.shape == (8, 12)
        assert np.isnan(plate_data).sum() == 94  # 96孔板中的94个空孔
        assert plate_data[0, 0] == 95.5  # A1
        assert plate_data[1, 1] == 87.3  # B2 