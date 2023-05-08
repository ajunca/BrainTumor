#####################################################################################
# Based on:
#   https://github.com/dagush/WholeBrain/blob/6e8ffe77b7c65fa053f4ca8804cd1c8cb025e263/WholeBrain/Observables/FC.py
#
# Adapted/Refactored from Gustavo Patow code by Albert Juncà
#####################################################################################

from observable import Observable
import numpy as np


class FunctionalConnectivity(Observable):
    # Apply the observable operator
    def _compute_from_fmri(self, bold_signal):
        cc = np.corrcoef(bold_signal, rowvar=True)
        return cc
