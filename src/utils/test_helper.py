class TestHelper:
    @staticmethod
    def verify_installation():
        """Verify required software installation"""
        # Check MSConvert
        msconvert_path = Path("C:/Program Files/ProteoWizard/MSConvert.exe")
        if not msconvert_path.exists():
            raise EnvironmentError("MSConvert not found")
            
        # Check Waters Raw file reader
        try:
            import pymsfilereader
        except ImportError:
            raise EnvironmentError("Waters Raw file reader not installed")
            
        # Check other dependencies
        required_packages = ['numpy', 'pandas', 'matplotlib', 'rdkit']
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                raise EnvironmentError(f"{package} not installed") 