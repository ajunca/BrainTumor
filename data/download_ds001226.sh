#!/bin/sh

# This mode has no derivative folder...
#datalad clone https://github.com/OpenNeuroDatasets/ds001226.git
#cd ds001226/ || { echo "Failure"; exit 1; }
#datalad get .

# From s3 there is derivative folder but it is not complete...
#aws s3 sync --no-sign-request s3://openneuro.org/ds001226 ds001226/

# Script method seems to be ok...
mkdir ds001226
cd ds001226/ || { echo "Failure"; exit 1; }
../ds001226-5.0.0.sh
