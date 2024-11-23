#!/bin/bash

# Load paths from config.ini
CONFIG_FILE="$HOME/.python_executor/config.ini"

# Function to load config values
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        VENV_PATH=$(grep -oP '(?<=^VENV_PATH=).*' "$CONFIG_FILE")
        SOURCE_PATH=$(grep -oP '(?<=^SOURCE_PATH=).*' "$CONFIG_FILE")
    else
        echo "Config file not found at $CONFIG_FILE"
        exit 1
    fi
}

# Load configuration
load_config

# Define the base directory for execution (current working directory)
EXECUTION_BASE="$(pwd)"

# Path to the bbrun requirements file
BBRUN_REQUIREMENTS="$HOME/skulley/bbrun/requirements.txt"

# Function to display help information
display_help() {
    echo "Usage: bbrun [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message and exit."
    echo "  -rebuild          Rebuild the virtual environment, removing any existing one."
    echo "  -d                Run the Python application in detached mode."
    echo ""
    echo "This script manages a Python virtual environment and runs a Python application."
    echo "If the -d option is provided, the script will run the application in the background"
    echo "and log output to bbrun.log."
    echo ""
}

# Function to create or rebuild the virtual environment
setup_virtualenv() {
    if [[ -d "$VENV_PATH" ]]; then
        echo "Virtual environment already exists."
        if [[ "$1" == "-rebuild" ]]; then
            echo "Rebuilding the virtual environment..."
            rm -rf "$VENV_PATH"
        else
            echo "Using existing virtual environment."
            return
        fi
    fi

    echo "Creating virtual environment in $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip  # Upgrade pip in the new environment

    # Use the bbrun requirements file
    pip install -r "$BBRUN_REQUIREMENTS"
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
    source "$VENV_PATH/bin/activate"

    # Run the Python application in the background (detached) and redirect output to log
    (cd "$EXECUTION_BASE" && nohup python3 "$SOURCE_PATH" > "$EXECUTION_BASE/bbrun.log" 2>&1 &)

    echo "Running in detached mode. Output is redirected to bbrun.log."

    # No need to deactivate here, as we are in a subshell
else
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"

    # Run the Python application in the terminal (foreground)
    (cd "$EXECUTION_BASE" && python3 "$SOURCE_PATH")

    # Deactivate the virtual environment when done
    deactivate
fi
