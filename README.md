WARNING: RE-RUNNING SIMULATIONS DELETE PREVIOUS SIMULATION DIRECTORIES. MOVE 
.HDF5 FILES TO ANOTHER DIRECTORY BEFORE HAND, AND CHECK CONFIGURATION CAREFULLY.

This project is a pipeline for running multiple DAMASK simulations using the Mahti
supercomputer. The project aims to run several simulations efficiently, automate
post-processing, and simplifies file input-output. This only works with DAMASK version
3.0.0-alpha7.

Config file in syntax:

<Material 1> <load case 1> <load case 2> ...

<Material 2> <load case 3> <load case 4> ...

...

Accept load cases with and without .yaml file extension. Example:

QP1000_DP linear_tensionX.yaml linear_tensionY.yaml tension_relax_cycle

To run DAMASK simulations:

    1.  Make sure that damask-grid.sif is in the working directory. If not, build
        a damask image following https://docs.csc.fi/computing/containers/creating/.
        Use docker://eisenforschung/damask-grid:<version>.
        Note that the current latest version may not be the one used in this
        project, 3.0.0-alpha7
        
    2.  Check and edit config.txt. Make sure that config.txt is in the working
        directory.
        
    3.  Add materials and load cases to corresponding folder.
    
    4.  Edit partition and time in pipeline.sh. Recommended partition is
        medium. Time should be ~ 10 minutes per 100 increments
        
    5.  Open terminal in the working directory and submit job with
        sbatch pipeline.sh
        
Note: due to specific interactions between damask writing to folders, Lustre file
system, Apptainer container system, and slurm, the simulations are currently NOT
parallel.
