from BrainTumor.subjects import Subjects
from BrainTumor.metastability_utils import *
from WholeBrain.Observables.metastability import MetastabilityResult

data_dir = "../../data"

subjects = Subjects()
subjects.initialize(data_dir)

metastabilities = compute_metastability(subjects)

# Compute metastability mean for control subjects
control_subjects_mean_metastability = np.mean([m.metastability for m in subjects.get_control_subset().keep_only_from_this_set(metastabilities).values()])

