from BrainTumor.subjects import Subjects
from BrainTumor.ignition_utils import *

data_dir = "../../data"

subjects = Subjects()
subjects.initialize(data_dir)

control_subset = subjects.get_control_subset()
tumor_subset = subjects.get_tumor_subset()

ignitions = compute_ignitions(subjects)
mean_control_ignition = compute_mean_ignition(control_subset, ignitions)
tumor_subjects_delta_ignitions = compute_delta_ignitions(
    mean_control_ignition,
    ignitions,
    tumor_subset
)

print("************************* Subjects Info *************************")
subjects.pretty_print()
print("*****************************************************************")