#!/bin/bash

# Save the current working directory
CURRENT_DIR=$PWD
VENV_DIR="venv"

# Function to display help information
display_help() {
    echo "Usage: ./bbrun.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message and exit."
    echo "  -rebuild          Rebuild the virtual environment, removing any existing one."
    echo "  -d                Run the Python application in detached mode."
    echo ""
    echo "This script manages a Python virtual environment and runs a Python application."
    echo "It will create a virtual environment if it does not exist, install the required"
    echo "packages listed in requirements.txt, and then execute the application."
    echo ""
    echo "If the -d option is provided, the script will run the application in the background"
    echo "and log output to bbrun.log."
    echo ""
    echo "If the -rebuild option is specified, any existing virtual environment will be removed"
    echo "and a new one will be created, ensuring that you start with a clean environment."
    echo ""
    echo "Examples:"
    echo "  ./bbrun.sh              # Run the application with the existing virtual environment."
    echo "  ./bbrun.sh -rebuild     # Rebuild the virtual environment and run the application."
    echo "  ./bbrun.sh -d           # Run the application in detached mode."
    echo "  ./bbrun.sh -rebuild -d  # Rebuild and run the application in detached mode."
}

# Function to create or rebuild the virtual environment
setup_virtualenv() {
    if [[ -d "$VENV_DIR" ]]; then
        echo "Virtual environment already exists."
        if [[ "$1" == "-rebuild" ]]; then
            echo "Rebuilding the virtual environment..."
            rm -rf "$VENV_DIR"
        else
            echo "Using existing virtual environment."
            return
        fi
    fi

    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip  # Upgrade pip in the new environment
    pip install -r requirements.txt
}

# Check for options
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    display_help
    exit 0
fi

# Check for the -rebuild flag
if [[ "$1" == "-rebuild" ]]; then
    setup_virtualenv -rebuild
else
    setup_virtualenv
fi

# Check for the -d flag (run detached)
if [[ "$2" == "-d" ]]; then
    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"

    # Run the Python application in the background (detached) and redirect output to log
    (cd "$CURRENT_DIR" && nohup python3 src/main.py > bbrun.log 2>&1 &)

    echo "Running in detached mode. Output is redirected to bbrun.log."

    # No need to deactivate here, as we are in a subshell
else
    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"

    # Run the Python application in the terminal (foreground)
    (cd "$CURRENT_DIR" && python3 src/main.py)

    # Deactivate the virtual environment when done
    deactivate
fi
