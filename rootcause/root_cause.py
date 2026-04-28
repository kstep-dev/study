from util import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

def collect_test_method_data():
    data = read_data()
    hashes = list(data.keys())

    group_rootcause_counts = np.zeros((len(OBSERVABILITY_TO_IDX), len(GROUP_TO_IDX_ROOTCAUSE)), dtype=int)

    for hash in hashes:
        rootcause = data[hash]["root_cause"]
        consequences = data[hash]["consequence"]
        for consequence in consequences:
            observability = CONSEQUENCE_TO_OBSERVABILITY[consequence]
            group = ROOTCAUSE_TO_GROUP[rootcause]
            group_rootcause_counts[OBSERVABILITY_TO_IDX[observability], GROUP_TO_IDX_ROOTCAUSE[group]] += 1

    return group_rootcause_counts

if __name__ == "__main__":
    group_rootcause_counts = collect_test_method_data()

    fig = plt.figure(figsize=(5.3, 1.4))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.01], hspace=0.2)
    ax1 = fig.add_subplot(gs[0, 0]) # Root Cause bar
    ax2 = fig.add_subplot(gs[1, 0]) # Root Cause legend
    ax2.axis('off')

    plot_stacked_bar_percentage(ax1, ax2,
                                group_rootcause_counts, 
                                ROOTCAUSE_ID_TO_COLORS, 
                                ROOTCAUSE_ID_TO_LABELS, 
                                OBSERVABILITY_ID_TO_LABELS,
                                legend_args={
                                    'ncol': 5, 'bbox_to_anchor': (0., 0.), 
                                    'handletextpad': 0.2, 'columnspacing': 0.5, 
                                    'handlelength': 1, 'labelspacing': 0.2
                                },
                               )
    save_figure_variants(fig, "Fig11_root_cause", bbox_inches='tight', pad_inches=0.0)
