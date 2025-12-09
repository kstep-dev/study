import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
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

# --- Prepare Data for Bar Charts ---
# Organize consequence counts by component AND warning type
severity_id_to_name = {v: k for k, v in GROUP_TO_IDX.items()}
warning_id_to_name = {v: k for k, v in ObservedWarnings.items()}
component_data = []

for comp_idx in range(len(COMPONENTS)):
    comp_name = COMPONENTS[comp_idx]
    hashes = component_to_hash.get(comp_idx, [])
    
    # Initialize counts for all severity levels and warning types
    counts_by_severity_warning = {
        name: {'panic': 0, 'warning': 0, 'silent': 0} 
        for name in groupnames
    }
    
    # Count bugs by both consequence group and warning type
    for h in hashes:
        severity = hash_to_severity[h]
        warning_id = hash_to_warning[h]
        warning_type = warning_id_to_name[warning_id]
        
        if severity in severity_id_to_name:
            severity_name = severity_id_to_name[severity]
            counts_by_severity_warning[severity_name][warning_type] += 1
    
    component_data.append({
        'name': comp_name,
        'counts': counts_by_severity_warning
    })

# --- Colors for consequence groups and warning types ---
# Base colors for consequence groups
consequence_base_colors = {
    'Func. Crash/Hang': {'panic':'#BF092F', 'warning':'#FA812F', 'silent':'#80A1BA'},
    'Func. Non-fatal': {'panic':'#BF092F', 'warning':'#FA812F', 'silent':'#FFCB61'},
    'Policy. With Effect': {'panic':'#BF092F', 'warning':'#658C58', 'silent':'#BBC863'},
    'Policy. Benign': {'panic':'#BF092F', 'warning':'#7A7A73', 'silent':'#EEEEEE'},
}

# Create color variations for warning types (darker to lighter)
def get_warning_color(group_name, warning_type):
    """Generate color variations for warning types."""
    print(group_name, warning_type)
    return consequence_base_colors[group_name][warning_type]

warning_types = ['panic', 'warning', 'silent']

# --- Plotting Percentage-based Horizontal Stacked Bar Chart ---
fig, ax = plt.subplots(figsize=(4.8, 1.8))

# Reverse component order so core is at top, and add "Total" at bottom
COMPONENTS_LABELS = [
    "core",
    "topology",
    "account",
    "fair",
    "deadline",
    "rt",
    # "load est.",
]
component_labels_reversed = ['Total'] + COMPONENTS_LABELS[::-1]
y_pos = np.arange(len(component_labels_reversed))
bar_height = 1

# Calculate percentages (including total) with warning type subdivisions
left = np.zeros(len(component_labels_reversed))
# Create separate lists for legend organization by group
legend_dict = {group: {'elements': [], 'labels': []} for group in groupnames}

for group_name in groupnames:
    for warning_type in warning_types:
        # Skip panic for non-Crash/Hang groups
        if warning_type == 'panic' and group_name != 'Func. Crash/Hang':
            continue
        # Skip warning/silent for Crash/Hang group
        if (warning_type == 'warning' or warning_type == 'silent') and group_name == 'Func. Crash/Hang':
            continue
            
        # Get counts for this consequence group and warning type
        counts = np.array([comp['counts'][group_name][warning_type] for comp in component_data])
        # Calculate total bugs per component
        totals = np.array([sum(sum(comp['counts'][g].values()) for g in groupnames) for comp in component_data])
        percentages = np.divide(counts, totals, where=totals!=0, out=np.zeros_like(counts, dtype=float)) * 100
        
        # Calculate total percentage
        total_count = sum(counts)
        total_all = sum(totals)
        total_pct = (total_count / total_all * 100) if total_all > 0 else 0
        
        # Reverse order: Total first, then reversed components
        percentages_reversed = np.concatenate([[total_pct], percentages[::-1]])
        counts_reversed = np.concatenate([[total_count], counts[::-1]])
        
        # Get color for this warning type
        color = get_warning_color(group_name, warning_type)
        
        bars = ax.barh(y_pos, percentages_reversed, bar_height,
                        left=left, color=color,
                        edgecolor='gray', linewidth=0.01)
        
        # Add to legend organized by group
        legend_dict[group_name]['elements'].append(bars[0])
        legend_dict[group_name]['labels'].append(f'{warning_type.capitalize()}')
        
        # Add percentage labels
        for i, (bar, pct, count) in enumerate(zip(bars, percentages_reversed, counts_reversed)):
            if pct > 3:  # Only show label if segment is large enough
                x_pos = left[i] + pct / 2
                if warning_type == 'silent':
                    color = 'black'
                else:
                    color = 'white'
                ax.text(x_pos, bar.get_y() + bar.get_height() / 2.4,
                        f'{int(count)}', ha='center', va='center',
                        color=color)
        
        left += percentages_reversed

