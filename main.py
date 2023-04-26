# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import WholeBrain.Utils.plotSC
from setup import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for sub in subjects_meta:
        # WholeBrain.Utils.plotSC.plotSC_and_Histogram(sub.sub_id, subjects_sc[sub.sub_id][0].weights)
        WholeBrain.Utils.plotSC.plotSCMatrixAsFancyGraph(subjects_sc[sub.sub_id][0].weights)
        break
