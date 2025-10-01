import sys
from PySide6.QtWidgets import QApplication
from .ui.main_window import MainWindow
import logging

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create application
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 