import os
import subprocess
import sys

def build_exe():
    print("Building Shocking VRChat EXE...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the command using python -m PyInstaller for better reliability
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "Shocking-VRChat",
        # Add templates folder just in case
        "--add-data", "templates;templates",
        # Ensure all submodules are captured
        "--collect-all", "srv",
        "gui_app.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful! The executable can be found in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")

if __name__ == "__main__":
    build_exe()

