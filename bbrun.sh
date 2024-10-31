#!/bin/bash

# Save the current working directory
CURRENT_DIR=$PWD

# Check for the -d flag (run detached)
if [[ $1 == "-d" ]]; then
    # Activate the virtual environment
    source /home/christopher.knight/bitbarn/sandbox/code_executer/venv/bin/activate

    # Run the Python application in the background (detached) and redirect output to log
    (cd $CURRENT_DIR && nohup python3 /home/christopher.knight/bitbarn/sandbox/code_executer/src/main.py > bbrun.log 2>&1 &)

    echo "Running in detached mode. Output is redirected to bbrun.log."

    # Deactivate the virtual environment
    deactivate
else
    # Activate the virtual environment
    source /home/christopher.knight/bitbarn/sandbox/code_executer/venv/bin/activate

    # Run the Python application in the terminal (foreground)
    (cd $CURRENT_DIR && python3 /home/christopher.knight/bitbarn/sandbox/code_executer/src/main.py)

    # Deactivate the virtual environment when done
    deactivate
fi

