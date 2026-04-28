from util import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

def collect_test_method_data():
    data = read_data()
    hashes = list(data.keys())

    group_discover_counts = np.zeros((len(OBSERVABILITY_TO_IDX), len(GROUP_TO_IDX_DISCOVER)), dtype=int)
    group_prevention_counts = np.zeros((len(OBSERVABILITY_TO_IDX), len(PREVENTION_TO_GROUP)), dtype=int)

    for hash in hashes:
        discover = data[hash]["discover"]
        preventions = data[hash]["prevention"]
        consequences = data[hash]["consequence"]
        for consequence in consequences:
            observability = CONSEQUENCE_TO_OBSERVABILITY[consequence]
            group = DISCOVER_TO_GROUP[discover]
            group_discover_counts[OBSERVABILITY_TO_IDX[observability], GROUP_TO_IDX_DISCOVER[group]] += 1

            for prevention in preventions:
                group = PREVENTION_TO_GROUP[prevention]
                group_prevention_counts[OBSERVABILITY_TO_IDX[observability], GROUP_TO_IDX_PREVENTION[group]] += 1

    return group_discover_counts, group_prevention_counts

if __name__ == "__main__":
    group_discover_counts, group_prevention_counts = collect_test_method_data()

    # Plot 1: Methods (before fix)
    fig = plt.figure(figsize=(4.5, 2))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.81], hspace=0.5)
    ax1 = fig.add_subplot(gs[0, 0]) # Discover Methods bar
    ax2 = fig.add_subplot(gs[1, 0]) # Discover Methods legend
    ax2.axis('off')

    plot_stacked_bar_percentage(ax1, ax2,
                                group_discover_counts, 
                                DISCOVER_ID_TO_COLORS, 
                                DISCOVER_ID_TO_LABELS, 
                                OBSERVABILITY_ID_TO_LABELS,
                                legend_args={
                                    'ncol': 2, 'bbox_to_anchor': (-0.3, 0.7), 
                                    'handletextpad': 0.6, 'columnspacing': 0.6, 
                                    'handlelength': 1.2, 'labelspacing': 0.5
                                },
                               )
    save_figure_variants(fig, "Fig9_manifest_methods", bbox_inches='tight', pad_inches=0.0)

    # Plot 2: Prevention Methods (after fix)
    fig = plt.figure(figsize=(4.5, 1.2))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.01], hspace=0.5)

    ax1 = fig.add_subplot(gs[0, 0]) # Prevention Methods bar
    ax2 = fig.add_subplot(gs[1, 0]) # Prevention Methods legend
    ax2.axis('off')

    plot_stacked_bar_percentage(ax1, ax2,
                                group_prevention_counts, 
                                PREVENTION_ID_TO_COLORS, 
                                PREVENTION_ID_TO_LABELS, 
                                OBSERVABILITY_ID_TO_LABELS,
                                legend_args={
                                    'ncol': 6, 'bbox_to_anchor': (-0.4, 2.5), 
                                    'handletextpad': 0.2, 'columnspacing': 0.4, 
                                    'labelspacing': 0.2, 'handlelength': 0.6}
                                )

    save_figure_variants(fig, "Fig10_prevention_methods", bbox_inches='tight', pad_inches=0.0)
