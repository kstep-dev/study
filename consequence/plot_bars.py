import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import sys
import os

# Ensure the util directory is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import get_components

# Map consequence descriptions for functionality
CONSEQUENCE_TO_GROUP_FUNC = {
    'Crash': 'Crash/Hang', 
    'lockup / hang': 'Crash/Hang', 
    'Functionality (CFS bandwidth)': 'Sched Attr',
    'Functionality (Deadline enforce / admission control)': 'Sched Attr',
    'Functionality (Trace or account)': 'Trace',
    'Functionality (config / feature not enabled/disabled)': 'Config',
    'Functionality (cpu allowed, or cpuiso)': 'Sched Attr',
    'Functionality (hotplug)': 'Hotplug',
    'Functionality (property change fail)': 'Sched Attr',
    'Functionality (response error)': 'Return Val',
    'Functionality (starvation)': 'Starvation',
    'Functionality (task state change failure)': 'Task State',
}

GROUP_TO_IDX_FUNC = {
    'Crash/Hang': 0,
    'Starvation': 1,
    'Sched Attr': 2,
    # 'CFS BW Vio.': 3,
    'Config': 3,
    # 'Affinity Vio.': 5,
    'Hotplug': 4,
    'Task State': 5,
    'Return Val': 6,
    'Trace': 7,
}

# Map consequence descriptions for policy
CONSEQUENCE_TO_GROUP_POLICY = {
    'Performance (Policy violation, sched overhead)': 'Sched Cost',
    'Performance (Policy violation, balance, work conserving)': 'Balance',
    'Performance (Policy violation, cpufreq control)': 'Freq Ctrl',
    'Performance (Policy violation, fairness)': 'Fairness',
    'Performance (Policy violation, impact from lower priority task)': 'Class Prio',
    'Performance (Policy violation, locality)': 'Locality',
    'Performance (energy efficiency, capacity fit)': 'Energy Eff',
}

GROUP_TO_IDX_POLICY = {
    'Sched Cost': 0,
    'Balance': 1,
    'Freq Ctrl': 2,
    'Fairness': 3,
    'Class Prio': 4,
    'Locality': 5,
    'Energy Eff': 6,
}

ObservedWarnings = {
    'panic': 0,
    'warning': 1,
    'silent': 2,
}

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

def process_data(df, consequence_mapping, group_to_idx):
    """Process data for a specific consequence type."""
    commit_hashes = df['hash'].astype(str).tolist()
    warning_col = df.columns[2]
    consequence_col = df.columns[1]
    
    # Parse Consequence Groups Per Row
    all_groups_set = set()
    groups_per_row = []
    commit_hashes_filtered = []
    
    for i, c in enumerate(df[consequence_col]):
        cons = parse_consequences(c)
        group_names = {}
        for con in cons:
            if con in consequence_mapping.keys():
                group_names[consequence_mapping[con]] = True
        if len(group_names) == 0:
            continue
        commit_hashes_filtered.append(commit_hashes[i])
        groups_per_row.append(list(group_names.keys()))
        all_groups_set.update(group_names.keys())
    
    hash_to_warning = {h: ObservedWarnings[df[warning_col][i].lower()] for i, h in enumerate(commit_hashes)}
    
    groupnames = sorted(all_groups_set, key=lambda x: group_to_idx[x])
    hash2idx = {h: i for i, h in enumerate(commit_hashes_filtered)}
    
    # Build Matrix
    num_cols = len(commit_hashes_filtered)
    matrix = np.zeros((len(groupnames), num_cols), dtype=int)
    
    col_idx = 0
    for h in commit_hashes_filtered:
        row_idx = hash2idx[h]
        for group in groups_per_row[row_idx]:
            group_idx = group_to_idx[group]
            matrix[group_idx, col_idx] = hash_to_warning[h] + 1
        col_idx += 1
    
    return matrix, groupnames

