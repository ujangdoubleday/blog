#!/usr/bin/env python3
"""
Automated publishing script that combines build and deploy
"""

import subprocess
import sys
from pathlib import Path

# Configuration
BUILD_SCRIPT = Path(__file__).parent / "build.py"
DEPLOY_SCRIPT = Path(__file__).parent / "deploy.py"


def run_command(command: str, check: bool = True) -> bool:
    """Run a shell command and return success status"""
    try:
        subprocess.run(command, shell=True, check=check, executable="/bin/bash")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error details: {e}")
        return False


def main():
    """Main execution function"""
    print("=== Starting publication process ===")

    # Step 1: Run build
    print("\n[1/2] Building site...")
    if not run_command(f"python {BUILD_SCRIPT}"):
        sys.exit(1)

    # Step 2: Run deploy
    print("\n[2/2] Deploying site...")
    if not run_command(f"python {DEPLOY_SCRIPT}"):
        sys.exit(1)

    print("\n=== Publication completed successfully ===")


if __name__ == "__main__":
    main()
