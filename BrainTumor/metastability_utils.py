import numpy as np
from WholeBrain.Observables.metastability import Metastability
from WholeBrain.Filters.bold_band_pass_filter import BOLDBandPassFilter

def compute_metastability(subjects):
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()
    ms_operator = Metastability()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        tr = subjects.get_subject_by_id(sub_id).get_fmri_tr()/1000.0
        ms_dk68 = ms_operator.from_fMRI(
            ts_dk68,
            BOLD_filter=BOLDBandPassFilter(tr=tr, flp=0.007, fhi=0.07, k=2, remove_strong_artifacts=3.0)
        )
        result[sub_id] = ms_dk68
    return result
