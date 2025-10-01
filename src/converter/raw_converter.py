from pathlib import Path
import subprocess
import logging
from typing import Dict, Optional
import tempfile
import os
import shutil
import platform

class RawConverter:
    """Waters .raw file converter"""

    def __init__(self):
        self.logger = logging.getLogger('RawConverter')
        self.is_windows = platform.system() == "Windows"
        self.msconvert_path = self._find_msconvert() if self.is_windows else None

    def _find_msconvert(self) -> Optional[str]:
        """Find MSConvert executable"""
        if not self.is_windows:
            return None

        # Common ProteoWizard installation paths
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
        """Use MSConvert to convert Waters .raw folder to mzML format"""
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
            # Create temporary directory for converted files
            temp_dir = Path(tempfile.mkdtemp())
            output_file = temp_dir / f"{raw_dir.stem}.mzML"

            # Build MSConvert command
            cmd = [
                self.msconvert_path,
                str(raw_dir),
                '--mzML',                    # Output format
                '-o', str(temp_dir),         # Output directory
                '--filter', "peakPicking",   # Peak detection
                '--filter', "msLevel 1-",    # All MS levels
                '--zlib',                    # Compression
                '--ignoreUnknownInstrumentError'
            ]

            # Execute conversion
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
                
            # Move file to target directory
            target_dir = raw_dir.parent.parent / 'mzml'
            target_dir.mkdir(exist_ok=True)
            target_file = target_dir / output_file.name

            shutil.move(str(output_file), str(target_file))

            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            self.logger.info(f"Conversion completed: {target_file}")
            return target_file
            
        except Exception as e:
            self.logger.error(f"Error converting file: {str(e)}")
            raise
            
    def check_msconvert(self) -> bool:
        """Check if MSConvert is available"""
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
        """Read complete Waters .raw folder"""
        if not self.is_windows:
            # Return mock data for development testing on non-Windows systems
            return {
                'ms_data': None,
                'pda_data': None,
                'metadata': {
                    'instrument': 'Development Mode',
                    'date': '2024-01-01',
                    'operator': 'Test User'
                }
            }

        # ... rest of the code remains unchanged ...