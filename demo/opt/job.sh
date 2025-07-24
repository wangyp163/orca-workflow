#!/bin/bash
#SBATCH --job-name=wyp.xyz
#SBATCH --ntasks-per-node=16
#SBATCH --output=%j.log
#SBATCH --partition=sdicnormal

# load the environment
module purge
source /public/home/wangyp3_/apprepo/orca/orca-6.1.0-f.0_linux_x86-64/env.sh
/public/home/wangyp3_/apprepo/orca/orca-6.1.0-f.0_linux_x86-64/bin/orca test_water.inp > test_water.out
