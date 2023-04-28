#############################################################################
# Setup file
# by Albert Juncà Sabrià
#############################################################################


# Some config parameters
data_root_path = "data/TVB_brain_tumor/"
data_subjects_path = data_root_path + "derivatives/TVB/"

# Configure BOLD filters
import WholeBrain.BOLDFilters as filters
apply_bold_filters = False
filters.k = 2
filters.flp = .008
filters.fhi = .08
# Note for filters.TR: Data has different fMRI TR values for different subjects (2100 and 2400ms),
# we will define it for each user when used


# Initialize subjects (metadata and data)
from subjects import *
subjects = Subjects()
subjects.initialize(data_subjects_path)

print("************************* Subjects Info *************************")
subjects.pretty_print()
print("*****************************************************************")