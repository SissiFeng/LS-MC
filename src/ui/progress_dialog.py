from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt, Signal

class ProcessingDialog(QDialog):
    """Custom progress dialog with detailed status information"""
    
    cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Data")
        self.setModal(True)
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Main progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Detailed status
        self.detail_label = QLabel("")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        
        self.setMinimumWidth(400)
        
    def update_progress(self, value: int, status: str = "", detail: str = ""):
        """Update progress bar and status information"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
        if detail:
            self.detail_label.setText(detail) 