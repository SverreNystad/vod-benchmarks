#!/bin/sh
#SBATCH --account=share-ie-idi
#SBATCH --job-name="test-slurm-job"
#SBATCH --time=06:00:00
#SBATCH --partition=CPUQ
#SBATCH --nodes=1
#SBATCH --output=slurm_outputs/output_simple.txt
#SBATCH --error=slurm_outputs/output_simple.err
#SBATCH --mail-user=sverrnys@ntnu.no
#SBATCH --mail-type=ALL


WORKDIR=${SLURM_SUBMIT_DIR}
cd ${WORKDIR}
echo "Running from this directory: $SLURM_SUBMIT_DIR"
echo "Name of job: $SLURM_JOB_NAME"
echo "ID of job: $SLURM_JOB_ID"
echo "The job was run on these nodes: $SLURM_JOB_NODELIST"

ENV_PATH="/cluster/work/$(whoami)/master/vod-benchmarks/conda-env/"

module purge
module load Anaconda3/2024.02-1

# Create a new Conda environment
conda create -y --prefix ${ENV_PATH} python=3.11

# Activate the environment
conda activate ${ENV_PATH}
pip install -r requirements.txt

echo "Downloaded dependencies:"
pip freeze


# Run the Python script
python -m awscliv2 s3 sync --no-sign-request s3://pohang-canal-dataset/ ./pohang-canal-dataset

# Deactivate the environment
conda deactivate

echo "Job finished"