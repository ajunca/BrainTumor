import zipfile
import numpy as np
from scipy.io import loadmat
import csv
import multiprocessing as mp


# Structural Connectivity Data
class StructuralCon:
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


class SubjectMeta:
    def __init__(self, sub_id, sub_dir_path, fmri_tr, tumor_type_and_grade, tumor_size):
        self.sub_id = sub_id  # String
        self.dir_path = sub_dir_path  # String
        self.fmri_tr = fmri_tr  # Float in ms
        self.tumor_type_and_grade = tumor_type_and_grade  # String
        self.tumor_size = tumor_size  # Float in cm³


class SubjectData:
    def __init__(self, sc_dk68, ts, ts_dk68):
        self.sc_dk68 = sc_dk68
        self.ts = ts
        self.ts_dk68 = ts_dk68


class Subject:
    def __init__(self):
        self.meta = None
        self.preop_data = None
        self.postop_data = None

    def initialize(self,
                   sub_id,
                   fmri_tr,
                   tumor_type_and_grade,
                   tumor_size,
                   sub_folder_path):
        # Create subjects metadata
        self.meta = SubjectMeta(sub_id, sub_folder_path, fmri_tr, tumor_type_and_grade, tumor_size)
        self._init_preop_data()
        # TODO: Initialize postop data?

    # Return subject id
    def get_id(self):
        return None if not self.meta else self.meta.sub_id

    def get_fmri_tr(self):
        return self.meta.fmri_tr

    def get_tumor_type_and_grade(self):
        return self.meta.tumor_type_and_grade

    def get_tumor_size(self):
        return self.meta.tumor_size

    def is_control(self):
        return 'CON' in self.meta.sub_id

    def get_dir_path(self):
        return self.meta.dir_path

    def _init_preop_data(self):
        sc_dk68 = StructuralCon(zip_filename=self.meta.dir_path + 'ses-preop/SC.zip')
        mat_contents = loadmat(self.meta.dir_path + 'ses-preop/FC.mat')
        self.preop_data = SubjectData(
            sc_dk68,
            np.transpose(mat_contents['' + self.meta.sub_id + 'T1_ROIts']),
            np.transpose(mat_contents['' + self.meta.sub_id + 'T1_ROIts_DK68'])
        )

class Subjects:

    def __init__(self):
        self.data = dict()

    def initialize(self, data_subjects_path):
        # Read and store subjects metadata. We are not interested in all, so we just store a subset of all. Full
        # layout: [
        #   'participant_id', ' sex', ' age', 'tumor type & grade', 'tumor size (cub cm)', 'tumor location',
        #   'fmri TR', 'handedness', 'height (cm)', 'weight (kg)', 'STAI', 'PSWQ', 'ERQ reappraisal',
        #   'ERQ suppression','ERQ processing', 'ERQ expression', 'Loneliness', 'Marital status', 'Education level (
        #   1-9)', 'Employment', 'Sport frequency/week', 'Smoking', 'Cafeine index', 'Alcohol index current',
        #   'Alcohol index lifetime', 'MOT_latency_mean', 'MOT_latency_md', 'MOT_error_mean', 'RTI_simple_accuracy',
        #   'RTI_simpleRT_mean', 'RTI_simpleRT_md', 'RTI_simpleRT_sd', 'RTI_simpleMT_mean', 'RTI_simpleMT_md',
        #   'RTI_simpleMT_sd', 'RTI_five_accuracy', 'RTI_fiveMT', 'RTI_fiveRT', 'RTI_fiveRT_sd', 'RTI_fiveMT_mean',
        #   'RTI_fiveMT_md', 'RTI_fiveMT_sd', 'RVP_A', 'RVP_probhit', 'RVP_falsealarms', 'RVP_latancy_mean',
        #   'RVP_latency_md', 'SOC_prob_minmoves', 'SOC_meanmoves2', 'SOC_meanmoves3', 'SOC_meanmoves4',
        #   'SOC_meanmoves5', 'SSP_spanlength'
        # ]
        # We are just interested at the moment in:
        #   ['participant_id', 'fmri TR', 'tumor type & grade', 'tumor size (cub cm)']
        with open(data_subjects_path + 'participants.tsv', 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            # Skip tsv header
            next(reader)
            for row in reader:
                sub_id = row[0][4:]
                fmri_tr = float(row[6])
                tumor_type_and_grade = row[3]
                tumor_size = float(row[4])
                sub_dir_path = data_subjects_path + row[0] + '/'
                # Create and initialize subject
                sub = Subject()
                sub.initialize(sub_id, fmri_tr, tumor_type_and_grade, tumor_size, sub_dir_path)
                # Store the subject
                self.data[sub_id] = sub

    def pretty_print(self):
        print('{:<15} {:<15} {:<30} {:<15}'.format(
            'ID', 'FMRI_TR (ms)', 'TYPE', 'VOLUME (cm³)',
        ))
        for sub in self.data.values():
            print('{:<15} {:<15} {:<30} {:<15}'.format(
                sub.meta.sub_id, str(sub.meta.fmri_tr), sub.meta.tumor_type_and_grade, str(sub.meta.tumor_size),
            ))

    def for_each(self, func):
        for sub in self.data.values():
            func(sub)

    def get_subject_by_id(self, sub_id):
        return self.data[sub_id]

    def filter_preop_ts_dk68(self):
        result = dict()
        for sub in self.data.values():
            result[sub.get_id()] = sub.preop_data.ts_dk68.copy()
        return result

    def filter_subjects(self, sub_filter):
        result = Subjects()
        for k, v in self.data.items():
            if sub_filter(v):
                result.data[k] = v
        return result

# class TS:
#     data = None
#
#     def __init__(self, roits_filename=None):
#         if roits_filename:
#             with open(roits_filename, 'r') as file:
#                 lines = file.readlines()
#                 self.data = []
#                 for line in lines:
#                     values = line.split()
#                     entry = np.array([float(v) for v in values])
#                     print(len(entry))
#                     #assert len(entry) == 68
#                     self.data.append(entry)