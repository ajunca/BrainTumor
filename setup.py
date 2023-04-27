#############################################################################
# Setup file
# by Albert Juncà Sabrià
#############################################################################

import csv
import os
from subjects import *

# Some config parameters
data_root_path = "data/TVB_brain_tumor/"
data_subjects_path = data_root_path + "derivatives/TVB/"
data_subjects_tsv_path = data_root_path + "derivatives/TVB/participants.tsv"

# List of subjects metadata
subjects_meta = []

# Subjects SC [pre-operational, post-operational] indexed by subject's id.
# IMPORTANT: Only SOME subjects have post-operational SC
subjects_sc = dict()

# Subjects BOLD time series [pre-operational, post-operational] indexed by subject's id.
subjects_ts = dict()

# Parcellation data
#parcellation = []


# Read and store subjects metadata. We are not interested in all, so we just store a subset of all.
# Full layout: ['participant_id', ' sex', ' age', 'tumor type & grade', 'tumor size (cub cm)', 'tumor location',
#               'fmri TR', 'handedness', 'height (cm)', 'weight (kg)', 'STAI', 'PSWQ', 'ERQ reappraisal',
#               'ERQ suppression','ERQ processing', 'ERQ expression', 'Loneliness', 'Marital status',
#               'Education level (1-9)', 'Employment', 'Sport frequency/week', 'Smoking', 'Cafeine index',
#               'Alcohol index current', 'Alcohol index lifetime', 'MOT_latency_mean', 'MOT_latency_md',
#               'MOT_error_mean', 'RTI_simple_accuracy', 'RTI_simpleRT_mean', 'RTI_simpleRT_md', 'RTI_simpleRT_sd',
#               'RTI_simpleMT_mean', 'RTI_simpleMT_md', 'RTI_simpleMT_sd', 'RTI_five_accuracy', 'RTI_fiveMT',
#               'RTI_fiveRT', 'RTI_fiveRT_sd', 'RTI_fiveMT_mean', 'RTI_fiveMT_md', 'RTI_fiveMT_sd', 'RVP_A',
#               'RVP_probhit', 'RVP_falsealarms', 'RVP_latancy_mean', 'RVP_latency_md', 'SOC_prob_minmoves',
#               'SOC_meanmoves2', 'SOC_meanmoves3', 'SOC_meanmoves4', 'SOC_meanmoves5', 'SSP_spanlength']
# We are just interested at the moment in: ['participant_id', 'fmri TR', 'tumor type & grade', 'tumor size (cub cm)']
with open(data_subjects_tsv_path, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    # Skip tsv header
    next(reader)
    for row in reader:
        sub = SubjectMeta(row[0], float(row[6]), row[3], float(row[4]))
        subjects_meta.append(sub)


# Read SC Matrices and BOLD time series for each subject (Pre and Post operational).
# Note that post operational data is only available for SOME subjects
for sub in subjects_meta:
    # Read SC Values
    preop_sc_zip_filename = data_subjects_path + sub.sub_id + '/ses-preop/SC.zip'
    postop_sc_zip_filename = data_subjects_path + sub.sub_id + '/ses-postop/SC.zip'
    preop_roits_filename = data_subjects_path + sub.sub_id + '/ses-preop/ROIts.dat'
    postop_roits_filename = data_subjects_path + sub.sub_id + '/ses-postop/ROIts.dat'

    has_postop_data = os.path.exists(postop_sc_zip_filename)

    # Every subject has pre-operational data
    preop_sc = SC(preop_sc_zip_filename)
    postop_sc = None
    preop_ts = TS(preop_roits_filename)
    postop_ts = None

    # Only some have post-operational data
    if has_postop_data:
        postop_sc = SC(postop_sc_zip_filename)
        postop_ts = TS(postop_roits_filename)

    # Store SC matrices
    subjects_sc[sub.sub_id] = [preop_sc, postop_sc]
    # Store BOLD time series
    subjects_ts[sub.sub_id] = [preop_ts, postop_ts]


print("************************* Subjects Info *************************")
pretty_print_subjects(subjects_meta)
print("*****************************************************************")