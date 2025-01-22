from pathlib import Path
import subprocess
import logging
from typing import Dict, Optional
import tempfile
import os
import shutil
import platform

class RawConverter:
    """Waters .raw 文件转换器"""
    
    def __init__(self):
        self.logger = logging.getLogger('RawConverter')
        self.is_windows = platform.system() == "Windows"
        self.msconvert_path = self._find_msconvert() if self.is_windows else None
        
    def _find_msconvert(self) -> Optional[str]:
        """查找 MSConvert 可执行文件"""
        if not self.is_windows:
            return None
            
        # ProteoWizard 常见安装路径
        possible_paths = [
            r"C:\Program Files\ProteoWizard\msconvert.exe",
            r"C:\Program Files (x86)\ProteoWizard\msconvert.exe",
            r"C:\Program Files\ProteoWizard\ProteoWizard\msconvert.exe",
            r"C:\Program Files (x86)\ProteoWizard\ProteoWizard\msconvert.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
                
        self.logger.warning("MSConvert not found in common installation paths")
        return None
        
    def convert_to_mzml(self, raw_dir: Path) -> Path:
        """使用 MSConvert 将 Waters .raw 文件夹转换为 mzML 格式"""
        if not self.is_windows:
            raise RuntimeError("MSConvert with vendor file support only works on Windows")
            
        if not raw_dir.is_dir() or raw_dir.suffix.lower() != '.raw':
            raise ValueError(f"Invalid Waters .raw folder: {raw_dir}")
            
        if not self.msconvert_path:
            raise RuntimeError(
                "MSConvert not found. Please install ProteoWizard 64-bit with vendor file support.\n"
                "Download from: http://proteowizard.sourceforge.net/downloads.shtml"
            )
            
        try:
            # 创建临时目录存放转换后的文件
            temp_dir = Path(tempfile.mkdtemp())
            output_file = temp_dir / f"{raw_dir.stem}.mzML"
            
            # 构建 MSConvert 命令
            cmd = [
                self.msconvert_path,
                str(raw_dir),
                '--mzML',                    # 输出格式
                '-o', str(temp_dir),         # 输出目录
                '--filter', "peakPicking",   # 峰检测
                '--filter', "msLevel 1-",    # 所有MS级别
                '--zlib',                    # 压缩
                '--ignoreUnknownInstrumentError'
            ]
            
            # 执行转换
            self.logger.info(f"Converting {raw_dir} to mzML...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(
                    f"MSConvert failed: {stderr}\n"
                    "Please ensure you have installed ProteoWizard 64-bit with vendor file support."
                )
                
            if not output_file.exists():
                raise FileNotFoundError(f"MSConvert did not generate output file: {output_file}")
                
            # 将文件移动到目标目录
            target_dir = raw_dir.parent.parent / 'mzml'
            target_dir.mkdir(exist_ok=True)
            target_file = target_dir / output_file.name
            
            shutil.move(str(output_file), str(target_file))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            self.logger.info(f"Conversion completed: {target_file}")
            return target_file
            
        except Exception as e:
            self.logger.error(f"Error converting file: {str(e)}")
            raise
            
    def check_msconvert(self) -> bool:
        """检查 MSConvert 是否可用"""
        if not self.is_windows:
            return False
            
        try:
            if not self.msconvert_path or not Path(self.msconvert_path).exists():
                return False
                
            process = subprocess.run(
                [self.msconvert_path, '--help'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            return process.returncode == 0
        except Exception:
            return False
            
    def read_raw_folder(self, raw_dir: Path) -> Dict:
        """读取完整的 Waters .raw 文件夹"""
        if not self.is_windows:
            # 在非Windows系统上返回模拟数据用于开发测试
            return {
                'ms_data': None,
                'pda_data': None,
                'metadata': {
                    'instrument': 'Development Mode',
                    'date': '2024-01-01',
                    'operator': 'Test User'
                }
            }
            
        # ... 其余代码保持不变 ... 