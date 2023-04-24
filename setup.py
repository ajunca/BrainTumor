#############################################################################
# Setup file
# by Albert Juncà Sabrià
#############################################################################

import csv

data_root_path = "data/TVB_brain_tumor/"
data_subjects_path = data_root_path + "derivatives/TVB"
data_subjects_tsv_path = data_root_path + "derivatives/TVB/participants.tsv"

# Read and store subjects data. We are not interested in all, so we just store a subset of all.
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
# We are just interested in: ['participant_id', 'fmri TR', 'tumor type & grade', 'tumor size (cub cm)']
class Subject:
    def __init__(self, sub_id, fmri_tr, tumor_type_and_grade, tumor_size):
        self.sub_id = sub_id
        self.fmri_tr = fmri_tr
        self.tumor_type_and_grade = tumor_type_and_grade
        self.tumor_size = tumor_size

    def to_string(self):
        return "ID: " + self.sub_id + ", fMRI_TR: " + str(self.fmri_tr) + "ms, Tumor Type & Grade: " \
            + self.tumor_type_and_grade + ", Tumor Size: " + str(self.tumor_size) + "cm³"

# Read subjects
subjects = []
with open(data_subjects_tsv_path, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    # Skip tsv header
    next(reader)
    for row in reader:
        sub = Subject(row[0], float(row[6]), row[3], float(row[4]))
        subjects.append(sub)

print("************************* Subjects Info *************************")
for i in subjects:
    print(i.to_string())
print("*****************************************************************")