import zipfile
import numpy as np
from scipy.io import loadmat
import os
import pandas as pd


class SubjectsPaths:
    def __init__(self, sub_id, data_dir):
        self.tvb_dir = os.path.join(data_dir, 'ds001226/derivatives/TVB', sub_id)
        self.derivative_dir = os.path.join(data_dir, 'derivatives', sub_id)


# Structural Connectivity Data
class StructuralCon:
    _weights = None  # 68*68 numpy float matrix
    _centres = None  # List consisting of region centers (68). Format: [region_name, x, y, z]

    @property
    def weights(self):
        return self._weights

    @property
    def centers(self):
        return self._centres

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
                self._weights = np.array(data, dtype=float)
            # Read centres
            with zip_file.open('centres.txt') as centres_file:
                contents_str = centres_file.read().decode('utf-8')
                rows = contents_str.strip().split('\n')
                self._centres = []
                for row in rows:
                    region, x, y, z = row.strip().split('\t')
                    self._centres.append([region, float(x), float(y), float(z)])
                assert len(self._centres) == 68


class SubjectMeta:
    def __init__(self, sub_id, data_path, fmri_tr, tumor_type_and_grade, tumor_size):
        self.sub_id = sub_id  # String
        self.paths = SubjectsPaths(sub_id, data_path)
        self.fmri_tr = fmri_tr  # Float in ms
        self.tumor_type_and_grade = tumor_type_and_grade  # String
        self.tumor_size = tumor_size  # Float in cm³

    @property
    def is_control(self):
        return 'CON' in self.sub_id


class SubjectData:
    def __init__(self, sc_dk68, ts, ts_dk68, fc_dk68):
        self._sc_dk68 = sc_dk68
        self._ts = ts
        self._ts_dk68 = ts_dk68
        self._fc_dk68 = fc_dk68

    @property
    def sc_dk68(self):
        return self._sc_dk68

    @property
    def ts(self):
        return self._ts

    @property
    def ts_dk68(self):
        return self._ts_dk68

    @property
    def fc_dk68(self):
        return self._fc_dk68


class SubjectTumorRegions:
    def __init__(self, tumor_regions_dataframe):
        self._tumor_regions_df = tumor_regions_dataframe

    def list_tumor_regions_names(self):
        return self._tumor_regions_df[self._tumor_regions_df['Tumor_volume_mm3'] != 0.0]['RegionName'].tolist()

    def list_tumor_regions_ids(self):
        self._tumor_regions_df[self._tumor_regions_df['Tumor_volume_mm3'] != 0.0]['RegionId'].tolist()

    def is_tumor_region_by_id(self, idx):
        assert idx < len(self._tumor_regions_df.index)
        return self._tumor_regions_df.loc[idx]['Tumor_volume_mm3'] != 0.0

    def get_tumor_volume_percentage_by_id(self, idx):
        return self._tumor_regions_df.loc[idx]['Tumor_volume_percentage']

    def get_tumor_volumes_percentage(self):
        return self._tumor_regions_df['Tumor_volume_percentage'].tolist()


