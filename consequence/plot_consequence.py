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
    'Crash': 'FailStop', 
    'lockup / hang': 'FailStop', 
    'Memory Leak': 'NoImpact', 
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
    'No impact (coding rule)': 'NoImpact',
    'No impact (duplicate call)': 'NoImpact',
    'No impact (self correcting)': 'NoImpact',
    'No impact (unnecessary check or warning)': 'NoImpact',
    # 'compile failure': 'Build',
}

GROUP_TO_IDX = {
    'FailStop': 0,
    'SilentFunc.': 1,
    'Policy': 2,
    'NoImpact': 3,
    'Security': 4,
}

ObservedWarnings = {
    'panic': 0,
    'warning': 1,
    'silent': 3,
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

# Group hashes by component
component_to_hash = {idx: [] for idx in range(len(COMPONENTS))}
for h in commit_hashes:
    components = get_components(h)
    if len(components) == 1:
        for comp in components:
            component_to_hash[COMPONENT_TO_IDX[comp]].append(h)
    else:
        for comp in components:
            if comp == "accounting":
                continue
            component_to_hash[COMPONENT_TO_IDX[comp]].append(h)

hash_to_warning = {h: ObservedWarnings[df[warning_col][i].lower()] for i, h in enumerate(commit_hashes)}
print(hash_to_warning)
# --- Parse Consequence Groups Per Row ---
all_groups_set = set()
groups_per_row = []
for c in df[consequence_col]:
    cons = parse_consequences(c)
    group_names = {CONSEQUENCE_TO_GROUP.get(con, con) for con in cons}
    groups_per_row.append(list(group_names))
    all_groups_set.update(group_names)

groupnames = sorted(all_groups_set, key=lambda x: GROUP_TO_IDX[x])
hash2idx = {h: i for i, h in enumerate(commit_hashes)}

# --- Build Matrix (rows: groups, columns: commits per component) ---
num_cols = sum(len(hashes) for hashes in component_to_hash.values())
matrix = np.zeros((len(groupnames), num_cols), dtype=int)

col_idx = 0
for component, hashes in component_to_hash.items():
    for h in hashes:
        row_idx = hash2idx[h]
        for group in groups_per_row[row_idx]:
            group_idx = GROUP_TO_IDX[group]
            matrix[group_idx, col_idx] = hash_to_warning[h] + 1
        col_idx += 1

print(col_idx)
# --- Component Boundaries for Plotting ---
component_boundaries = []
colcount = 0
for hashes in component_to_hash.values():
    colcount += len(hashes)
    component_boundaries.append(colcount)

# --- Colors ---
custom_colors = [
    "#FFFFFF",  # white
    "#BF092F",  # green
    "#FA812F",  # red
    "#80A1BA",  # blue
]

# --- Plotting ---

plt.figure(figsize=(10, 1.4))
im = plt.imshow(matrix, aspect='auto', interpolation='nearest', cmap=ListedColormap(custom_colors))

# Draw component boundaries and labels
offset = [0.5, 10, -5, 0.5, 10, 3, 0.5]
for i, boundary in enumerate(component_boundaries):
    plt.axvline(x=boundary - 0.5, color='black', linestyle='--', linewidth=1)
    last_boundary = component_boundaries[i-1] if i > 0 else 0
    label_pos = (boundary + last_boundary) / 2 - offset[i]
    # y_offset = -1 if i in (2, 6) else 0.1
    plt.text(label_pos, -1, COMPONENTS[i], ha='center', va='center')

plt.xlabel("Commits (group by component)")
plt.yticks(np.arange(len(groupnames)), groupnames, rotation=0)
plt.xticks(
    np.arange(0, matrix.shape[1], 30),
    labels=[str(i) for i in np.arange(0, matrix.shape[1], 30)]
)

import matplotlib as mpl

# Add a colorbar (colormap) to show color meaning
cbar = plt.colorbar(
    im,
    orientation='horizontal',
    fraction=0.13,
    pad=0.23,
    ticks=[0, 1, 2, 3],
    anchor=(0.0, 0.0)  # Shift colorbar a little bit to the right
)

positions = [0.5, 1.5, 2.5, 3.5]
labels = ['', 'Panic', 'Warning', 'Silent']

cbar.set_ticks([])
colors = ['#FFFFFF', '#FFFFFF', '#000000', '#000000']

for pos, label in zip(positions, labels):
    cbar.ax.text(
        pos, 0.5, label,
        ha='center', va='center',
        fontsize=10,
        color=colors[int(pos-0.5)],
        transform=cbar.ax.transData
    )

plt.tight_layout(pad=0.1)
plt.savefig("consequence.pdf")
