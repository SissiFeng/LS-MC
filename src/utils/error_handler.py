from typing import Optional, Dict
from PySide6.QtWidgets import QMessageBox
import logging
from dataclasses import dataclass

@dataclass
class ProcessingError:
    """Structured error information"""
    error_type: str
    message: str
    details: Optional[str] = None
    suggestions: Optional[str] = None

class ErrorHandler:
    """Centralized error handling and user feedback"""
    
    def __init__(self):
        self.logger = logging.getLogger('ErrorHandler')
        
        # Error message templates
        self.error_templates = {
            'file_not_found': {
                'message': "File not found: {path}",
                'suggestions': "Please check if the file exists and you have proper permissions."
            },
            'invalid_format': {
                'message': "Invalid file format: {format}",
                'suggestions': "Please ensure you're using a supported Waters .raw file."
            },
            'processing_failed': {
                'message': "Data processing failed: {reason}",
                'suggestions': "Try processing the file again or contact support."
            }
        }
        
    def handle_error(self, error_type: str, context: Dict, parent=None) -> None:
        """Handle error and show appropriate message to user"""
        template = self.error_templates.get(error_type, {})
        message = template.get('message', str(context)).format(**context)
        suggestions = template.get('suggestions', "")
        
        self.logger.error(f"{error_type}: {message}")
        
        if parent:
            QMessageBox.critical(
                parent,
                "Error",
                f"{message}\n\nSuggestions:\n{suggestions}"
            ) 