# Adapted from Whole Brain library
# https://github.com/dagush/WholeBrain/blob/master/WholeBrain/Observables/Metastability.py

import warnings
from observable import Observable
from bold_band_pass_filter import BoldBandPassFilter
from scipy import signal
from WholeBrain.Utils import demean
import numpy as np


class Metastability(Observable):
    def _compute_from_fmri(self, bold_signal):
        (N, t_max) = bold_signal.shape
        npattmax = t_max - 19    # Calculates the size of phfcd vector

        # Some data structures we are going to need
        phases = np.zeros([N, t_max])

        # Parent class already applies the bold filter if not None, so no need in here

        # Compute phases
        for n in range(N):
            # TODO: Is demean really necessary? Done when bold filter is applied? What if bold filter is not applied?
            x_analytic = signal.hilbert(demean.demean(bold_signal[n, :]))
            phases[n, :] = np.angle(x_analytic)

        T = np.arange(10, t_max - 10 + 1)
        sync = np.zeros(T.size)
        for t in T:
            ku = np.sum(np.cos(phases[:, t-1]) + 1j * np.sin(phases[:, t-1])) / N
            sync[t - 10] = abs(ku)

        # Return the metastability value
        return np.std(sync)
