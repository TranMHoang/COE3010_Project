#!/bin/bash
# arguments: material, load, geometry, path from current project directory
# to simulation directory
mat="${1}"; load="${2}"; geom="${3}"; path="${4}"; n=$((${5}));
cd "${project_dir}/${path:2}"
#apptainer_wrapper run DAMASK_grid --load "${load}" --geom "${geom}"
apptainer run --pwd "/wd" --env OMP_NUM_THREADS=${OMP_NUM_THREADS} -B "${PWD}:/wd, /tmp" "damask-grid_$((${n}+1)).sif" --load "${load}" --geom "${geom}" > "slurm_${geom}_${load:0:(-5)}.out"