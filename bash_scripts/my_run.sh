#!/bin/bash

# put Hugging Face cache somewhere with space
export HF_HOME=/scratch/zt1/project/mcukier-prj/shared/models
export HF_HUB_OFFLINE=1

# activate python environment inside container if needed
. /opt/venv/bin/activate

# make output folder
mkdir -p travail_output
mkdir -p results

# run your code
python3 /Users/riyalakhani/MITInterviewData/llm_experiments.py