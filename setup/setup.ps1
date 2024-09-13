# Requires PowerShell 5.0 or higher

# Exit immediately if a command exits with a non-zero status.
$ErrorActionPreference = "Stop"

# Define the required Python version.
$PYTHON_VERSION = "3.10.7"

Write-Host "Starting setup..."

function Install-Pyenv {
    Write-Host "Installing Pyenv-Win..."

    # Install pyenv-win via Git
    git clone https://github.com/pyenv-win/pyenv-win.git $env:USERPROFILE\.pyenv

    # Add Pyenv to the user environment variables
    [Environment]::SetEnvironmentVariable("PYENV", "$env:USERPROFILE\.pyenv\pyenv-win\", "User")
    [Environment]::SetEnvironmentVariable("Path", "$env:PYENV\bin;$env:PYENV\shims;$([Environment]::GetEnvironmentVariable('Path', 'User'))", "User")

    # Update the current session's environment variables
    $env:PYENV = "$env:USERPROFILE\.pyenv\pyenv-win\"
    $env:Path = "$env:PYENV\bin;$env:PYENV\shims;$env:Path"
}

# Install Git if not installed
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Installing Git..."
    # Download and install Git silently
    $gitInstaller = "$env:TEMP\Git-setup.exe"
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/Git-2.41.0-64-bit.exe" -OutFile $gitInstaller
    Start-Process -FilePath $gitInstaller -ArgumentList '/VERYSILENT' -Wait
    Remove-Item $gitInstaller
}

# Check if Pyenv is installed
if (-not (Get-Command pyenv.exe -ErrorAction SilentlyContinue)) {
    Install-Pyenv
} else {
    Write-Host "Pyenv-Win is already installed."
}

# Install the required Python version using Pyenv
if (-not (pyenv versions | Select-String -Pattern "^$PYTHON_VERSION$")) {
    Write-Host "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
} else {
    Write-Host "Python $PYTHON_VERSION is already installed."
}

# Set the local Python version for the project
pyenv local $PYTHON_VERSION

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install Pipenv if not already installed
if (-not (Get-Command pipenv.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Pipenv..."
    python -m pip install --user pipenv

    # Correct the Pipenv path to Python310
    $userPipPath = "$env:APPDATA\Python\Python310\Scripts"
    
    # Add Pipenv to User Environment Variable
    if (Test-Path "$userPipPath\pipenv.exe") {
        [Environment]::SetEnvironmentVariable("Path", "$userPipPath;$([Environment]::GetEnvironmentVariable('Path', 'User'))", "User")
        
        # Update the current session's PATH
        $env:Path = "$userPipPath;$env:Path"
        
        Write-Host "Pipenv installed at $userPipPath"
    } else {
        Write-Host "Pipenv executable not found in $userPipPath. Please verify Pipenv installation."
        exit 1
    }

} else {
    Write-Host "Pipenv is already installed."
}

# Verify if Pipenv exists in the correct path
if (-not (Test-Path "$userPipPath\pipenv.exe")) {
    Write-Host "Pipenv executable not found in $userPipPath. Please verify Pipenv installation."
    exit 1
}

# Use the full path to pipenv to avoid the PATH issue
Write-Host "Installing project dependencies using Pipenv..."

Start-Process -NoNewWindow -FilePath "$userPipPath\pipenv.exe" -ArgumentList "install" -Wait

Write-Host "Setup complete! You can now use the CLI tool."