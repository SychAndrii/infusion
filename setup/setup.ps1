# Requires PowerShell 5.0 or higher

# Stop the script if any command fails.
$ErrorActionPreference = "Stop"

# Define the required Python version.
$PYTHON_VERSION = "3.10.6"

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

# Install dependencies for Windows (using Chocolatey if required)
if (-not (Get-Command choco.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey not found. Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Install Git if not installed
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Installing Git..."
    choco install git -y
} else {
    Write-Host "Git is already installed."
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

# Force the shell to use the correct Python version immediately
pyenv shell $PYTHON_VERSION

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install Pipenv if not already installed
if (-not (Get-Command pipenv.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Pipenv..."
    python -m pip install --user pipenv

    # Find the path to the pipenv installation dynamically
    $pipenvPath = Get-Command pipenv.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path

    if ($pipenvPath) {
        Write-Host "Pipenv installed at $pipenvPath"

        # Add Pipenv to the PATH environment variable
        [Environment]::SetEnvironmentVariable("Path", "$pipenvPath;$([Environment]::GetEnvironmentVariable('Path', 'User'))", "User")
        
        # Update the current session's PATH
        $env:Path = "$pipenvPath;$env:Path"
    } else {
        Write-Host "Pipenv executable not found after installation. Please verify Pipenv installation."
        exit 1
    }
} else {
    Write-Host "Pipenv is already installed."
}

# Verify if Pipenv exists
$pipenvPath = Get-Command pipenv.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path

if (-not $pipenvPath) {
    Write-Host "Pipenv executable not found. Please verify Pipenv installation."
    exit 1
}

# Check if a virtual environment already exists, and remove it if so
$pipenvVenv = pipenv --venv 2>&1
if ($pipenvVenv -and $pipenvVenv -notlike "*No virtualenv has been created*") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force $pipenvVenv
} else {
    Write-Host "No existing virtual environment found."
}

# Use the full path to pipenv to avoid the PATH issue
Write-Host "Installing project dependencies using Pipenv with Python $PYTHON_VERSION..."

Start-Process -NoNewWindow -FilePath $pipenvPath -ArgumentList "--python", "$(pyenv which python)", "install" -Wait

Write-Host "Setup complete! You can now use the CLI tool."