# Reorganize legend elements and labels: 4 columns, 2 rows
# Need to use mode to control layout - matplotlib fills column by column with ncol
# We want:
# Col 1: Crash/Hang Panic + blank
# Col 2: Non-fatal Warning + Non-fatal Silent  
# Col 3: With Effect Warning + With Effect Silent
# Col 4: Benign Warning + Benign Silent

legend_elements = []
legend_labels = []

# Using ncol=4 fills row by row, so we add items in row order
# Row 1 (items 0-3): one from each column
legend_elements.append(legend_dict['Func. Crash/Hang']['elements'][0])
legend_labels.append('Func.Crash/Hang\n    Panic')

# Row 2 (items 4-7): second from each column
legend_elements.append(plt.Rectangle((0, 0), 1, 1, fc='none', ec='none', linewidth=0, alpha=0))
legend_labels.append('')


legend_elements.append(legend_dict['Func. Non-fatal']['elements'][0])
legend_labels.append('Func. Non-fatal\n    Warning')

legend_elements.append(legend_dict['Func. Non-fatal']['elements'][1])
legend_labels.append('    Silent')


legend_elements.append(legend_dict['Policy. With Effect']['elements'][0])
legend_labels.append('Policy. With Effect\n    Warning')

legend_elements.append(legend_dict['Policy. With Effect']['elements'][1])
legend_labels.append('    Silent')


legend_elements.append(legend_dict['Policy. Benign']['elements'][0])
legend_labels.append('Policy. Benign\n    Warning')

# # Row 2 (items 4-7): second from each column
# legend_elements.append(plt.Rectangle((0, 0), 1, 1, fc='none', ec='none', linewidth=0, alpha=0))
# legend_labels.append('')

legend_elements.append(legend_dict['Policy. Benign']['elements'][1])
legend_labels.append('    Silent')

# Add a separator line between Total and components
# Extend line to the left to include y-axis labels area
ax.plot([-25, 100], [0.5, 0.5], color='black', linewidth=1., linestyle='-', zorder=10, clip_on=False)

# Customize percentage plot
# ax.set_ylabel('Component')
# ax.set_xlabel('Percentage (%)')
ax.set_ylim(bottom=-0.5, top = 6.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(component_labels_reversed)
ax.set_xlim(0, 100)
ax.set_xticks([])
# ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], fontsize=8)
ax.tick_params(which='both', length=0.1)
legend = ax.legend(legend_elements, legend_labels, loc='upper center', bbox_to_anchor=(0.44, -0.),
           frameon=False, ncol=4, handlelength=0.9, columnspacing=1.3, handletextpad=-1, fontsize=9.5,
           labelspacing=0.1, borderpad=0.
           )

# Align all legend handlers to the top of text and adjust vertical position
for vpack in legend._legend_handle_box.get_children():
    for hpack in vpack.get_children():
        hpack.align = 'bottom'

# Adjust handler vertical offset by modifying the text position
for text in legend.get_texts():
    # text.set_verticalalignment('top')
    text.set_y(text.get_position()[1] - 1)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout(pad = 0.1)
plt.savefig("consequence_bar_percentage.pdf", bbox_inches=0.0)
plt.savefig("consequence_bar_percentage.png", dpi=300, bbox_inches=0.0)

plt.show()
