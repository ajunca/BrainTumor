from observable import Observable
import numpy as np

# ==================================
# import the matlab engine. I hate this, but...
# ==================================
import matlab.engine
eng = matlab.engine.start_matlab()
# ==================================


class IntrinsicIgnition(Observable):
    # ignition_tr_length is the parameter nTRs in the non class based code
    def __init__(self, ignition_tr_length=5):
        self._ignition_tr_length = ignition_tr_length

    @property
    def ignition_tr_length(self):
        return self._ignition_tr_length

    @ignition_tr_length.setter
    def ignition_tr_length(self, value):
        assert (value >= 0)
        self._ignition_tr_length = value

    def _deperm(self, a):
        (useless1, p, useless2, r) = eng.dmperm(eng.double(a), nargout=4)  # Apply MATLABs dmperm
        outp = np.asarray(p).flatten()
        outr = np.asarray(r).flatten()
        return outp, outr

    def _get_components(self, a):
        if a.shape[0] != a.shape[1]:
            raise Exception('Adjacency matrix is not square')

        if not np.any(a - np.triu(a)):
            a = np.logical_or(a, a.T)
            a = a.astype(np.int64)

        # if main diagonal of adj do not contain all ones, i.e., autoloops
        if np.sum(np.diag(a)) != a.shape[0]:
            # the main diagonal is set to ones
            a = np.logical_or(a, np.eye(a.shape[0]))
            a = a.astype(np.int64)

        # i = Integration.IntegrationFromFC_Fast(A, nbins=20)
        p, r = self._dmperm(a)
        # p indicates a permutation (along rows and columns)
        # r is a vector indicating the component boundaries
        # List including the number of nodes of each component. ith entry is r(i+1)-r(i)
        comp_sizes = np.diff(r)
        # Number of components found.
        num_comps = np.size(comp_sizes)
        # initialization
        comps = np.zeros(a.shape[0])
        # first position of each component is set to one
        comps[r[0:num_comps].astype(int)-1] = np.ones(num_comps)
        # cumulative sum produces a label for each component (in a consecutive way)
        comps = np.cumsum(comps)
        # re-order component labels according to adj.
        comps[p.astype(int)-1] = comps

        return comps, comp_sizes

    def _compute_events(self, node_signal, n, t_max):
        events = np.zeros((n, t_max))
        # Let's compute the events. From [DecoEtAl2017]:
        # An intrinsic ignition event for a given brain region is defined by binarizing the transformed
        # functional time series (BOLD fMRI) into z-scores z_i(t) and imposing a threshold \theta such that
        # the binary sequence \sigma_i(t) = 1 if z_i(t) > \theta, and is crossing the threshold from below,
        # and \sigma_i(t) = 0 otherwise
        for seed in range(n):
            tise = node_signal[seed, :t_max]

            # This part of the code computes the \sigma_i as a difference between the binary series ev1
            # and itself shifted (to the right) by 1, to fulfill the "from below" condition: imagine that
            # we have    ev1 = [0 0 1 1 1 1 0],
            # and then   ev2 = [0 0 0 1 1 1 1]
            # the difference will be
            #        ev1-ev2 = [0 0 1 0 0 0 -1]
            # Then, the verification (ev1-ev2) > 0 will give
            #  (ev1-ev2) > 0 = [0 0 1 0 0 0 0],
            # assuming 0 is False and 1 is True. As we see, we have a 1 at the third position, indicating
            # that that's where the event (signal above threshold) started.
            ev1 = tise > (np.std(tise) + np.mean(tise))
            ev1 = ev1.astype(np.int64)  # conversion to int because numpy does not like boolean subtraction...

            # originally, it was ev2 = [0 ev1(1:end-1)])
            ev2 = np.roll(ev1, shift=1)
            ev2[0] = 0

            events[seed, :] = (ev1 - ev2) > 0
        return events

    def _compute_events_max(self, events):
        return events.shape[1]  # int(np.max(np.sum(events, axis=1)))

    # Virtual function, phase based and event based has different implementations
    def _compute_integration(self, node_signal, events, n, t_max):
        pass

    def _event_based_trigger(self, events, integ, n, t_max):
        event_counter = np.zeros(n, dtype=np.uint)  # matrix with 1 x node and number of events in each cell
        integ_stim = np.zeros((n, self._ignition_tr_length-1, self._compute_events_max(events)))  # (nodes x (nTR-1) x events)

        # Save events and integration values for nTRs after the event
        for seed in range(n):
            flag = 0
            for t in range(t_max):
                # Detect first event (nevents = matrix with (1 x node) and number of events in each cell)
                if events[seed, t] == 1 and flag == 0: # if there is an event...
                    flag = 1 # ... initialize the flag, and ...
                    # real events for each subject
                    event_counter[seed] += 1    # ... count it
                # save integration value for nTRs after the first event (nodes x (nTRs-1) x events)
                if flag > 0:
                    # integration for each subject
                    integ_stim[seed, flag-1, int(event_counter[seed])-1] = integ[t]
                    flag = flag + 1
                # after nTRs, set flag to 0 and wait for the next event (then, integ saved for (nTRs-1) events)
                if flag == self._ignition_tr_length:
                    flag = 0
        return event_counter, integ_stim

    def _mean_and_std_dev_ignition(self, event_counter, integ_stim, n):
        # mean and std of the max ignition in the nTRs for each subject and for each node
        mevokedinteg = np.zeros(n)
        stdevokedinteg = np.zeros(n)
        varevokedinteg = np.zeros(n)
        for seed in range(n):
            # Mean integration is called ignition [EscrichsEtAl2021]
            mevokedinteg[seed] = np.mean(np.max(np.squeeze(integ_stim[seed, :, 0:event_counter[seed]]), axis=0))
            # The standard deviation is called metastability [EscrichsEtAl2021]. Greater metastability in a brain
            # area means that this activity changes more frequently across time within the network.
            stdevokedinteg[seed] = np.std(np.max(np.squeeze(integ_stim[seed, :, 0:event_counter[seed]]), axis=0))
            varevokedinteg[seed] = np.var(np.max(np.squeeze(integ_stim[seed, :, 0:event_counter[seed]]), axis=0))
        return mevokedinteg, stdevokedinteg, varevokedinteg

    # Implementation of Observable virtual function
    # output: mean and variability of ignition across the events for a single subject (ss = single subject)
    # 'mevokedinteg_ss', 'stdevokedinteg_ss',
    #  Spontaneous events for each subject
    # 'SubjEvents'
    # mean and variability of ignition across nodes for each single subject (an = across nodes)
    # 'mignition_an', 'stdignition_an'
    def _compute_from_fmri(self, node_signal):
        (n, t_max) = node_signal.shape
        # Both alternatives, event-based and phase-based, require the events for the ignition.
        events = self._compute_events(node_signal, n, t_max)

        # Once we have the events, we can compute the integrations
        integ = self._compute_integration(node_signal, events, n, t_max)

        event_counter, integ_stim = self._event_based_trigger(events, integ, n, t_max)

        mevokedinteg, stdenvokedinteg, varevokedinteg = self._mean_and_std_dev_ignition(event_counter, integ_stim, n)

        # Mean and std ignition across events for each subject in each node (Single Subject -> ss)
        # Done for compatibility with Deco's code
        mevokedinteg_ss = mevokedinteg
        stdevokedinteg_ss = stdenvokedinteg
        fanofactorevokedinteg_ss = varevokedinteg / mevokedinteg  # calculate Fan factor var()./mevokedinteg
        # Mean and std ignition for a subject across nodes (an)
        mignition_an = np.mean(mevokedinteg)

        return {
            'mevokedinteg': mevokedinteg_ss,
            'stdevokedinteg': stdevokedinteg_ss,
            'fanofactorevokedinteg': fanofactorevokedinteg_ss,
            'mignition': mignition_an
        }
