batch_my_test.sh -> runs my_test.sh
batch_my_experiment.sh -> runs my_run.sh
my_run.sh -> RUNS OUR PROGRAM


-------------------------------------------------

separate SLURM from python 
use apptainer to make environment stable -- this is why we have a sif file
use scratch/storage paths carefully  -- need to define vars and then bind them to an apptainer 
test -- seperate testing scripts 



NEED TO: 

In batch_my_experiment.sh
    Change:
    job name
    memory
    time
    email
    maybe GPU count

    + make the scripts executables 


ask jess: 

- export APPTAINER_CACHEDIR=$CACHEDIR/cache ??? -- buiilding app , stroing cache files 
all i need is the batch zt llm 
test file 





