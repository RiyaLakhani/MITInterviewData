#!/bin/bash

# put Hugging Face cache somewhere with space
export HF_HOME=/scratch/zt1/project/mcukier-prj/shared/models
export HF_HUB_OFFLINE=1

# activate python environment inside container if needed
. /opt/venv/bin/activate

# make output folder
mkdir -p travail_output
mkdir -p results

echo "inside run script"
pwd
ls

python3 ./llm_experiments.py

#empty line
