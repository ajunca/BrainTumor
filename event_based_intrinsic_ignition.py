
from intrinsic_ignition import IntrinsicIgnition
import numpy as np

class EventBasedIntrinsicIgnition(IntrinsicIgnition):
    def _compute_integration(self, node_signal, events, n, t_max):
        # Integration
        # -----------
        # obtain 'events connectivity matrix' and integration value (integ)
        events_matrix = np.zeros([n, n])
        integ = np.zeros(t_max)
        for t in range(t_max):
            for i in range(n):
                for j in range(n):
                    events_matrix[i, j] = events[i, t] * events[j, t]
            cc = events_matrix - np.eye(n)
            comps, csize = self._get_components(cc)
            integ[t] = max(csize)/n
        return integ
