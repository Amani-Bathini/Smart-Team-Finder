"""
Smart Team Finder - Required Dependencies & Auto-Installer
==========================================================
This file lists all required packages for Smart Team Finder and allows
you to automatically verify or install missing dependencies by running:
    python requirements.py
"""

import sys
import subprocess
import importlib.util

# Core application dependencies
REQUIRED_PACKAGES = [
    {
        "name": "Flask",
        "import_name": "flask",
        "version": ">=3.0.0",
        "pip_spec": "Flask>=3.0.0",
        "description": "Core Python Web Framework"
    },
    {
        "name": "mysql-connector-python",
        "import_name": "mysql.connector",
        "version": ">=8.0.0",
        "pip_spec": "mysql-connector-python>=8.0.0",
        "description": "Official MySQL database driver"
    },
    {
        "name": "bcrypt",
        "import_name": "bcrypt",
        "version": ">=4.0.0",
        "pip_spec": "bcrypt>=4.0.0",
        "description": "Password hashing and verification"
    },
    {
        "name": "python-dotenv",
        "import_name": "dotenv",
        "version": ">=1.0.0",
        "pip_spec": "python-dotenv>=1.0.0",
        "description": "Loads environment variables from .env"
    },
    {
        "name": "PyMySQL",
        "import_name": "pymysql",
        "version": ">=1.0.0",
        "pip_spec": "PyMySQL>=1.0.0",
        "description": "Pure Python MySQL client (fallback/support)"
    }
]


def check_and_install():
    """Verify all required packages and install any that are missing."""
    print("=" * 60)
    print(" Smart Team Finder - Dependency Checker & Installer")
    print("=" * 60)

    missing = []

    for pkg in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(pkg["import_name"].split(".")[0])
        if spec is not None:
            print(f" [OK] {pkg['name']:<24} - {pkg['description']}")
        else:
            print(f" [MISSING] {pkg['name']:<20} - {pkg['description']}")
            missing.append(pkg["pip_spec"])

    print("-" * 60)

    if not missing:
        print(" All required packages are already installed and verified!")
        print(" You can start the app using: python app.py")
        print("=" * 60)
        return True

    print(f" Found {len(missing)} missing package(s): {', '.join(missing)}")
    print(" Installing missing packages now...\n")

    cmd = [sys.executable, "-m", "pip", "install"] + missing
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("\n All dependencies were installed successfully!")
            print(" You can now run the app using: python app.py")
            print("=" * 60)
            return True
    except subprocess.CalledProcessError as e:
        print(f"\n Error installing dependencies: {e}")
        print(" Please run manually: pip install " + " ".join(missing))
        print("=" * 60)
        return False


if __name__ == "__main__":
    check_and_install()

