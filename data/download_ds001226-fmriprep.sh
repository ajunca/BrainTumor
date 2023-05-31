#!/bin/sh

datalad install https://github.com/OpenNeuroDerivatives/ds001226-fmriprep.git
cd ds001226-fmriprep || { echo "Failure"; exit 1; }
git annex get .
