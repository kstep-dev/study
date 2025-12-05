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
    'Crash': 'Func. Crash/Hang', 
    'lockup / hang': 'Func. Crash/Hang', 
    'Memory Leak': 'Policy. Benign', 
    'security vulnerability': 'Func. Non-fatal',
    'data corruption': 'Func. Non-fatal',
    'Functionality (CFS bandwidth)': 'Func. Non-fatal',
    'Functionality (Deadline enforce / admission control)': 'Func. Non-fatal',
    'Functionality (Trace or account)': 'Func. Non-fatal',
    'Functionality (config / feature not enabled/disabled)': 'Func. Non-fatal',
    'Functionality (cpu allowed, or cpuiso)': 'Func. Non-fatal',
    'Functionality (hotplug)': 'Func. Non-fatal',
    'Functionality (property change fail)': 'Func. Non-fatal',
    'Functionality (response error)': 'Func. Non-fatal',
    'Functionality (starvation)': 'Func. Non-fatal',
    'Functionality (task state change failure)': 'Func. Non-fatal',
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

GROUP_TO_IDX = {
    'Func. Crash/Hang': 0,
    'Func. Non-fatal': 1,
    'Policy. With Effect': 2,
    'Policy. Benign': 3,
    # 'NoImpact': 3,
    # 'Security': 4,
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
    # "load est.",
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

# Create a mapping from hash to its most severe consequence (lowest GROUP_TO_IDX value)
hash_to_severity = {}
for i, h in enumerate(commit_hashes):
    groups = groups_per_row[i]
    if groups:
        min_severity = min(GROUP_TO_IDX[g] for g in groups)
    else:
        min_severity = 999  # No consequence, put at end
    hash_to_severity[h] = min_severity

# Sort hashes within each component by:
# 1. Consequence severity (primary)
# 2. Warning level (secondary) - panic/warning before silent
for component in component_to_hash:
    component_to_hash[component].sort(key=lambda h: (hash_to_severity[h], hash_to_warning[h]))

# Count commits per severity per component
component_severity_counts = {}
for comp_idx, hashes in component_to_hash.items():
    severity_counts = {}
    for h in hashes:
        severity = hash_to_severity[h]
        if severity not in severity_counts:
            severity_counts[severity] = 0
        severity_counts[severity] += 1
    component_severity_counts[comp_idx] = severity_counts

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

plt.figure(figsize=(10, 1.2))
im = plt.imshow(matrix, aspect='auto', interpolation='nearest', cmap=ListedColormap(custom_colors))


# Draw component boundaries and labels
offset = [0.5, 10, -5, 0.5, 0, 0, 0.5]
original_ylim = plt.ylim()
plt.plot([0 - 0.5, 0 - 0.5], [-0.5, -1], color='black', linewidth=1, clip_on=False)
plt.ylim(original_ylim)
for i, boundary in enumerate(component_boundaries):
    # Draw a small vertical line at the top
    plt.axvline(x=boundary - 0.5, color='black', linewidth=1, clip_on=False)
    original_ylim = plt.ylim()
    plt.plot([boundary - 0.5, boundary - 0.5], [-0.5, -0.8], color='black', linewidth=1, clip_on=False)
    plt.ylim(original_ylim)
    last_boundary = component_boundaries[i-1] if i > 0 else 0
    label_pos = (boundary + last_boundary) / 2 - offset[i]
    # y_offset = -1 if i in (2, 6) else 0.1
    plt.text(label_pos, -1.2, COMPONENTS[i], ha='center', va='center')

plt.plot([0-0.5,boundary-0.5], [-0.75, -0.75], color='black', linewidth=1, clip_on=False)

# Add severity count annotations for each component
severity_id_to_name = {v: k for k, v in GROUP_TO_IDX.items()}
for comp_idx, severity_counts in component_severity_counts.items():
    start_pos = component_boundaries[comp_idx - 1] if comp_idx > 0 else 0
    end_pos = component_boundaries[comp_idx]
    
    # Track position within component for each severity
    current_pos = start_pos
    for severity_id in sorted(severity_counts.keys()):
        count = severity_counts[severity_id]
        severity_name = severity_id_to_name[severity_id]
        severity_row = GROUP_TO_IDX[severity_name]
        
        # Position text at the center of this severity group
        center_x = current_pos + count / 2
        
        # Add text annotation on the matrix
        if count > 5:  # Only show if there's enough space
            plt.text(center_x, severity_row, str(count), 
                    ha='center', va='center', fontsize=10, 
                    color='white', weight='bold')
        
        current_pos += count

plt.xlabel("Commits (group by component)", labelpad=1)
plt.yticks(np.arange(len(groupnames)), groupnames, rotation=0)

plt.tick_params(which='both', length=2)

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

plt.tight_layout(pad=0.)
plt.savefig("consequence.pdf")
