import os
import subprocess

def compile_project():
    command = [
        "python", "-m", "nuitka",
        "--follow-imports",
        "--plugin-enable=pyside6",
        "--standalone",
        "--show-progress",
        "--show-memory",
        "--output-dir=build",
        "src/main.py"
    ]
    
    subprocess.run(command)

if __name__ == "__main__":
    compile_project()