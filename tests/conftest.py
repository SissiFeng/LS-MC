import pytest
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_data_dir():
    """返回测试数据目录的路径"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def sample_raw_file(test_data_dir):
    """返回示例raw文件的路径"""
    return os.path.join(test_data_dir, 'raw', 'AC P1 E3.raw') 