#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the required Python version.
PYTHON_VERSION="3.10.6"
PIPENV_PATH="$HOME/.local/bin"

echo "Starting setup..."

# Function to install Pyenv
install_pyenv() {
    echo "Installing Pyenv..."

    # Check if the .pyenv directory already exists
    if [ -d "$HOME/.pyenv" ]; then
        echo "Pyenv directory already exists at $HOME/.pyenv. Skipping installation."
    else
        # Install Pyenv via Git
        git clone https://github.com/pyenv/pyenv.git ~/.pyenv

        # Add Pyenv to the shell configuration file to initialize it on startup
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Use .bashrc for Linux
            echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
            echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
            echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
            echo 'eval "$(pyenv init -)"' >> ~/.bashrc

            # Immediately source the .bashrc to make pyenv available in the current session
            export PYENV_ROOT="$HOME/.pyenv"
            export PATH="$PYENV_ROOT/bin:$PATH"
            eval "$(pyenv init --path)"
            eval "$(pyenv init -)"
        fi
    fi
}

# Install dependencies for Linux (Ubuntu/Debian)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing dependencies for Pyenv..."
    sudo apt-get update
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev git
fi

# Install Git if not installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Installing Git..."
    sudo apt-get install -y git
else
    echo "Git is already installed."
fi

# Check if Pyenv is installed
if ! command -v pyenv &> /dev/null; then
    install_pyenv
else
    echo "Pyenv is already installed."
fi

# Initialize Pyenv in this script session
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Install the required Python version using Pyenv
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
else
    echo "Python $PYTHON_VERSION is already installed."
fi

# Set the local Python version for the project
pyenv local $PYTHON_VERSION

# **Force the shell to use the correct Python version immediately**
pyenv shell $PYTHON_VERSION

# Ensure pip is using the correct Python version
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Pipenv if not already installed
if ! command -v pipenv &> /dev/null; then
    echo "Installing Pipenv..."
    python -m pip install --user pipenv

    # Add Pipenv to User Environment Variable
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

    # Export the path for the current session
    export PATH="$HOME/.local/bin:$PATH"
    
    echo "Pipenv installed at $PIPENV_PATH"
else
    echo "Pipenv is already installed."
fi

# Verify if Pipenv exists in the correct path
if [ ! -f "$PIPENV_PATH/pipenv" ]; then
    echo "Pipenv executable not found in $PIPENV_PATH. Please verify Pipenv installation."
    exit 1
fi

# Check if a virtual environment already exists, and remove it if so
if pipenv --venv &> /dev/null; then
    echo "Removing existing virtual environment..."
    rm -rf "$(pipenv --venv)"
else
    echo "No existing virtual environment found."
fi

# Use the full path to pipenv to avoid the PATH issue
echo "Installing project dependencies using Pipenv with Python $PYTHON_VERSION..."

"$PIPENV_PATH/pipenv" --python "$PYENV_ROOT/versions/$PYTHON_VERSION/bin/python" install

echo "Setup complete! You can now use the CLI tool."