from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
                             QLabel, QLineEdit, QMessageBox, QProgressBar, QInputDialog)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
from pathlib import Path
import pandas as pd
import platform
from ..analysis.data_processor import DataProcessor
from ..visualization.plate_heatmap import PlateHeatmap
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from ..visualization.chromatogram_viewer import ChromatogramViewer
from ..utils.error_handler import ErrorHandler
from ..ui.progress_dialog import ProcessingDialog
from ..ui.result_viewer import ResultViewer
from typing import Dict

class ProcessingThread(QThread):
    """Background processing thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, processor, raw_dir: Path, smiles: str):
        super().__init__()
        self.processor = processor
        self.raw_dir = raw_dir
        self.smiles = smiles
        
    def run(self):
        try:
            # Process the entire .raw folder
            result = self.processor.process_sample(
                raw_file=self.raw_dir,
                sample_id=self.raw_dir.stem,
                smiles=self.smiles
            )
            self.progress.emit(100)
            self.finished.emit([result])
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.error_handler = ErrorHandler()
        self.progress_dialog = None
        self.result_viewer = None
        self.setup_ui()
        
    def process_files(self, files):
        """Process selected files with progress tracking"""
        self.progress_dialog = ProcessingDialog(self)
        
        try:
            # Start processing
            self.processor.process_files(
                files,
                progress_callback=self._update_progress,
                error_callback=self._handle_error
            )
            
            # Show results
            self._show_results(self.processor.get_results())
            
        except Exception as e:
            self.error_handler.handle_error(
                'processing_failed',
                {'reason': str(e)},
                self
            )
            
    def _update_progress(self, value: int, status: str, detail: str):
        """Update progress dialog"""
        if self.progress_dialog:
            self.progress_dialog.update_progress(value, status, detail)
            
    def _show_results(self, results: Dict):
        """Display results in the result viewer"""
        if not self.result_viewer:
            self.result_viewer = ResultViewer(self)
            self.setCentralWidget(self.result_viewer)
            
        self.result_viewer.update_results(results) 