import sys
from PyQt5.QtWidgets import QApplication  # Change from PySide2 to PyQt5
from views.main_window import PythonExecutor

def main():
    app = QApplication(sys.argv)
    executor = PythonExecutor()
    executor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
