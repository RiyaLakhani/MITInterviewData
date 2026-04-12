#!/bin/bash
#SBATCH --job-name=my_llm_job
#SBATCH --output=output/%j_%x.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rlakhan3@umd.edu

mystoredir=/scratch/zt1/project/mcukier-prj
myworkdir=/scratch/zt1/project/mcukier-prj/user/$USER

[ -d $myworkdir ] || mkdir -p $myworkdir
cd $myworkdir

module load apptainer

srun apptainer exec -e --nv \
    --bind $mystoredir \
    --pwd $myworkdir \
    $mystoredir/shared/sifs/travail_base5.sif \
   bash_scripts/my_run.sh