import os
from PyQt5.QtCore import QProcess  # Change from PySide2 to PyQt5

class ScriptExecutor:
    @staticmethod
    def run_script(code, output_callback, sudo=False, password=None):
        temp_filename = "temp_script.py"
        with open(temp_filename, 'w') as temp_file:
            temp_file.write(code)

        process = QProcess()

        if sudo and password:
            sudo_command = f"echo {password} | sudo -S python3 {temp_filename}"
            process.start("bash", ["-c", sudo_command])
        else:
            process.start("python3", [temp_filename])

        process.waitForFinished()

        output = process.readAllStandardOutput().data().decode()
        error = process.readAllStandardError().data().decode()

        os.remove(temp_filename)

        if output:
            output_callback(f"Output:\n{output}")
        if error:
            output_callback(f"Error:\n{error}")
