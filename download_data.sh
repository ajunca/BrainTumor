#!/bin/sh

cd data/ || { echo "Failure"; exit 1; }

# Download ds001226
./download_ds001226.sh

# Download ds001226-fmriprep
./download_ds001226-fmriprep.sh
