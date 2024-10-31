import sys
from PySide2.QtWidgets import QApplication
from views.main_window import PythonExecutor

def main():
    app = QApplication(sys.argv)
    executor = PythonExecutor()
    executor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()