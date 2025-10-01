from PySide6.QtCore import QObject, Slot, Signal, Property
from pathlib import Path
from ..converter import RawConverter
from ..analysis import DataProcessor
from ..analysis.data_validator import DataValidator
import logging

class Backend(QObject):
    resultDataChanged = Signal()
    statusChanged = Signal(str, str)  # (message, type: 'info'|'error'|'success')
    progressChanged = Signal(float)   # 0-100

    def __init__(self):
        super().__init__()
        self._result_data = []
        self._converter = RawConverter()
        self._processor = DataProcessor()
        self._parameters = {
            'peakHeight': 10000,
            'rtTolerance': 0.1
        }
        self.logger = logging.getLogger('Backend')
        self._validator = DataValidator()

    @Property('QVariantList', notify=resultDataChanged)
    def resultData(self):
        return self._result_data

    @Slot(str, str, list)
    def processFiles(self, sample_id: str, smiles: str, files: list):
        """Process selected raw files with sample information"""
        total_files = len(files)
        for i, file_url in enumerate(files):
            file_path = Path(file_url.toLocalFile())
            if file_path.suffix.lower() == '.raw':
                try:
                    self.statusChanged.emit(f"Processing file: {file_path.name}", "info")
                    self.progressChanged.emit((i / total_files) * 100)

                    # Process sample with complete information
                    result = self._processor.process_sample(
                        raw_file=file_path,
                        sample_id=sample_id,
                        smiles=smiles,
                        mass_tolerance=0.5
                    )
                    
                    # Update UI with complete result
                    self._result_data = [vars(result)]  # Convert dataclass to dict
                    self.resultDataChanged.emit()
                    self.statusChanged.emit(f"Successfully processed: {file_path.name}", "success")
                    
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    self.statusChanged.emit(f"Processing failed: {str(e)}", "error")

        self.progressChanged.emit(100)

    @Slot(dict)
    def updateParameters(self, params):
        """Update processing parameters"""
        self._parameters.update(params)

    @Slot()
    def exportResults(self):
        """Export processing results"""
        if self._result_data:
            try:
                output_dir = Path.home() / 'Waters_Results'
                self._processor.export_results(
                    {'peaks': pd.DataFrame(self._result_data)},
                    output_dir,
                    'analysis_results'
                )
            except Exception as e:
                print(f"Error exporting results: {str(e)}") 