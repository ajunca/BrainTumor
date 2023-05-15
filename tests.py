# This is a sample Python script.
# import BOLDFilters
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# import WholeBrain.Utils.plotSC
# import WholeBrain.Observables.FC as FCObservable
# import WholeBrain.Observables.Metastability as MSObservable
from subjects import *
import WholeBrain.Observables.intrinsicIgnition as ISObservable
from Observables.functional_connectivity import FunctionalConnectivity
import Observables.swFCD as NonClass_swFCD
from Observables.metastability import Metastability
from Observables.event_based_intrinsic_ignition import EventBasedIntrinsicIgnition
from WholeBrain.Observables.phase_based_intrinsic_ignition import PhaseBasedIntrinsicIgnition
from WholeBrain.Observables.swfcd import swFCD
from Filters.bold_band_pass_filter import BOLDBandPassFilter
import matplotlib.pyplot as plt


def compute_preop_fc_dk68():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()
    fc_operator = FunctionalConnectivity()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        fc_dk68 = fc_operator.from_fMRI(ts_dk68)
        result[sub_id] = fc_dk68

    return result


def compute_preop_metastability_dk68():

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

def compute_preop_event_based_intrinsic_ignition():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()
    ebig_operator = EventBasedIntrinsicIgnition()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        ebig_dk68 = ebig_operator.from_fMRI(ts_dk68)
        result[sub_id] = ebig_dk68

    return result

def compute_preop_event_based_intrinsic_ignition_2():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()

    ISObservable.modality = ISObservable.EventBasedIntrinsicIgnition
    for sub_id, ts_dk68 in preop_ts_dk68.items():
        ebig = ISObservable.from_fMRI(ts_dk68, applyFilters=False, removeStrongArtefacts=False)
        result[sub_id] = ebig
    return result

def compute_preop_phase_based_intrinsic_ignition():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()
    ebig_operator = PhaseBasedIntrinsicIgnition()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        ebig_dk68 = ebig_operator.from_fMRI(ts_dk68)
        result[sub_id] = ebig_dk68

    return result

def compute_preop_phase_based_intrinsic_ignition_2():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()

    ISObservable.modality = ISObservable.PhaseBasedIntrinsicIgnition
    for sub_id, ts_dk68 in preop_ts_dk68.items():
        ebig = ISObservable.from_fMRI(ts_dk68, applyFilters=False, removeStrongArtefacts=False)
        result[sub_id] = ebig
    return result

def compute_preop_swFCD():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()
    ebig_operator = swFCD()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        swFCD_dk68 = ebig_operator.from_fMRI(
            ts_dk68,
            BOLD_filter=BOLDBandPassFilter(tr=2., flp=0.02, fhi=0.1, k=2, remove_strong_artifacts=3.0)
        )
        result[sub_id] = swFCD_dk68

    return result

def compute_preop_swFCD_2():
    preop_ts_dk68 = subjects.filter_preop_ts_dk68()
    result = dict()

    for sub_id, ts_dk68 in preop_ts_dk68.items():
        swFCD = NonClass_swFCD.from_fMRI(ts_dk68, applyFilters=True, removeStrongArtefacts=True)
        result[sub_id] = swFCD
    return result

def plot_metastability_box(subjects_ms):
    fig, ax = plt.subplots()

    s_none = subjects.filter_subjects(lambda sub: sub.get_tumor_type_and_grade() == 'none')
    s_tumor = subjects.filter_subjects(lambda sub: sub.get_tumor_type_and_grade() != 'none')
    s_meningioma = subjects.filter_subjects(lambda sub: 'Meningioma' in sub.get_tumor_type_and_grade())
    s_glioma = subjects.filter_subjects(lambda sub: sub.get_tumor_type_and_grade() != 'none' and 'Meningioma' not in sub.get_tumor_type_and_grade())
    s_plus_15_cm3 = subjects.filter_subjects(lambda sub: sub.get_tumor_size() >= 15.0)
    s_plus_20_cm3 = subjects.filter_subjects(lambda sub: sub.get_tumor_size() >= 20.0)
    s_plus_30_cm3 = subjects.filter_subjects(lambda sub: sub.get_tumor_size() >= 30.0)

    data_none = {k: v.metastability for k, v in subjects_ms.items() if k in s_none.data}
    data_tumor = {k: v.metastability for k, v in subjects_ms.items() if k in s_tumor.data}
    data_meningioma = {k: v.metastability for k, v in subjects_ms.items() if k in s_meningioma.data}
    data_glioma = {k: v.metastability for k, v in subjects_ms.items() if k in s_glioma.data}
    data_plus_15_cm3 = {k: v.metastability for k, v in subjects_ms.items() if k in s_plus_15_cm3.data}
    data_plus_20_cm3 = {k: v.metastability for k, v in subjects_ms.items() if k in s_plus_20_cm3.data}
    data_plus_30_cm3 = {k: v.metastability for k, v in subjects_ms.items() if k in s_plus_30_cm3.data}

    # Convert data to nparray
    split_data = {
        'Control':  np.array(list(data_none.values())),
        'Tumor': np.array(list(data_tumor.values())),
        'Meningioma': np.array(list(data_meningioma.values())),
        'Glioma': np.array(list(data_glioma.values())),
        '>= 15cm³': np.array(list(data_plus_15_cm3.values())),
        '>= 20cm³': np.array(list(data_plus_20_cm3.values())),
        '>= 30cm³': np.array(list(data_plus_30_cm3.values()))
    }
    plt.boxplot(split_data.values(), labels=split_data.keys())

    plt.show()

def plot_metastability(subjects_ms):
    fig = plt.plot()

    plt.barh(
        list(subjects_ms.keys()),
        list({v.metastability for k, v in subjects_ms.items()})
    )
    plt.xlabel('Metastability')
    plt.ylabel('Subject ID')

    plt.show()

if __name__ == '__main__':
    data_root_path = "data/TVB_brain_tumor/"
    data_subjects_path = data_root_path + "derivatives/TVB/"

    subjects = Subjects()
    subjects.initialize(data_subjects_path)

    print("************************* Subjects Info *************************")
    subjects.pretty_print()
    print("*****************************************************************")

    # We then compute the functional connectivity matrices from the filtered BOLD signals
    # preop_fc_dk68_dict = compute_preop_fc_dk68()

    # Compute metastability
    # preop_meta_dk68 = compute_preop_metastability_dk68()
    # plot_metastability_box(preop_meta_dk68)
    # plot_metastability(preop_meta_dk68)

    # preop_ebig_dk68 = compute_preop_event_based_intrinsic_ignition()
    # preop_ebig_dk68_2 = compute_preop_event_based_intrinsic_ignition_2()

    # preop_pbig_dk68 = compute_preop_phase_based_intrinsic_ignition()
    # preop_pbig_dk68_2 = compute_preop_phase_based_intrinsic_ignition_2()

    preop_swFCD_dk68 = compute_preop_swFCD()
    preop_swFCD_dk68_2 = compute_preop_swFCD_2()