def compute_warning_counts(matrix, groupnames):
    """Compute warning type counts for each group."""
    warning_types = ["panic", "warning", "silent"]
    group_warning_counts = np.zeros((len(groupnames), len(warning_types)), dtype=int)
    
    for group_idx in range(len(groupnames)):
        for col in range(matrix.shape[1]):
            v = matrix[group_idx, col]
            if v == 1:
                group_warning_counts[group_idx, 0] += 1   # panic
            elif v == 2:
                group_warning_counts[group_idx, 1] += 1   # warning
            elif v == 3:
                group_warning_counts[group_idx, 2] += 1   # silent
    
    # Sort by total
    total_counts = group_warning_counts.sum(axis=1)
    sorted_indices = np.argsort(-total_counts)
    sorted_groupnames = [groupnames[i] for i in sorted_indices]
    sorted_group_warning_counts = group_warning_counts[sorted_indices, :]
    
    return sorted_group_warning_counts, sorted_groupnames

def plot_stacked_bars(ax, sorted_group_warning_counts, sorted_groupnames, title):
    """Create a stacked bar chart."""
    warning_types = ["panic", "warning", "silent"]
    if title == "(a) Functionality Bugs":
        warning_colors = ["#BF092F", "#FA812F", "#FFCB61"]
    else:
        warning_colors = ["#BF092F", "#658C58", "#BBC863"]
    # warning_colors = ["#BF092F", "#FA812F", "#80A1BA"]
    
    bottom = np.zeros(len(sorted_groupnames))
    
    for i, warn_label in enumerate(warning_types):
        for j in range(len(sorted_groupnames)):
            count = sorted_group_warning_counts[j, i]
            if count > 0:
                ax.bar(
                    j,
                    count,  
                    bottom=bottom[j],
                    width=0.8, 
                    color=warning_colors[i],
                    label=warn_label.capitalize() if j == i else None
                )
                bottom[j] += count
    
    ax.set_xticks(range(len(sorted_groupnames)))
    ax.set_xticklabels(sorted_groupnames, rotation=40, ha='right')
    ax.set_title(title, fontsize=10)
    if title == "(a) Functionality Bugs":
        ax.set_ylabel("#Bugs")
        # ax.legend(ncol=2, handletextpad=0.7, columnspacing=0.5, borderpad=0.4)
    else:
        ax.set_ylabel("")
        ax.set_yticks([])

    ax.set_ylim(0, 55)
    
    # Add count labels
    for i in range(len(sorted_groupnames)):
        y = 0
        for j in range(len(warning_types)):
            count = sorted_group_warning_counts[i, j]
            if count > 5:
                ax.text(i, y + count/2, str(count), ha='center', va='center', 
                       fontsize=9, color="white" if j==0 else "black")
            y += count

# --- Load Data ---
df = pd.read_csv("consequence.csv", low_memory=False)
if 'hash' not in df.columns:
    df.columns = [c.strip() for c in df.columns]

# Process functionality data
matrix_func, groupnames_func = process_data(df, CONSEQUENCE_TO_GROUP_FUNC, GROUP_TO_IDX_FUNC)
sorted_counts_func, sorted_names_func = compute_warning_counts(matrix_func, groupnames_func)

# Process policy data
matrix_policy, groupnames_policy = process_data(df, CONSEQUENCE_TO_GROUP_POLICY, GROUP_TO_IDX_POLICY)
sorted_counts_policy, sorted_names_policy = compute_warning_counts(matrix_policy, groupnames_policy)

# --- Create Figure with Two Subplots ---
# Dynamically adjust subplot widths based on number of bars/groups
n_func = len(sorted_names_func)
n_policy = len(sorted_names_policy)

# Calculate width ratios; minimum 1 for each, scale left by #groups
# A small fudge (ex: add 0.2 per bar) for better aspect, tune as needed
left_ratio = n_func
right_ratio = n_policy if n_policy else 1
width_ratios = [left_ratio, right_ratio]

fig, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(5.2, 0.8),  # Reduced height from 1.7 to 1.4
    gridspec_kw={'wspace': 0.05, 'width_ratios': width_ratios}  # Remove space between subplots
)

# Plot functionality
plot_stacked_bars(ax1, sorted_counts_func, sorted_names_func, "(a) Functionality Bugs")

# Plot policy
plot_stacked_bars(ax2, sorted_counts_policy, sorted_names_policy, "(b) Policy Bugs")

plt.tight_layout(pad=0.)
plt.savefig("functionality_policy.pdf", bbox_inches='tight', pad_inches=0.01)
print("Saved combined plot to functionality_policy.pdf")

