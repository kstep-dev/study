from typing import Any


import csv
from collections import defaultdict
CONSEQUENCE_TO_GROUP = {
    'Crash': 'Func. Crash/Hang', 
    'lockup / hang': 'Func. Crash/Hang', 
    'Memory Leak': 'Policy. With Effect', 
    'security vulnerability': 'Func. Non-fatal.',
    'data corruption': 'Func. Non-fatal.',
    'Functionality (CFS bandwidth)': 'Func. Non-fatal.',
    'Functionality (Deadline enforce / admission control)': 'Func. Non-fatal.',
    'Functionality (Trace or account)': 'Func. Non-fatal.',
    'Functionality (config / feature not enabled/disabled)': 'Func. Non-fatal.',
    'Functionality (cpu allowed, or cpuiso)': 'Func. Non-fatal.',
    'Functionality (hotplug)': 'Func. Non-fatal.',
    'Functionality (property change fail)': 'Func. Non-fatal.',
    'Functionality (response error)': 'Func. Non-fatal.',
    'Functionality (starvation)': 'Func. Non-fatal.',
    'Functionality (task state change failure)': 'Func. Non-fatal.',
    'Performance (Policy violation, balance, work conserving)': 'Policy. With Effect',
    'Performance (Policy violation, cpufreq control)': 'Policy. With Effect',
    'Performance (Policy violation, fairness)': 'Policy. With Effect',
    'Performance (Policy violation, impact from lower priority task)': 'Policy. With Effect',
    'Performance (Policy violation, locality)': 'Policy. With Effect',
    'Performance (Policy violation, sched overhead)': 'Policy. With Effect',
    'Performance (energy efficiency, capacity fit)': 'Policy. With Effect',
    'No impact (coding rule)': 'Policy. Benign',
    'No impact (duplicate call)': 'Policy. Benign',
    'No impact (self correcting)': 'Policy. Benign',
    'No impact (unnecessary check or warning)': 'Policy. Benign',
    # 'compile failure': 'Build',
}


discover_label = {
    "Benchmark/stress test regression": "Benchmark(Perf regression)",
    "Benchmark/stress test/standard test fail": "Benchmark(Warning/Crash)",
    "Customizied test": "Customized test cases",
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
    "Func. Crash/Hang": 0,
    "Func. Non-fatal.": 1,
    "Policy. With Effect": 2,
    # "NoImpact": 3,
    "Policy. Benign": 3,
    # "Security": 4,
}

