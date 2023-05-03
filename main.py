# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import WholeBrain.Utils.plotSC
from setup import *
import WholeBrain.Observables.FC as FCObservable
from functional_connectivity import FunctionalConnectivity


# Return the pre-operational BOLD signal (ts_dk68) filtered for each subject in s
def filter_preop_ts_dk68_signals_if_needed(s):
    filtered_ts_dk68_dict = dict()

    def f(sub):
        if apply_bold_filters:
            filters.TR = sub.get_fmri_tr() / 1000.  # Subject fMRI TR in seconds
            filtered_dk68 = filters.BandPassFilter(sub.preop_data.ts_dk68)  # Apply filter
            filtered_ts_dk68_dict[sub.get_id()] = filtered_dk68  # Store result
        else:
            # Just return a copy of the stored signal
            filtered_ts_dk68_dict[sub.get_id()] = sub.preop_data.ts_dk68.copy()

    # Process each subject
    s.for_each(f)
    return filtered_ts_dk68_dict


def compute_preop_fc_dk68(preop_ts_dk68_dict):
    preop_fc_dk68_dict = dict()

    for sub_id, ts_dk68 in preop_ts_dk68_dict.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        fc_dk68 = FCObservable.from_fMRI(ts_dk68, applyFilters=False, removeStrongArtefacts=False)
        preop_fc_dk68_dict[sub_id] = fc_dk68

    return preop_fc_dk68_dict


def compute_preop_fc_dk68_2(preop_ts_dk68_dict):
    preop_fc_dk68_dict = dict()

    fc_operator = FunctionalConnectivity(bold_filter=None)

    for sub_id, ts_dk68 in preop_ts_dk68_dict.items():
        # Compute functional connectivity. Note signal are already filtered, so no need to do it here
        fc_dk68 = fc_operator.from_fmri(ts_dk68)
        preop_fc_dk68_dict[sub_id] = fc_dk68

    return preop_fc_dk68_dict


if __name__ == '__main__':
    # First step is to filter preop BOLD data signals if needed
    filtered_preop_ts_dk68_dict = filter_preop_ts_dk68_signals_if_needed(subjects)

    # We then compute the functional connectivity matrices from the filtered BOLD signals
    preop_fc_dk68_dict = compute_preop_fc_dk68_2(filtered_preop_ts_dk68_dict)
