#!/bin/sh

datalad clone https://github.com/OpenNeuroDatasets/ds001226.git
cd ds001226/ || { echo "Failure"; exit 1; }
datalad get .
