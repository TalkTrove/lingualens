#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PACKAGE_NAME="lingualens" # Adjust if your package name differs
SRC_FOLDER="src"
INIT_FILE="${SRC_FOLDER}/__init__.py"
# ---------------------

# Function to print messages
info() {
    echo -e "\033[1;34m=> $1\033[0m"
}

error() {
    echo -e "\033[1;31mError: $1\033[0m" >&2
    exit 1
}

# Function to confirm actions
confirm() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;; # Proceed
            [Nn]* ) return 1;; # Skip
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

# 1. Get Current Version
info "Reading current version from ${INIT_FILE}..."
CURRENT_VERSION=$(grep -oP "^__version__\s*=\s*['\"]\K[^'\"]+" "$INIT_FILE")
if [ -z "$CURRENT_VERSION" ]; then
    error "Could not find __version__ in ${INIT_FILE}"
fi
echo "Current version: $CURRENT_VERSION"

# 2. Prompt for New Version
read -p "Enter new version (current is $CURRENT_VERSION, press Enter to keep): " NEW_VERSION
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
    info "Keeping current version: $NEW_VERSION"
else
    # Basic validation (adjust regex if versioning scheme differs)
    if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.dev[0-9]+)?$ ]]; then
        error "Invalid version format. Please use X.Y.Z or X.Y.Z.devN"
    fi
fi

# 3. Update Version if Changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    info "Updating version in ${INIT_FILE} to ${NEW_VERSION}..."
    # Use sed to replace the version string (works on GNU sed, macOS sed might need '' after -i)
    sed -i -E "s/^(__version__\s*=\s*['\"])[^'\"]+(['\"])/\1${NEW_VERSION}\2/" "$INIT_FILE"
    echo "Version updated."
else
    info "Version unchanged."
fi

# 4. Clean Build Artifacts
info "Cleaning previous build artifacts..."
rm -rf dist/ build/ *.egg-info "${SRC_FOLDER}"/*.egg-info
echo "Cleaning complete."

# 5. Build the Package
info "Building source distribution and wheel..."
python -m build
echo "Build complete."

# 6. Check the Package
info "Checking distributions with twine..."
python -m twine check dist/*
echo "Twine check complete."

# 7. Upload to TestPyPI (Optional)
info "--- Upload Steps ---"
echo -e "\033[1;33mIMPORTANT: Twine will prompt for authentication (use an API token!).\033[0m"
echo "===================================================="

if confirm "\nUpload to TestPyPI?"; then
    info "Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    info "Uploaded to TestPyPI."
    echo -e "\nConsider installing from TestPyPI to verify:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --no-deps ${PACKAGE_NAME}==${NEW_VERSION}"
else
    info "Skipping TestPyPI upload."
fi

# 8. Upload to PyPI (Optional)
if confirm "\nUpload to PyPI (LIVE)?"; then
    info "Uploading to PyPI..."
    python -m twine upload dist/*
    info "Successfully uploaded ${PACKAGE_NAME} version ${NEW_VERSION} to PyPI!"
else
    info "Skipping PyPI upload."
fi

info "Publish script finished." 