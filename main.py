# main.py
import sys
from PyQt6.QtWidgets import QApplication
from code_editor import CodeEditor



if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    sys.exit(app.exec())

