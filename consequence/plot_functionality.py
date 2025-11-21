import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import sys
import os

# Ensure the util directory is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import get_components

# Map consequence descriptions to their normalized group names
CONSEQUENCE_TO_GROUP = {
    'Crash': 'Crash/Hang', 
    'lockup / hang': 'Crash/Hang', 
    'Functionality (CFS bandwidth)': 'CFS BW Vio.',
    'Functionality (Deadline enforce / admission control)': 'Deadline Vio.',
    'Functionality (Trace or account)': 'Trace Err.',
    'Functionality (config / feature not enabled/disabled)': 'Config Vio.',
    'Functionality (cpu allowed, or cpuiso)': 'Affinity Vio.',
    'Functionality (hotplug)': 'Hotplug Fail',
    'Functionality (property change fail)': 'Property Err.',
    'Functionality (response error)': 'Return Val Err.',
    'Functionality (starvation)': 'Starvation',
    'Functionality (task state change failure)': 'Task State Err.',
}

GROUP_TO_IDX = {
    'Crash/Hang': 0,
    'Starvation': 1,
    'Deadline Vio.': 2,
    'CFS BW Vio.': 3,
    'Config Vio.': 4,
    'Affinity Vio.': 5,
    'Hotplug Fail': 6,
    'Task State Err.': 7,
    'Property Err.': 8,
    'Return Val Err.': 9,
    'Trace Err.': 10,
}

ObservedWarnings = {
    'panic': 0,
    'warning': 1,
    'silent': 2,
}

COMPONENTS = [
    "core",
    "topology",
    "accounting",
    "fair",
    "deadline",
    "rt",
    "load est.",
]
COMPONENT_TO_IDX = {name: idx for idx, name in enumerate(COMPONENTS)}

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

# --- Load Data ---

df = pd.read_csv("consequence.csv", low_memory=False)
if 'hash' not in df.columns:
    df.columns = [c.strip() for c in df.columns]
commit_hashes = df['hash'].astype(str).tolist()

# Parse the warning for each commit and store in a list
warning_col = df.columns[2]
consequence_col = df.columns[1]

# --- Parse Consequence Groups Per Row ---
all_groups_set = set()
groups_per_row = []
commit_hashes_functionality = []
for i, c in enumerate(df[consequence_col]):
    cons = parse_consequences(c)
    group_names = {}
    for con in cons:
        if con in CONSEQUENCE_TO_GROUP.keys():
            group_names[CONSEQUENCE_TO_GROUP[con]] = True
    if len(group_names) == 0:
        continue
    commit_hashes_functionality.append(commit_hashes[i])
    groups_per_row.append(list(group_names.keys()))
    all_groups_set.update(group_names.keys())

hash_to_warning = {h: ObservedWarnings[df[warning_col][i].lower()] for i, h in enumerate(commit_hashes)}

groupnames = sorted(all_groups_set, key=lambda x: GROUP_TO_IDX[x])
hash2idx = {h: i for i, h in enumerate(commit_hashes_functionality)}

# --- Build Matrix (rows: groups, columns: commits per component) ---
num_cols = len(commit_hashes_functionality)
matrix = np.zeros((len(groupnames), num_cols), dtype=int)

col_idx = 0
for h in commit_hashes_functionality:
    row_idx = hash2idx[h]
    for group in groups_per_row[row_idx]:
        group_idx = GROUP_TO_IDX[group]
        matrix[group_idx, col_idx] = hash_to_warning[h] + 1
    col_idx += 1

print(col_idx)

# --- Plotting ---

# Stacked bar by warning type: panic, warning, silent
warning_types = ["panic", "warning", "silent"]
warning_colors = ["#BF092F", "#FA812F", "#80A1BA"]

# 1: panic, 2: warning, 4: silent (from value in matrix)
# We want the counts for each group, split by warning
group_warning_counts = np.zeros((len(groupnames), len(warning_types)), dtype=int)
for group_idx in range(len(groupnames)):
    # Go through all columns (commits)
    for col in range(matrix.shape[1]):
        v = matrix[group_idx, col]
        if v == 1:
            group_warning_counts[group_idx, 0] += 1   # panic
        elif v == 2:
            group_warning_counts[group_idx, 1] += 1   # warning
        elif v == 3:
            group_warning_counts[group_idx, 2] += 1   # silent

print(group_warning_counts)
# Sort by total
total_counts = group_warning_counts.sum(axis=1)
sorted_indices = np.argsort(-total_counts)
sorted_groupnames = [groupnames[i] for i in sorted_indices]

sorted_group_warning_counts = group_warning_counts[sorted_indices, :]

fig, ax = plt.subplots(figsize=(4.5, 2))
bottom = np.zeros(len(sorted_groupnames))

bars = []
for i, warn_label in enumerate(warning_types):
    for j in range(len(sorted_groupnames)):
        count = sorted_group_warning_counts[j, i]
        if count > 0:
            bar = ax.bar(
                j,
                count,  
                bottom=bottom[j],
                color=warning_colors[i],
                label=warn_label.capitalize() if j == i else None
            )
            bars.append(bar)
            bottom[j] += count

ax.set_xticks(range(len(sorted_groupnames)))
ax.set_xticklabels(sorted_groupnames, rotation=30, ha='right')
ax.set_ylabel("Number of Bugs")
# ax.set_xlabel("Consequence Group")
# ax.set_title("Functionality Consequence Counts (by Warning Type)")
ax.legend(ncol = 2)

for i in range(len(sorted_groupnames)):
    y = 0
    for j in range(len(warning_types)):
        count = sorted_group_warning_counts[i, j]
        if count > 0:
            ax.text(i, y + count/2, str(count), ha='center', va='center', fontsize=9, color="white" if j==0 else "black")
        y += count

plt.tight_layout()
plt.savefig("functionality.pdf")
