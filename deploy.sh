#!/bin/bash
set -e

# Get Virtualenv Directory Path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -z "$VIRTUAL_ENV_DIR" ]; then
    VIRTUAL_ENV_DIR="$SCRIPT_DIR/venv"
fi

if [ "$(uname)" == "MINGW64_NT-6.1" ]; then
    VIRTUAL_ENV_DIR="C:/Python27"
fi

echo "Using virtualenv located in : $VIRTUAL_ENV_DIR"

pip install -r requirements.txt

# If zip artefact already exists, back it up
if [ -f $SCRIPT_DIR/aws-scheduler.zip ]; then
    mv $SCRIPT_DIR/aws-scheduler.zip $SCRIPT_DIR/aws-scheduler.zip.backup
fi

# Add virtualenv libs in new zip file
cd $VIRTUAL_ENV_DIR/lib/site-packages
zip -r9 $SCRIPT_DIR/aws-scheduler.zip *
cd $SCRIPT_DIR

# Add python code in zip file
zip -r9 $SCRIPT_DIR/aws-scheduler.zip aws-scheduler.py
zip -r9 $SCRIPT_DIR/aws-scheduler.zip aws-scheduler.cfg 

# Run terraform apply
#terraform apply
