"""
Cross-platform Ollama setup runner.
Detects OS and runs the appropriate setup script.

Usage:
    python setup_ollama.py                  # Default model: llama3.2
    python setup_ollama.py --model mistral  # Custom model
"""
import platform
import subprocess
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).parent


def run_windows_setup(model: str):
    script = TOOLS_DIR / "setup_ollama_windows.ps1"
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script), "-Model", model],
        check=True,
    )


def run_linux_setup(model: str):
    script = TOOLS_DIR / "setup_ollama_linux.sh"
    script.chmod(0o755)
    subprocess.run(["bash", str(script), model], check=True)


def main():
    model = "llama3.2"
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    os_name = platform.system()
    print(f"Detected OS: {os_name}")
    print(f"Model: {model}")
    print()

    if os_name == "Windows":
        run_windows_setup(model)
    elif os_name == "Linux":
        run_linux_setup(model)
    elif os_name == "Darwin":
        # macOS uses the same install script as Linux
        run_linux_setup(model)
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
