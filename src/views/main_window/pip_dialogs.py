from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QDialogButtonBox,
                            QPlainTextEdit, QMessageBox)
from PyQt5.QtCore import Qt
import os
import subprocess
import sys

class RequirementsEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Requirements Editor")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        self.load_requirements()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add path label
        self.path_label = QLabel(f"Editing: {self.get_requirements_path()}")
        layout.addWidget(self.path_label)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Enter requirements, one per line")
        layout.addWidget(self.editor)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.save_requirements)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_requirements_path(self):
        # Get the project root directory (where src folder is)
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of this file
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))  # Go up to project root
        return os.path.join(project_root, 'requirements.txt')

    def load_requirements(self):
        requirements_path = self.get_requirements_path()
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    self.editor.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load requirements.txt: {str(e)}")
        else:
            QMessageBox.information(self, "Information", 
                                  f"No requirements.txt found at {requirements_path}\n"
                                  "A new file will be created when you save.")

    def save_requirements(self):
        try:
            requirements_path = self.get_requirements_path()
            with open(requirements_path, 'w') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Success", "Requirements file saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save requirements.txt: {str(e)}")

class PipExecutorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pip Command Executor")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add venv info
        venv_path = os.path.join(self.get_project_root(), 'venv')
        venv_label = QLabel(f"Using venv: {venv_path}")
        layout.addWidget(venv_label)

        # Command input
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("pip"))
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("install package_name")
        cmd_layout.addWidget(self.command_input)
        
        layout.addLayout(cmd_layout)

        # Execute button
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_command)
        layout.addWidget(self.execute_button)

        # Output display
        self.output_display = QPlainTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def get_project_root(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

    def get_venv_python(self):
        venv_dir = os.path.join(self.get_project_root(), 'venv')
        if os.name == 'nt':  # Windows
            python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:  # Linux/Mac
            python_path = os.path.join(venv_dir, 'bin', 'python')
            
        if not os.path.exists(python_path):
            raise FileNotFoundError(f"Virtual environment Python not found at: {python_path}")
        return python_path

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        try:
            # Get the Python executable from the venv
            python_exe = self.get_venv_python()
            self.output_display.appendPlainText(f"Using Python: {python_exe}")
            
            # Build and execute the pip command
            pip_cmd = [python_exe, '-m', 'pip'] + command.split()
            
            # Execute the pip command
            process = subprocess.Popen(
                pip_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.get_project_root()  # Set working directory to project root
            )
            
            stdout, stderr = process.communicate()
            
            # Display output
            if stdout:
                self.output_display.appendPlainText(stdout)
            if stderr:
                self.output_display.appendPlainText("Errors:\n" + stderr)
                
            if process.returncode == 0:
                self.output_display.appendPlainText("Command completed successfully.")
            else:
                self.output_display.appendPlainText(f"Command failed with return code {process.returncode}")
                
        except Exception as e:
            self.output_display.appendPlainText(f"Error executing command: {str(e)}")