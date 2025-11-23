from typing import Any


import csv
from collections import defaultdict
CONSEQUENCE_TO_GROUP = {
    'Crash': 'FailStop', 
    'lockup / hang': 'FailStop', 
    'Memory Leak': 'Policy', 
    'security vulnerability': 'Security',
    'data corruption': 'SilentFunc.',
    'Functionality (CFS bandwidth)': 'SilentFunc.',
    'Functionality (Deadline enforce / admission control)': 'SilentFunc.',
    'Functionality (Trace or account)': 'SilentFunc.',
    'Functionality (config / feature not enabled/disabled)': 'SilentFunc.',
    'Functionality (cpu allowed, or cpuiso)': 'SilentFunc.',
    'Functionality (hotplug)': 'SilentFunc.',
    'Functionality (property change fail)': 'SilentFunc.',
    'Functionality (response error)': 'SilentFunc.',
    'Functionality (starvation)': 'SilentFunc.',
    'Functionality (task state change failure)': 'SilentFunc.',
    'Performance (Policy violation, balance, work conserving)': 'Policy',
    'Performance (Policy violation, cpufreq control)': 'Policy',
    'Performance (Policy violation, fairness)': 'Policy',
    'Performance (Policy violation, impact from lower priority task)': 'Policy',
    'Performance (Policy violation, locality)': 'Policy',
    'Performance (Policy violation, sched overhead)': 'Policy',
    'Performance (energy efficiency, capacity fit)': 'Policy',
    'No impact (coding rule)': 'Policy',
    'No impact (duplicate call)': 'Policy',
    'No impact (self correcting)': 'Policy',
    'No impact (unnecessary check or warning)': 'Policy',
    # 'compile failure': 'Build',
}


discover_label = {
    "Benchmark/stress test regression": "Benchmark(Perf regression)",
    "Benchmark/stress test/standard test fail": "Benchmark(Warning/Crash)",
    "Customizied test": "Customizied test cases",
    "Fuzz": "Fuzzing",
    "Code Review or Internal Debug": "Inspection from developer",
    "Other kernel subsystem behavior": "Other subsystem reported",
    "User reported or In-production": "Production-user reported",
}
discover_label_to_id = {
    "Benchmark/stress test regression": 0,
    "Benchmark/stress test/standard test fail": 1,
    "Customizied test": 2,
    "Fuzz": 3,
    "Code Review or Internal Debug": 4,
    "Other kernel subsystem behavior": 5,
    "User reported or In-production": 6,
}

discover_id_to_colors = {
    0: '#473472',
    1: '#53629E',
    2: '#87BAC3',
    3: '#D6F4ED',
    4: '#B45253',
    5: '#FCB53B',
    6: '#FFE797',
}
action_label_to_id = {
    "unit test": 2,
    # "bug-on": 1,
    "warning": 0,
    "tracepoint": 1,
    "document": 3,
    "comment": 4,
    "no action": 5,
}

action_id_to_colors = {
    0: '#E49BA6',
    1: '#FFC50F',
    2: '#92487A',
    # 3: '#FFD3D5',
    3: '#658C58',
    4: '#BBC863',
    5: '#F5E5E1',
}

action_label = {
    "unit test": "Unit test",
    # "bug-on": "Bug-on",
    "warning": "Warning",
    "tracepoint": "Tracepoint",
    "comment": "Comment",
    "document": "Document",
    "no action": "Nothing",
}

consequence_group_to_id = {
    "FailStop": 0,
    "SilentFunc.": 1,
    "Policy": 2,
    # "NoImpact": 3,
    "Security": 3,
}

consequence_group_to_label = {
    "FailStop": "FailStop",
    "SilentFunc.": "SilentFunc.",
    "Policy": "Policy",
    # "NoImpact": "NoImpact",
    "Security": "Security",
}


import pandas as pd

def parse_consequences(x):
    """Parse possibly quoted, comma-separated consequence strings."""
    if pd.isna(x):
        return []
    parts, curr, in_quotes = [], '', False
    for char in str(x):
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            if curr.strip():
                parts.append(curr.strip().strip('"'))
            curr = ''
        else:
            curr += char
    if curr.strip():
        parts.append(curr.strip().strip('"'))
    return [p.strip() for p in parts if p.strip()]

def get_consequence_to_methods(csv_file="study-bug-set.csv"):
    consequence_to_methods = {}
    df = pd.read_csv(csv_file, low_memory=False)
    for _, row in df.iterrows():
        method = str(row[1]).strip()
        consequences_str = row[3]
        consequences = parse_consequences(consequences_str)
        for consequence in consequences:
            group = CONSEQUENCE_TO_GROUP[consequence]
            if group not in consequence_to_methods.keys():
                consequence_to_methods[group] = {}
            for m in [m.strip() for m in method.split(',') if m.strip()]:
                if m not in consequence_to_methods[group]:
                    consequence_to_methods[group][m] = 1
                else:
                    consequence_to_methods[group][m] += 1
    # Convert sets to sorted lists
    return consequence_to_methods

# INSERT_YOUR_CODE

