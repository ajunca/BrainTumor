#############################################################################
# Setup file
# by Albert Juncà Sabrià
#############################################################################


import os
from subjects import *

# Some config parameters
data_root_path = "data/TVB_brain_tumor/"
data_subjects_path = data_root_path + "derivatives/TVB/"

# Initialize subjects (metadata and data)
subjects = Subjects()
subjects.initialize(data_subjects_path)

print("************************* Subjects Info *************************")
subjects.pretty_print()
print("*****************************************************************")