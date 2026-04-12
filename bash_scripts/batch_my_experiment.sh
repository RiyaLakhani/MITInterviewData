#!/bin/bash
#SBATCH --job-name=my_run3
#SBATCH --output=/scratch/zt1/project/mcukier-prj/user/rlakhan3/output/%j_%x.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rlakhan3@umd.edu

mystoredir=/scratch/zt1/project/mcukier-prj
myworkdir=/scratch/zt1/project/mcukier-prj/user/rlakhan3
apptainer_bin=/cvmfs/hpcsw.umd.edu/apptainer/1.3.6/x86_64/bin/apptainer

mkdir -p "$myworkdir/output"
cd "$myworkdir" || exit 1

export HOME="$myworkdir"
export APPTAINER_NO_HOME=1

echo "PWD=$PWD"
echo "PATH=$PATH"
echo "APPTAINER=$apptainer_bin"
"$apptainer_bin" --version
ls -l "$myworkdir"

srun "$apptainer_bin" exec --no-home -e --nv \
    --bind "$mystoredir" \
    --pwd "$myworkdir" \
    "$mystoredir/shared/sifs/travail_base5.sif" \
    /bin/bash ./my_run.sh
