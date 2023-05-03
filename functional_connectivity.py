
from observable import Observable
import numpy as np


class FunctionalConnectivity(Observable):

    # This constructor is not needed (redundant), just is in here to make the code more understandable
    def __init__(self, bold_filter=None):
        super().__init__(bold_filter)

    # Apply the observable operator
    def _compute_from_fmri(self, bold_signal):
        cc = np.corrcoef(bold_signal, rowvar=True)
        return cc
