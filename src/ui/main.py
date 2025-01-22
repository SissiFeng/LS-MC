import sys
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Get the path to the main.qml file
    qml_file = Path(__file__).parent / "qml/main.qml"
    
    # Load the QML file
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if the QML file was loaded successfully
    if not engine.rootObjects():
        sys.exit(-1)
        
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 