#!/bin/bash
#SBATCH -p ai_training
#SBATCH -w dx-ai-node7
#SBATCH --cpus-per-task=1
#SBATCH --job-name=case_viewer
#SBATCH -o /dev/null
#SBATCH -e /dev/null
set -e
eval "$(conda shell.bash hook)"
conda activate evalscope
timestamp=$(date "+%Y-%m-%d_%H-%M-%S")

output_folder="/mnt/lustre/houbingxi/1212_moe_eval_badcase/case_viewer/logs"
log_file="${output_folder}/${timestamp}_evaluate.log"
exec &> $log_file

cd /mnt/lustre/houbingxi/1212_moe_eval_badcase/case_viewer
streamlit run  main.py --server.port 8501 

