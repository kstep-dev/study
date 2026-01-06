from util import *
from typing import Any
import csv
from collections import defaultdict
import pandas as pd
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

# Create a horizontal stacked bar chart showing percentage of each method under each observability group.
def plot_stacked_bar_percentage(ax, legend_ax, counts, colors, labels, y_labels, legend_args):
    # Prepare data: calculate percentages
    data = []
    for method_idx in range(len(counts[0])):
        method_percentages = []
        for observability_idx in range(len(counts)):
            total_bugs = sum(counts[observability_idx])
            method_count = counts[observability_idx][method_idx]
            percentage = (method_count / total_bugs * 100) if total_bugs > 0 else 0
            method_percentages.append(percentage)
        data.append(method_percentages)
    
    # Create horizontal stacked bar chart
    y = np.arange(len(counts))
    left = np.zeros(len(counts))
    bars = []
    for method_idx, method_data in enumerate(data):
        bar = ax.barh(y, method_data, 1, label=labels[method_idx], left=left, color=colors[method_idx][0], edgecolor='gray', linewidth=0.01)
        bars.append(bar)
        left += method_data
    
    # Add count annotations
    for method_idx, method_data in enumerate(data):
        for observability_idx, percentage in enumerate(method_data):
            if percentage > 2:  # Only show if there are bugs
                x_pos = sum(data[k][observability_idx] for k in range(method_idx)) + percentage / 2
                y_pos = y[observability_idx]                
                ax.text(x_pos, y_pos, str(counts[observability_idx][method_idx]), 
                       ha='center', va='center', fontsize=8, 
                       color=colors[method_idx][1])

    # the plot settings for the bar chart
    ax.invert_yaxis()
    ax.tick_params(which='both', length=0.1)

    ax.set_ylim(bottom=-0.5, top = len(counts) - 0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([y_labels[i] for i in y], rotation=0)

    ax.set_xlim(0, 100)
    ax.set_xticks([])

    # Add legend
    handles = [bar[0] for bar in bars]
    legend_ax.legend(handles, [labels[i] for i in range(len(labels))],
                     loc="center left",  frameon=False, 
                     **legend_args)

    return

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
    fig.savefig(RESULT_DIR / 'manifest_methods.pdf', bbox_inches='tight', pad_inches=0.0)

    # Plot 2: Prevention Methods (after fix)
    fig = plt.figure(figsize=(4.5, 1.5))
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

    fig.savefig(RESULT_DIR / 'prevention_methods.pdf', bbox_inches='tight', pad_inches=0.0)
