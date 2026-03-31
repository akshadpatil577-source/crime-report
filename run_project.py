"""
run_project.py

Cross-platform helper to:
- find a Python 3.11 or 3.12 interpreter
- create a venv (.venv311) if missing
- install project dependencies from requirements.txt into the venv
- run the Flask app using the venv's Python

Usage:
    python run_project.py          # setup (if needed) and run the app
    python run_project.py --setup  # only setup environment
    python run_project.py --venv .venv   # choose a custom venv directory

Notes:
- On Windows the script prefers the "py -3.11" launcher if present.
- The script prints helpful instructions if a compatible Python is not found.
"""

from __future__ import annotations
import os
import sys
import shutil
import subprocess
import platform
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VENV = os.path.join(ROOT, ".venv311")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")
APP_FILE = os.path.join(ROOT, "app.py")


def find_python_311() -> str | None:
    """Return a command to use for Python 3.11/3.12 (executable or launcher), or None."""
    # Windows: prefer "py -3.11" launcher
    if platform.system() == "Windows":
        for ver in ("3.11", "3.12"):
            try:
                p = subprocess.run(["py", f"-{ver}", "-c", "import sys; print(sys.executable)"],
                                   capture_output=True, text=True, check=True)
                exe = p.stdout.strip()
                if exe:
                    return f"py -{ver}"
            except Exception:
                continue
    # Try common executable names
    for name in ("python3.11", "python3.12", "python3", "python"):
        path = shutil.which(name)
        if not path:
            continue
        try:
            p = subprocess.run([path, "-c", "import sys; print(sys.version)"], capture_output=True, text=True, check=True)
            out = p.stdout.strip() or p.stderr.strip()
            if out.startswith("3.11") or out.startswith("3.12") or "3.11" in out or "3.12" in out:
                return path
        except Exception:
            continue
    return None


def run(cmd, **kwargs):
    print("+", " ".join(cmd) if isinstance(cmd, (list, tuple)) else cmd)
    subprocess.check_call(cmd, **kwargs)


def create_venv(python_cmd: str, venv_path: str):
    if os.path.isdir(venv_path):
        print(f"Virtual environment already exists at: {venv_path}")
        return
    print(f"Creating virtual environment at: {venv_path}")
    # If python_cmd is like 'py -3.11', split and run
    if isinstance(python_cmd, str) and python_cmd.startswith("py "):
        parts = python_cmd.split()
        run(parts + ["-m", "venv", venv_path])
    else:
        run([python_cmd, "-m", "venv", venv_path])


def venv_python(venv_path: str) -> str:
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")


def install_requirements(python_exe: str):
    print("Installing dependencies into venv...")
    run([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    if os.path.isfile(REQUIREMENTS):
        run([python_exe, "-m", "pip", "install", "-r", REQUIREMENTS])
    else:
        print("No requirements.txt found; skipping dependency install.")


def start_app(python_exe: str):
    if not os.path.isfile(APP_FILE):
        print(f"Error: {APP_FILE} not found.")
        sys.exit(1)
    print("Starting Flask app (press Ctrl+C to stop)...")
    run([python_exe, APP_FILE])


def main():
    parser = argparse.ArgumentParser(description="Setup & run Crime Report Portal")
    parser.add_argument("--setup", action="store_true", help="Only set up the environment, do not run the app")
    parser.add_argument("--venv", default=DEFAULT_VENV, help="Path to virtualenv directory")

    args = parser.parse_args()

    python_cmd = find_python_311()
    if not python_cmd:
        print("Compatible Python (3.11 or 3.12) not found on PATH or via py launcher.")
        print("Please install Python 3.11 or 3.12 and rerun, or use the steps in RUN_COMMANDS.md.")
        sys.exit(2)

    print("Using Python command:", python_cmd)

    try:
        create_venv(python_cmd, args.venv)
        pyexe = venv_python(args.venv)
        if not os.path.isfile(pyexe):
            print(f"ERROR: created venv but python not found at {pyexe}")
            sys.exit(3)

        install_requirements(pyexe)

        if args.setup:
            print("Setup completed. Activate your venv and run the app with:")
            if platform.system() == "Windows":
                print(f"  & \"{args.venv}\\Scripts\\Activate.ps1\"\n  python app.py")
            else:
                print(f"  source {args.venv}/bin/activate\n  python app.py")
            return

        start_app(pyexe)

    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
