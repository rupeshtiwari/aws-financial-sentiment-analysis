#!/bin/bash

# create the virtual environment
python3 -m venv .venv
# Install into the virtual environment
source .venv/bin/activate
# download requirements
.venv/bin/python -m pip install -r requirements.txt --upgrade pip
# download other requirements
# .venv/bin/python -m pip install --target stacks/smep/ -r stacks/smep/requirements.txt
# create cfn
cdk synth