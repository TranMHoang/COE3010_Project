#!/bin/bash -l
# created: Feb 14, 2020 2:22 PM
# author: minhhoan
#SBATCH --job-name=DAMASK_array
#SBATCH --account=project_2008630
#SBATCH --partition=medium
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=64
#SBATCH --hint=multithread
#SBATCH --mail-type=NONE
#SBATCH --mail-user=tran.minhhoang@aalto.fi
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo '=== Reading config.txt ==='
module load python-data
# Compatibility reasons
dos2unix config.txt
# Read config file
file="config.txt"
# Record which material and load case to run
declare -a materials
declare -a loadcases
declare -a geometries
N=0
while IFS= read -r line
do
    if [[ ${line:0:1} != "#" ]]
    then
        IFS=' ' read -a temp <<< "$line"
        for loadcase in "${temp[@]:1}"
        do
            # Save a combination of load case and material onto arrays
            N=$((N+1))
            materials+=("${temp[0]}")
            # Make sure load case name works whether if .yaml extension is there
            if [ ${loadcase:(-5)} != ".yaml" ]
            then
                loadcase=("${loadcase}.yaml")
            fi
            loadcases+=("${loadcase}")
            # Find the geometry .vti file in material directory
            dir="./materials/${temp[0]}/"
            file="$(find $dir -type f -name '*.vti')"
            geometry=("${file#"$dir"}")
            geometries+=("${geometry}")
            # Create folders in simulations and copy needed files
            rm -rf "./simulations/${temp[0]}_${loadcase:0:(-5)}"
            mkdir "./simulations/${temp[0]}_${loadcase:0:(-5)}"
            cp "./materials/${temp[0]}/material.yaml" "./simulations/${temp[0]}_${loadcase:0:(-5)}/material.yaml"
            cp "./materials/${temp[0]}/numerics.yaml" "./simulations/${temp[0]}_${loadcase:0:(-5)}/numerics.yaml"
            cp "./materials/${temp[0]}/${geometry}" "./simulations/${temp[0]}_${loadcase:0:(-5)}/${geometry}"
            cp "./loadcases/${loadcase}" "./simulations/${temp[0]}_${loadcase:0:(-5)}/${loadcase}"
            cp "./damask-grid.sif" "./simulations/${temp[0]}_${loadcase:0:(-5)}/damask-grid_${N}.sif"
        done
    fi
done < $file
export project_dir=$PWD
echo "=== Submitting ${N} jobs ==="
# export SING_IMAGE=damask-grid.sif
for ((n=0; n<$N; n++))
do
    mat=("${materials[n]}")
    load=("${loadcases[n]}")
    geom=("${geometries[n]}")
    path=("./simulations/${mat}_${load:0:(-5)}")
    echo "=== Running simulation for ${mat} and load ${load} ==="
    srun pipeline_internal.sh $mat $load $geom $path $n
    #cd "${project_dir}/${path:2}"
    #srun apptainer run -B "${PWD}:${PWD}, /tmp" damask-grid.sif --load "${PWD}/${load}" --geom "${PWD}/${geom}" > "slurm_${geom}_${load:0:(-5)}.out" &
    #srun apptainer_wrapper run --env OMP_NUM_THREADS=${OMP_NUM_THREADS} DAMASK_grid --load "${loadcases[n]}" --geom "${geometries[n]}" > "slurm_${geometries[n]}_${loadcases[n]:0:(-5)}.out"
done
wait
for ((n=0; n<$N; n++))
do
    mat=("${materials[n]}")
    load=("${loadcases[n]}")
    geom=("${geometries[n]}")
    path=("./simulations/${mat}_${load:0:(-5)}")
    python3 postprocessing.py -f "${path}/${geom::(-4)}_${load::(-5)}.hdf5" > "${path}/slurm_${geom}_${load:0:(-5)}_py.out"
done
echo "Finished submitting"