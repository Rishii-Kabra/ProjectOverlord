import subprocess
import sys
import os

class ShellTool:
    def __init__(self, workspace_dir="workspace"):
        self.workspace_dir = os.path.abspath(workspace_dir)

    def execute_python(self, file_name):
        #guard rail for when AI forgot the file name
        if not file_name:
            return "Error: You didn't provide a file_name to run. Please specify a file to run."
        file_path = os.path.join(self.workspace_dir, file_name)
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True, text=True, timeout=15,
                cwd=self.workspace_dir
            )
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def install_package(self, package_name):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return f"Installed package: {package_name}"
        except Exception as e:
            return f"Failed to install {package_name}: {e}"