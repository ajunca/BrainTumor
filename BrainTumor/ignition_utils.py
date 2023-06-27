import numpy as np
from WholeBrain.Observables.event_based_intrinsic_ignition import EventBasedIntrinsicIgnition
from WholeBrain.Filters.bold_band_pass_filter import BOLDBandPassFilter

def compute_ignitions(subjects):
    ignitions = dict()

    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    for sub_id, ts_dk68 in preop_ts_dk68.items():

        tr_ms = subjects.get_subject_by_id(sub_id).get_fmri_tr()

        # If we use length 8 for the 2100ms TR scans and length 7 for the 2400ms scans (or multiple of them), then we have the same windows
        # time frame for each subject (16800ms)
        ignition_tr_length = None
        if np.isclose(tr_ms, 2400.0):
            ignition_tr_length = 7
        elif np.isclose(tr_ms, 2100.0):
            ignition_tr_length = 8
        assert ignition_tr_length is not None, "Ups... TR length not 2100 or 2400..."

        ebig_operator = EventBasedIntrinsicIgnition(ignition_tr_length=ignition_tr_length)

        ebig_dk68 = ebig_operator.from_fMRI(
            ts_dk68,
            # flp=0.01, fhi=0.1
            #   Tagliazucchi, Enzo, Pablo Balenzuela, Daniel Fraiman, and Dante R. Chialvo.
            #       “Criticality in Large-Scale Brain FMRI Dynamics Unveiled by a Novel
            #       Point Process Analysis.” Frontiers in Physiology 3 (2012). https://doi.org/10.3389/fphys.2012.00015.
            #
            # flp=0.04, fhi=0.07. NOTE: This paper uses phased based intrinsic ignition.
            #   Glerean, Enrico, Juha Salmi, Juha M. Lahnakoski, Iiro P. Jääskeläinen, and Mikko Sams.
            #       “Functional Magnetic Resonance Imaging Phase Synchronization as a Measure of Dynamic Functional Connectivity.”
            #       Brain Connectivity 2, no. 2 (April 2012): 91–101. https://doi.org/10.1089/brain.2011.0068.

            # Anira paper flp=0.01 fhi=0.09
            BOLD_filter=BOLDBandPassFilter(tr=tr_ms / 1000.0, flp=0.01, fhi=0.09, k=2, remove_strong_artifacts=3.0)
        )
        ignitions[sub_id] = ebig_dk68
    return ignitions

def compute_mean_ignition(subjects_subset, ignitions):
    mean_control_ignition = [{
        'mevokedinteg': 0.0,
        'stdevokedinteg': 0.0,
        'fanofactorevokedinteg': 0.0,
    } for i in range(68)]

    for k, sub in subjects_subset.items():
        for i in range(68):
            mean_control_ignition[i]['mevokedinteg'] += ignitions[k].mevokedinteg[i]
            mean_control_ignition[i]['stdevokedinteg'] += ignitions[k].stdevokedinteg[i]
            mean_control_ignition[i]['fanofactorevokedinteg'] += ignitions[k].fanofactorevokedinteg[i]

    for i in range(68):
        mean_control_ignition[i]['mevokedinteg'] /= subjects_subset.count()
        mean_control_ignition[i]['stdevokedinteg'] /= subjects_subset.count()
        mean_control_ignition[i]['fanofactorevokedinteg'] /= subjects_subset.count()

    return mean_control_ignition

def compute_delta_ignitions(mean_ignition, ignitions, subjects_subset):
    subjects_delta_ignitions = {}

    for k, s in subjects_subset.items():
        subjects_delta_ignitions[k] = [{} for i in range(68)]
        for i in range(68):
            subjects_delta_ignitions[k][i]['mevokedinteg'] = ignitions[k].mevokedinteg[i] - \
                                                                   mean_ignition[i]['mevokedinteg']
            subjects_delta_ignitions[k][i]['stdevokedinteg'] = ignitions[k].stdevokedinteg[i] - \
                                                                     mean_ignition[i]['stdevokedinteg']
            subjects_delta_ignitions[k][i]['fanofactorevokedinteg'] = ignitions[k].fanofactorevokedinteg[i] - \
                                                                            mean_ignition[i][
                                                                                'fanofactorevokedinteg']
    return subjects_delta_ignitions