def get_consequence_to_fixed_methods(csv_file="study-bug-set.csv"):
    """
    Returns a dict mapping consequence group -> {fixed method: count} using the after-fix methods listed in the CSV.
    """
    consequence_to_fixed_methods = {}
    df = pd.read_csv(csv_file, low_memory=False)
    for _, row in df.iterrows():
        fixed_method = str(row[2]).strip()
        consequences_str = row[3]
        consequences = parse_consequences(consequences_str)
        for consequence in consequences:
            group = CONSEQUENCE_TO_GROUP[consequence]
            if group not in consequence_to_fixed_methods:
                consequence_to_fixed_methods[group] = {}
            for m in [m.strip() for m in fixed_method.split(',') if m.strip()]:
                if m not in consequence_to_fixed_methods[group]:
                    consequence_to_fixed_methods[group][m] = 1
                else:
                    consequence_to_fixed_methods[group][m] += 1
    return consequence_to_fixed_methods

# Example usage:
consequence_fixed_map = get_consequence_to_fixed_methods()
print(consequence_fixed_map)



# Example Usage:
consequence_map = get_consequence_to_methods()
print(consequence_map)

import matplotlib.pyplot as plt
import numpy as np

import matplotlib.gridspec as gridspec

def plot_stacked_bar_percentage(ax, consequence_to_methods, title, labels, label_to_id, return_handles_labels=False):
    """
    Create a stacked bar chart showing percentage of each method under each consequence group.
    
    Args:
        ax: matplotlib axis object
        consequence_to_methods: dict mapping consequence group -> {method: count}
        title: title for the subplot
        return_handles_labels: if True, return (handles, labels) for legend use
    """
    # Get sorted consequence groups
    consequence_groups = sorted(consequence_to_methods.keys(), key=lambda x: consequence_group_to_id[x])
    
    # Collect all unique methods across all consequence groups
    all_methods = set()
    for methods_dict in consequence_to_methods.values():
        all_methods.update(methods_dict.keys())
    all_methods = sorted(all_methods, key=lambda m: label_to_id[m])
    
    # Prepare data: calculate percentages
    data = []
    for method in all_methods:
        method_percentages = []
        for group in consequence_groups:
            total_bugs = sum(consequence_to_methods[group].values())
            method_count = consequence_to_methods[group].get(method, 0)
            percentage = (method_count / total_bugs * 100) if total_bugs > 0 else 0
            method_percentages.append(percentage)
        data.append(method_percentages)
    
    # Create stacked bar chart
    x = np.arange(len(consequence_groups))
    width = 0.6
    
    # Generate colors for each method
    if title == '(a) Manifest Methods':
        colors = [discover_id_to_colors[label_to_id[method]] for method in all_methods]
    else:
        colors = [action_id_to_colors[label_to_id[action]] for action in action_label_to_id.keys()]
    
    # Plot stacked bars
    bottom = np.zeros(len(consequence_groups))
    bars = []
    for i, (method, method_data) in enumerate(zip(all_methods, data)):
        bar = ax.bar(x, method_data, width, label=labels[method], bottom=bottom, color=colors[i])
        bars.append(bar)
        bottom += method_data
    
    # Customize plot
    # ax.set_xlabel('Consequence Group')
    if title == '(a) Manifest Methods':
        ax.set_ylabel('Percentage (%)')
    ax.set_title(title, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(consequence_groups, rotation=45, ha='right')
    ax.set_ylim(0, 100)
    # Don't set legend here; will do globally
    ax.grid(axis='y', alpha=0.3)
    
    if return_handles_labels:
        # Return handles and labels for legend (one bar per method)
        handles = [bar[0] for bar in bars]
        method_labels = [labels[method] for method in all_methods]
        return handles, method_labels

# Instead of subplots, define a GridSpec for two axes and one (shared) legend panel beneath

fig = plt.figure(constrained_layout=False, figsize=(5, 6))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.7, 1], hspace=0.32)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
legend_ax = fig.add_subplot(gs[1, :])
legend_ax.axis('off')  # Hide legend panel axis

# Plot 1: Methods (before fix)
handles1, labels1 = plot_stacked_bar_percentage(ax1, consequence_map, '(a) Manifest Methods', discover_label, discover_label_to_id, return_handles_labels=True)
# Plot 2: Fixed Methods (after fix)
handles2, labels2 = plot_stacked_bar_percentage(ax2, consequence_fixed_map, '(b) After-fix Actions', action_label, action_label_to_id, return_handles_labels=True)

# Plot legends for each plot separately (do not combine)
legend1 = legend_ax.legend(handles1, labels1, loc="lower left", ncol=1, frameon=False, bbox_to_anchor=(-0.15, -0.1))
legend2 = legend_ax.legend(handles2, labels2, loc="lower right", ncol=1, frameon=False, bbox_to_anchor=(0.9, -0.))
legend_ax.add_artist(legend1)  # Ensure both legends appear
legend_ax.add_artist(legend2)
# Optionally, shrink subplot area up a bit to make room for legend (if tight layout isn't enough)
# plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig('test_methods_comparison.pdf', dpi=300, bbox_inches='tight')
plt.show()
