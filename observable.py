
import warnings
import numpy as np

class Observable:
    def __init__(self, bold_filter=None):
        self.bold_filter = bold_filter

    @property
    def bold_filter(self):
        return self.bold_filter

    @bold_filter.setter
    def bold_filter(self, value):
        self.bold_filter = value

    def from_fmri(self, bold_signal):
        # First check that there are no NaNs in the signal. If NaNs found, rise a warning and return None
        if np.isnan(bold_signal).any():
            warnings.warn(f'############ Warning!!! {self.__class__.__name__}.from_fmri: NAN found ############')
            return None

        # Compute bold filter if needed, if not leave the signal as it is
        s = bold_signal
        if self.bold_filter is not None:
            s = self.bold_filter.apply_filter(bold_signal)

        # Because we already checked for NaNs in the signal, s must be OK. Apply the observable and return the result
        return self._compute_from_fmri(s)

    def _compute_from_fmri(self, bold_signal):
        pass
