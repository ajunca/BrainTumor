import zipfile
import numpy as np


# Subjects Metadata
class SubjectMeta:
    def __init__(self, sub_id, fmri_tr, tumor_type_and_grade, tumor_size):
        self.sub_id = sub_id  # String
        self.fmri_tr = fmri_tr  # Float in ms
        self.tumor_type_and_grade = tumor_type_and_grade  # String
        self.tumor_size = tumor_size  # Float in cm³

    def is_control(self):
        return 'CON' in self.sub_id


# Structural Connectivity Data
class SC:
    weights = None  # 68*68 numpy float matrix
    centres = None  # List consisting of region centers (68). Format: [region_name, x, y, z]

    def __init__(self, zip_filename=None):
        if zip_filename is not None:
            self.read_sc_data(zip_filename)

    def read_sc_data(self, zip_filename):
        with zipfile.ZipFile(zip_filename, 'r') as zip_file:
            # Read weights
            with zip_file.open('weights.txt') as weights_file:
                contents_str = weights_file.read().decode('utf-8')
                rows = contents_str.strip().split('\n')
                data = [row.strip().split(' ') for row in rows]
                self.weights = np.array(data, dtype=float)
            # Read centres
            with zip_file.open('centres.txt') as centres_file:
                contents_str = centres_file.read().decode('utf-8')
                rows = contents_str.strip().split('\n')
                self.centres = []
                for row in rows:
                    region, x, y, z = row.strip().split('\t')
                    self.centres.append([region, float(x), float(y), float(z)])
                assert len(self.centres) == 68


class TS:
    data = None

    def __init__(self, roits_filename=None):
        if roits_filename:
            with open(roits_filename, 'r') as file:
                lines = file.readlines()
                self.data = []
                for line in lines:
                    values = line.split()
                    entry = np.array([float(v) for v in values])
                    print(len(entry))
                    #assert len(entry) == 68
                    self.data.append(entry)


# Class storing all related Matlab data
class FcMat:
    def __init__(self):


def pretty_print_subjects(subjects):
    print('{:<15} {:<15} {:<30} {:<15}'.format(
        'ID', 'FMRI_TR (ms)', 'TYPE', 'VOLUME (cm³)',
    ))
    for sub in subjects:
        print('{:<15} {:<15} {:<30} {:<15}'.format(
            sub.sub_id, str(sub.fmri_tr), sub.tumor_type_and_grade, str(sub.tumor_size),
        ))
