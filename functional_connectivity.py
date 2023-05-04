
from observable import Observable
import numpy as np


class FunctionalConnectivity(Observable):
    # Apply the observable operator
    def _compute_from_fmri(self, bold_signal):
        cc = np.corrcoef(bold_signal, rowvar=True)
        return cc
