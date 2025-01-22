from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, 
                             QTableView, QPushButton, QToolBar)
from PySide6.QtCore import Qt
import pandas as pd
from ..visualization.chromatogram_viewer import ChromatogramViewer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class ResultViewer(QWidget):
    """Advanced result viewer with multiple visualization options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.addAction("Export", self.export_results)
        toolbar.addAction("Print", self.print_results)
        layout.addWidget(toolbar)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add different views
        self.table_view = QTableView()
        self.tabs.addTab(self.table_view, "Data Table")
        
        self.chromatogram_widget = self._create_chromatogram_widget()
        self.tabs.addTab(self.chromatogram_widget, "Chromatograms")
        
        self.spectrum_widget = self._create_spectrum_widget()
        self.tabs.addTab(self.spectrum_widget, "Spectra")
        
        layout.addWidget(self.tabs)
        
    def update_results(self, results: Dict):
        """Update all views with new results"""
        # Update table view
        if 'data_table' in results:
            model = pd.DataFrame(results['data_table'])
            self.table_view.setModel(model)
            
        # Update chromatogram view
        if 'chromatograms' in results:
            self._update_chromatogram(results['chromatograms'])
            
        # Update spectrum view
        if 'spectra' in results:
            self._update_spectrum(results['spectra']) 