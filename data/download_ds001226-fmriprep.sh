#!/bin/sh

datalad clone https://github.com/OpenNeuroDerivatives/ds001226-fmriprep.git
mkdir ds001226-fmriprep
cd ds001226-fmriprep || { echo "Failure"; exit 1; }
datalad get .
