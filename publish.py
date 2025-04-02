import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

# --- Configuration ---
PACKAGE_NAME = "lingualens" # Set your package name here
SRC_FOLDER = Path("src")
INIT_FILE = SRC_FOLDER / "__init__.py"
# ---------------------

def run_command(command, cwd=None, capture_output=False, text=True, check=True):
    """Runs a shell command."""
    print(f"\n>> Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=text,
            check=check # Will raise CalledProcessError if command fails
        )
        print("Command finished successfully.")
        return result
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}", file=sys.stderr)
        print("Please ensure the necessary tools (like build, twine) are installed and in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(f"stdout:\n{e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"stderr:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def get_current_version():
    """Reads the current version from the __init__.py file."""
    try:
        with open(INIT_FILE, "r") as f:
            content = f.read()
            match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", content, re.MULTILINE)
            if match:
                return match.group(1)
            else:
                print(f"Error: Could not find __version__ in {INIT_FILE}", file=sys.stderr)
                sys.exit(1)
    except FileNotFoundError:
        print(f"Error: {INIT_FILE} not found.", file=sys.stderr)
        sys.exit(1)

def update_version(new_version):
    """Updates the version in the __init__.py file."""
    try:
        with open(INIT_FILE, "r") as f:
            content = f.read()

        new_content, n_subs = re.subn(
            r"(^__version__\s*=\s*['\"])([^'\"]*)(['\"])",
            f"\g<1>{new_version}\g<3>",
            content,
            count=1,
            flags=re.MULTILINE
        )

        if n_subs == 0:
            print(f"Error: Could not find line to update __version__ in {INIT_FILE}", file=sys.stderr)
            sys.exit(1)

        with open(INIT_FILE, "w") as f:
            f.write(new_content)
        print(f"Updated version in {INIT_FILE} to {new_version}")
    except FileNotFoundError:
        print(f"Error: {INIT_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error updating version file: {e}", file=sys.stderr)
        sys.exit(1)

def clean_build_artifacts():
    """Removes previous build artifacts."""
    print("\nCleaning build artifacts...")
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    egg_info_dirs = list(Path(".").glob(f"{PACKAGE_NAME}.egg-info")) + \
                    list(SRC_FOLDER.glob(f"{PACKAGE_NAME}.egg-info"))
    for d in egg_info_dirs:
        print(f"Removing {d}...")
        shutil.rmtree(d, ignore_errors=True)
    print("Cleaning complete.")

def confirm_action(prompt):
    """Asks the user for confirmation."""
    while True:
        response = input(f"{prompt} (y/n): ").lower().strip()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Please enter 'y' or 'n'.")

def main():
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    while True:
        new_version = input(f"Enter new version (current is {current_version}): ").strip()
        if not new_version:
            new_version = current_version # Keep current if blank
            print(f"Keeping current version: {new_version}")
            break
        # Simple validation (you might want a more robust check)
        if re.match(r"^\d+\.\d+\.\d+(\.dev\d+)?$", new_version):
            break
        else:
            print("Invalid version format. Please use X.Y.Z or X.Y.Z.devN")

    if new_version != current_version:
        update_version(new_version)
    else:
        print("Version unchanged.")

    # --- Build Steps ---
    clean_build_artifacts()

    # Build distributions
    run_command([sys.executable, "-m", "build"])

    # Check distributions
    run_command([sys.executable, "-m", "twine", "check", "dist/*"])

    # --- Upload Steps ---
    print("\n--- Upload Options --- " + "="*30)
    print("IMPORTANT: Twine will prompt for authentication.")
    print("It is recommended to use a PyPI API token instead of your password.")
    print("NEVER hardcode credentials in scripts.")
    print("="*52)

    if confirm_action("\nUpload to TestPyPI?"): 
        run_command([
            sys.executable, "-m", "twine", "upload",
            "--repository", "testpypi",
            "dist/*"
        ])
        print("\nConsider installing from TestPyPI to verify:")
        print(f"  pip install --index-url https://test.pypi.org/simple/ --no-deps {PACKAGE_NAME}=={new_version}")
    else:
        print("Skipping TestPyPI upload.")

    if confirm_action("\nUpload to PyPI (Live)?"): 
        run_command([
            sys.executable, "-m", "twine", "upload",
            "dist/*"
        ])
        print(f"\nSuccessfully uploaded {PACKAGE_NAME} version {new_version} to PyPI!")
    else:
        print("Skipping PyPI upload.")

    print("\nPublish script finished.")

if __name__ == "__main__":
    main() 