class Subject:
    def __init__(self):
        self.meta = None
        self._tumor_regions = None
        self._preop_data = None
        # self._postop_data = None

    @property
    def preop_data(self):
        return self._preop_data

    @property
    def tumor_regions(self):
        return self._tumor_regions

    def initialize(self,
                   sub_id,
                   fmri_tr,
                   tumor_type_and_grade,
                   tumor_size,
                   data_dir):
        # Create subjects metadata
        self.meta = SubjectMeta(sub_id, data_dir, fmri_tr, tumor_type_and_grade, tumor_size)

        self._load_tumor_regions()

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
        return self.meta.is_control

    def get_paths(self):
        return self.meta.paths

    def _init_preop_data(self):
        sc_dk68 = StructuralCon(zip_filename=os.path.join(self.meta.paths.tvb_dir, 'ses-preop/SC.zip'))
        mat_contents = loadmat(os.path.join(self.meta.paths.tvb_dir, 'ses-preop/FC.mat'))
        self._preop_data = SubjectData(
            sc_dk68,
            np.transpose(mat_contents['' + self.meta.sub_id[4:] + 'T1_ROIts']),
            np.transpose(mat_contents['' + self.meta.sub_id[4:] + 'T1_ROIts_DK68']),
            np.transpose(mat_contents['FC_cc_DK68'])
        )

    def _load_tumor_regions(self):
        # If it is not control, load corresponding file
        if not self.is_control():
            self._tumor_regions = SubjectTumorRegions(pd.read_csv(
                os.path.join(self.meta.paths.derivative_dir, 'tumor_regions.tsv'),
                sep='\t'
            ))

    def list_tumor_regions_names(self):
        return self.tumor_regions.list_tumor_regions_names() if self.tumor_regions else []

    def count_tumor_regions(self):
        return len(self.list_tumor_regions_names())

    def list_tumor_regions_ids(self):
        return self.tumor_regions.list_tumor_regions_ids() if self.tumor_regions else []


class Subjects:

    def __init__(self):
        self.data = dict()

    def initialize(self, data_dir):
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
        participants = pd.read_csv(
            os.path.join(data_dir, 'ds001226/participants.tsv'),
            sep='\t'
        )
        for idx, row in participants.iterrows():
            sub = Subject()
            sub.initialize(
                sub_id=row['participant_id'],
                fmri_tr=float(row['fmri TR']),
                tumor_type_and_grade=row['tumor type & grade'],
                tumor_size=float(row['tumor size (cub cm)']),
                data_dir=data_dir
            )
            self.data[row['participant_id']] = sub

    def pretty_print(self):
        print(f'\033[94m', end="")  # Start blue color
        print('{:<15} {:<15} {:<30} {:<15} {:<15}'.format(
            'ID', 'FMRI_TR (ms)', 'TYPE', 'VOLUME (cm³)', '# REGIONS WITH TUMOR'
        ))
        print(f'\033[0m', end="")  # End blue color
        for sub in self.data.values():
            print('{:<15} {:<15} {:<30} {:<15} {:<15}'.format(
                sub.meta.sub_id,
                str(sub.meta.fmri_tr),
                sub.meta.tumor_type_and_grade,
                str(sub.meta.tumor_size),
                str(len(sub.list_tumor_regions_names()))
            ))

    def count(self):
        return len(self.data)

    def for_each(self, func):
        for sub in self.data.values():
            func(sub)

    def get_subject_by_id(self, sub_id):
        return self.data[sub_id]

    def filter_preop_ts_dk68(self):
        result = dict()
        for sub in self.data.values():
            # TODO: Maybe we don't need a copy?
            result[sub.get_id()] = sub.preop_data.ts_dk68.copy()
        return result

    def filter_subjects(self, sub_filter):
        result = Subjects()
        for k, v in self.data.items():
            if sub_filter(v):
                result.data[k] = v
        return result

    def get_control_subset(self):
        return self.filter_subjects(lambda sub: sub.is_control())

    def get_tumor_subset(self):
        return self.filter_subjects(lambda sub: sub.get_tumor_type_and_grade() != 'none')

    def get_meningioma_subset(self):
        return self.filter_subjects(lambda sub: 'Meningioma' in sub.get_tumor_type_and_grade())

    def get_glioma_subset(self):
        return self.filter_subjects(
            lambda sub: sub.get_tumor_type_and_grade() != 'none' and 'Meningioma' not in sub.get_tumor_type_and_grade()
        )

    def get_plus_x_cm3_subset(self, x):
        return self.filter_subjects(lambda sub: sub.get_tumor_size() >= x)

    def exclude_from_subset(self, exclude_list):
        return self.filter_subjects(
            lambda sub: sub.get_id() not in exclude_list
        )

    def keep_only_from_this_set(self, dict_to_filter):
        assert isinstance(dict_to_filter, dict), "dict_to_filter is not a dictionary"
        return {k: v for k, v in dict_to_filter.items() if k in self.data}

    def items(self):
        return self.data.items()