consequence_group_to_label = {
    "Func. Crash/Hang": "Func. Crash/Hang",
    "Func. Non-fatal.": "Func. Non-fatal.",
    "Policy. With Effect": "Policy. With Effect",
    # "NoImpact": "NoImpact",
    "Policy. Benign": "Policy. Benign",
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
        method = str(row[2]).strip()
        consequences_str = row[4]
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
        fixed_method = str(row[3]).strip()
        consequences_str = row[4]
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
    Create a horizontal stacked bar chart showing percentage of each method under each consequence group.
    
    Args:
        ax: matplotlib axis object
        consequence_to_methods: dict mapping consequence group -> {method: count}
        title: title for the subplot
        return_handles_labels: if True, return (handles, labels) for legend use
    """
    # Get sorted consequence groups (reversed for horizontal bars to show top to bottom)
    consequence_groups = sorted(consequence_to_methods.keys(), key=lambda x: consequence_group_to_id[x], reverse=True)
    
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
    
    # Create horizontal stacked bar chart
    y = np.arange(len(consequence_groups))
    height = 1
    
    # Generate colors for each method
    if title == '(a) Manifest Methods':
        colors = [discover_id_to_colors[label_to_id[method]] for method in all_methods]
    else:
        colors = [action_id_to_colors[label_to_id[action]] for action in action_label_to_id.keys()]
    
    # Plot horizontal stacked bars
    left = np.zeros(len(consequence_groups))
    bars = []
    # Store actual counts for annotations
    actual_counts = []
    for i, (method, method_data) in enumerate(zip(all_methods, data)):
        # Calculate actual counts from percentages
        counts_for_method = []
        for j, group in enumerate(consequence_groups):
            total_bugs = sum(consequence_to_methods[group].values())
            count = consequence_to_methods[group].get(method, 0)
            counts_for_method.append(count)
        actual_counts.append(counts_for_method)
        
        bar = ax.barh(y, method_data, height, label=labels[method], left=left, color=colors[i], edgecolor='gray', linewidth=0.01)
        bars.append(bar)
        left += method_data
    
    # Add count annotations
    # Define text colors for each method type based on background colors
    if title == '(a) Manifest Methods':
        color_list = ['white', 'white', 'black', 'black', 'white', 'black', 'black']
    else:
        color_list = ['white', 'black', 'white', 'black', 'black', 'black']
    
    for i, (method, method_data) in enumerate(zip(all_methods, data)):
        for j, (percentage, count) in enumerate(zip(method_data, actual_counts[i])):
            if percentage > 2:  # Only show if there are bugs
                # Calculate position for text
                x_pos = sum(data[k][j] for k in range(i)) + percentage / 2
                y_pos = y[j]
                
                ax.text(x_pos, y_pos, str(count), 
                       ha='center', va='center', fontsize=8, 
                       color=color_list[i])
    
    # Customize plot
    # if title != '(a) Manifest Methods':
        # ax.set_xlabel('Percentage (%)', labelpad=1)
    # ax.set_title(title, fontsize=10)
    ax.set_yticks(y)
    ax.set_yticklabels(consequence_groups, rotation=0)
    ax.set_xlim(0, 100)
    # if title == '(a) Manifest Methods':
    ax.set_xticks([])
    # ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    # else:
    #     ax.set_xticks([0, 20, 40, 60, 80, 100])
    #     ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    # Don't set legend here; will do globally
    ax.grid(axis='x', alpha=0.3)
    ax.set_ylim(bottom=-0.5, top = len(consequence_groups) - 0.5)
    
    if return_handles_labels:
        # Return handles and labels for legend (one bar per method)
        handles = [bar[0] for bar in bars]
        method_labels = [labels[method] for method in all_methods]
        return handles, method_labels

# Instead of subplots, define a GridSpec for two axes and one (shared) legend panel beneath

fig = plt.figure(constrained_layout=False, figsize=(4.5, 3.9))
gs = gridspec.GridSpec(4, 1, height_ratios=[1, 0.8, 1, 0.01], hspace=0.5)

ax1 = fig.add_subplot(gs[0, 0])
legend1_ax = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[2, 0])
legend2_ax = fig.add_subplot(gs[3, 0])
legend1_ax.axis('off')  # Hide legend panel axis
legend2_ax.axis('off')

ax1.tick_params(which='both', length=1)
ax2.tick_params(which='both', length=1)

# Plot 1: Methods (before fix)
handles1, labels1 = plot_stacked_bar_percentage(ax1, consequence_map, '(a) Manifest Methods', discover_label, discover_label_to_id, return_handles_labels=True)
# Legend for plot 1
legend1 = legend1_ax.legend(handles1, labels1, loc="center left", ncol=2, frameon=False, bbox_to_anchor=(-0.3, 0.7), handletextpad=0.6, columnspacing=0.6, handlelength=1.2, labelspacing=0.5)

# Plot 2: Fixed Methods (after fix)
handles2, labels2 = plot_stacked_bar_percentage(ax2, consequence_fixed_map, '(b) After-fix Actions', action_label, action_label_to_id, return_handles_labels=True)
# Legend for plot 2
legend2 = legend2_ax.legend(handles2, labels2, loc="center left", ncol=6, frameon=False, bbox_to_anchor=(-0.4, 2.5), handletextpad=0.2, columnspacing=0.4, labelspacing=0.2, handlelength=0.6)

plt.savefig('test_methods_comparison.pdf', bbox_inches='tight', pad_inches=0.0)
plt.show()
