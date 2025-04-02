#Requires -Version 5.1

<#
.SYNOPSIS
Automates the build and PyPI publishing process for the lingualens package on Windows.

.DESCRIPTION
This script reads the current version, prompts for a new version, updates the package files,
builds the distribution, checks it with twine, and optionally uploads to TestPyPI and PyPI.
It uses twine for secure authentication (prompts or uses twine config).
Requires Python, pip, build, and twine to be installed and in the PATH.

.NOTES
Author: Gemini
Version: 1.0
Requires: Python, pip, wheel, build, twine
Ensure Execution Policy allows running local scripts (e.g., `Set-ExecutionPolicy RemoteSigned -Scope Process`).

.EXAMPLE
.\publish.ps1
#>

# --- Configuration ---
$PackageName = "lingualens" # Set your package name here
$SrcFolder = "src"
$InitFile = Join-Path -Path $PSScriptRoot -ChildPath $SrcFolder | Join-Path -ChildPath "__init__.py"
# ---------------------

# --- Script Setup ---
# Stop script on first error
$ErrorActionPreference = 'Stop'

# --- Helper Functions ---
function Write-Info {
    param([string]$Message)
    Write-Host "=> $Message" -ForegroundColor Cyan
}

function Write-Warn {
    param([string]$Message)
    Write-Host "WARN: $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "Error: $Message" -ForegroundColor Red
    # Use Write-Error to potentially stop script if $ErrorActionPreference wasn't 'Stop'
    # Write-Error $Message
}

function Confirm-Action {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Prompt
    )
    while ($true) {
        $Response = Read-Host -Prompt "$Prompt (y/n)"
        switch ($Response.ToLower().Trim()) {
            'y' { return $true }
            'n' { return $false }
            default { Write-Host "Please enter 'y' or 'n'." }
        }
    }
}

function Invoke-CommandWithErrorHandling {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Executable,
        [Parameter(Mandatory=$true)]
        [string[]]$Arguments
    )
    Write-Info "Running: $Executable $($Arguments -join ' ')"
    try {
        # Use Invoke-Expression for simplicity here, but consider Start-Process for more control
        # & $Executable $Arguments # This often works too
        Invoke-Expression "$Executable $($Arguments -join ' ')"

        # Check the exit code of the last command
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE."
        }
        Write-Host "Command finished successfully." -ForegroundColor Green
    }
    catch {
        Write-ErrorMsg "Failed to execute command: $Executable $($Arguments -join ' ')"
        Write-ErrorMsg "Error details: $($_.Exception.Message)"
        # Exit the script on command failure
        exit 1
    }
}


# --- Main Script ---

# 1. Get Current Version
Write-Info "Reading current version from $InitFile..."
$VersionRegex = '^__version__\s*=\s*[''"](?<version>[^''"]+)[''"]'
try {
    $CurrentVersion = (Get-Content -Path $InitFile -Raw | Select-String -Pattern $VersionRegex).Matches.Groups['version'].Value
} catch {
    Write-ErrorMsg "Could not read or find version pattern in $InitFile."
    Write-ErrorMsg "Error details: $($_.Exception.Message)"
    exit 1
}

if (-not $CurrentVersion) {
    Write-ErrorMsg "Could not extract __version__ string from $InitFile using regex '$VersionRegex'."
    exit 1
}
Write-Host "Current version: $CurrentVersion"

# 2. Prompt for New Version
$NewVersion = ""
while ($true) {
    $NewVersion = Read-Host -Prompt "Enter new version (current is $CurrentVersion, press Enter to keep)"
    if (-not $NewVersion) { # If user pressed Enter
        $NewVersion = $CurrentVersion
        Write-Info "Keeping current version: $NewVersion"
        break
    }
    # Basic validation
    if ($NewVersion -match '^\d+\.\d+\.\d+(\.dev\d+)?$') {
        break
    } else {
        Write-Warn "Invalid version format. Please use X.Y.Z or X.Y.Z.devN"
    }
}

# 3. Update Version if Changed
if ($NewVersion -ne $CurrentVersion) {
    Write-Info "Updating version in $InitFile to $NewVersion..."
    try {
        # Read, Replace, Write
        (Get-Content -Path $InitFile -Raw) -replace "(^__version__\s*=\s*['""])[^'""]+(['""])", "`$1$NewVersion`$2" | Set-Content -Path $InitFile
        Write-Host "Version updated."
    } catch {
        Write-ErrorMsg "Failed to update version in $InitFile."
        Write-ErrorMsg "Error details: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Info "Version unchanged."
}

# 4. Clean Build Artifacts
Write-Info "Cleaning previous build artifacts..."
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "." -Filter "*.egg-info" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $SrcFolder -Filter "*.egg-info" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cleaning complete."

# 5. Build the Package
Write-Info "Building source distribution and wheel..."
# Use 'python' - adjust if you need 'py', 'python3', or a specific path
Invoke-CommandWithErrorHandling -Executable "python" -Arguments "-m", "build"
Write-Host "Build complete."

# 6. Check the Package
Write-Info "Checking distributions with twine..."
# Use 'python' - adjust if needed
Invoke-CommandWithErrorHandling -Executable "python" -Arguments "-m", "twine", "check", "dist/*"
Write-Host "Twine check complete."

# 7. Upload to TestPyPI (Optional)
Write-Info "--- Upload Steps ---"
Write-Host "IMPORTANT: Twine will prompt for authentication." -ForegroundColor Yellow
Write-Host "It is recommended to use a PyPI API token instead of your password." -ForegroundColor Yellow
Write-Host "NEVER hardcode credentials in scripts." -ForegroundColor Yellow
Write-Host ("=" * 52)

if (Confirm-Action "`nUpload to TestPyPI?") {
    Write-Info "Uploading to TestPyPI..."
    # Use 'python' - adjust if needed
    Invoke-CommandWithErrorHandling -Executable "python" -Arguments "-m", "twine", "upload", "--repository", "testpypi", "dist/*"
    Write-Info "Uploaded to TestPyPI."
    Write-Host "`nConsider installing from TestPyPI to verify:" -ForegroundColor Green
    Write-Host "  pip install --index-url https://test.pypi.org/simple/ --no-deps ${PackageName}==${NewVersion}" -ForegroundColor Green
} else {
    Write-Info "Skipping TestPyPI upload."
}

# 8. Upload to PyPI (Optional)
if (Confirm-Action "`nUpload to PyPI (LIVE)?") {
    Write-Info "Uploading to PyPI..."
    # Use 'python' - adjust if needed
    Invoke-CommandWithErrorHandling -Executable "python" -Arguments "-m", "twine", "upload", "dist/*"
    Write-Info "Successfully uploaded ${PackageName} version ${NewVersion} to PyPI!"
} else {
    Write-Info "Skipping PyPI upload."
}

Write-Info "Publish script finished."