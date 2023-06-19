import os
import sys
from BrainTumor.subjects import *

os.chdir('..')

data_dir = "data"

subjects = Subjects()
subjects.initialize(data_dir)

print("************************* Subjects Info *************************")
subjects.pretty_print()
print("*****************************************************************")