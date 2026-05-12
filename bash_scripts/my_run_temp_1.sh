#!/bin/bash

export HF_HOME=/scratch/zt1/project/mcukier-prj/shared/models
export HF_HUB_OFFLINE=1

. /opt/venv/bin/activate

mkdir -p travail_output
mkdir -p results

echo "inside run script for temperature 1"
pwd
ls

python3 ./llm_experiments.py --config ./config_temp_1.json

#empty line