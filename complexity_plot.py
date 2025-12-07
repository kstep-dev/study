import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import numpy as np

# Load LOC data by component for all versions
with open("sched_loc.json", "r") as f:
    data = json.load(f)

# Get all components from the data (union of all component keys)
all_components = set()
for version, compdict in data.items():
    all_components.update(compdict.keys())
all_components = sorted(all_components)

all_components = ["core", "topology",  "accounting",  "fair", "deadline", "rt"]

component_colors = {
    "core": "#87BAC3",
    # "clock": "#5459AC",
    "topology": "#648DB3",
    "accounting": "#53629E",
    # "Load estimation": "#84994F",
    "fair": "#A72703",
    "rt": "#FCB53B",
    "deadline": "#FFE797",
    "": "#FFFFFF",
}

component_bug_counts = {
    "core": 113,
    "topology": 11,
    "accounting": 16,
    "Load estimation": 6,
    "fair": 112,
    "rt": 14,
    "deadline": 26,
}


# Sort versions in version order (not lexicographic)
def version_key(v):
    t = v.lstrip('v').split('.')
    try:
        return tuple(int(x) for x in t)
    except:
        return (0,)
versions = sorted(data.keys(), key=version_key)

# Build matrix: rows=versions, columns=components
loc_matrix = []
for v in versions:
    row = [data[v].get(c, 0) for c in all_components]
    loc_matrix.append(row)
loc_matrix = list(zip(*loc_matrix))  # shape: comps x versions

percentage_of_codes = {}
for i in range(len(all_components)):
    percentage_of_codes[all_components[i]] = row[i] / sum(row)

percetage_of_bugs = {}
for i in range(len(all_components)):
    percetage_of_bugs[all_components[i]] = component_bug_counts[all_components[i]] / sum(component_bug_counts.values())

print(percentage_of_codes, percetage_of_bugs)

# ==== Use gridspec to separate plot and legend ====
fig = plt.figure(figsize=(4.3, 1.2))
# Use gridspec with two columns for side-by-side plots, and one small row for the legend
gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1], height_ratios=[11, 1],  bottom=0.33, wspace=0.2)

# Bar plot (left)
ax = fig.add_subplot(gs[0, 0])

# x axis selection
selected_indices = list(range(0, len(versions), 5))
selected_versions = [versions[i] for i in selected_indices]

# Bar plotting
bottom = [0] * len(selected_versions)
bars = []
for i, comp in enumerate(all_components):
    heights = [loc_matrix[i][j] for j in selected_indices]
    bar = ax.bar(selected_versions, heights, label=comp, bottom=bottom, color=component_colors[comp], width=0.8)
    bottom = [b + h for b, h in zip(bottom, heights)]
    bars.append(bar)

ax.set_xlim(0 - 0.5, len(selected_versions) )
ytick_vals = np.arange(0, max(bottom) + 10000, 10000)
ytick_labels = [f"{int(y/1000)}k" for y in ytick_vals if y != 0]
# Always keep 0 on axis
ytick_vals = [0] + [y for y in ytick_vals if y != 0]
ax.set_yticks(ytick_vals)
ax.set_yticklabels([str(0)] + ytick_labels)

# Only label every version where x.0 (e.g., 3.0, 4.0, ...)
tick_indices = []
tick_labels = []
for i, v in enumerate(selected_versions):
    parts = v.lstrip('v').split('.')
    if len(parts) >= 2:
        major, minor = parts[:2]
        try:
            minor_int = int(minor)
        except ValueError:
            continue
        tick_indices.append(i)
        tick_labels.append(v[1:])
ax.set_xticks(tick_indices)
ax.set_xticklabels(tick_labels, rotation=90)
ax.set_ylabel("LOC")
ax.tick_params(axis='both', which='major', labelsize=8, pad=0.1)
ax.xaxis.labelpad = 1.3  # Make xlabel closer
ax.yaxis.labelpad = 1.3  # Make ylabel closer
# ax.set_title("Component LOC by Version")

# Scatter subplot (right)
ax_scatter = fig.add_subplot(gs[0, 1])
# Prepare data for scatter
scatter_components = [c for c in all_components if c in component_bug_counts and c in percentage_of_codes]
x_vals = [percentage_of_codes[c] for c in scatter_components]
y_vals = [percetage_of_bugs[c] for c in scatter_components]
# Slight jitter for crowded markers to improve separation
import numpy as np

marker_styles = {'core': '*', 'fair': 's', 'topology': '^', 'deadline': 'v', 'accounting': 'o', 'rt': 'P', 'Load estimation': 'p'}

# Define manual jitter offsets (in data units) for visually crowded points
# Positive/negative values for tiny horizontal move; only adjust close points
jitter_offsets = {
    'core':   (0.00,  0.0),   
    'fair':   (0.00, -0.0),   
    'topology': (0.015, 0.00),  
    'deadline': (-0.012, 0.01), 
    'accounting': (0.023, 0.02), 
    'rt':    (0.00,  0.0),
    'Load estimation': (0.00, 0.002), # Down
}

for i, (c, x, y) in enumerate(zip(scatter_components, x_vals, y_vals)):
    dx, dy = jitter_offsets.get(c, (0.0, 0.0))
    ax_scatter.scatter(x + dx, y + dy, color=component_colors[c], marker=marker_styles[c], edgecolor='black', label=c, s=60, zorder=3)

ax_scatter.axline((0, 0), slope=1, color="gray", linestyle="--", lw=1, zorder=0)
ax_scatter.set_xlabel("% of code")
ax_scatter.set_ylabel("% of bugs")
ax_scatter.set_xlim(0, 0.41)
ax_scatter.set_ylim(0, 0.41)
ax_scatter.grid(axis="both", linestyle=":", alpha=0.4, zorder=0)
ax_scatter.set_yticks([0, 0.1, 0.2, 0.3])
ax_scatter.set_yticklabels([0, 10, 20, 30])
ax_scatter.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
ax_scatter.set_xticklabels([0, 10, 20, 30, 40])
ax_scatter.tick_params(axis='both', which='major', labelsize=8, pad=0.1)
# ax_scatter.set_title("Component bug rate vs. code size", fontsize=10, pad=5)
ax_scatter.xaxis.labelpad = 1.3  # Make xlabel closer
ax_scatter.yaxis.labelpad = 1.3  # Make ylabel closer

# set title for the subplots
ax_scatter.set_title("(b) Bug vs. Code", fontsize=10)
ax.set_title("(a) LOC across versions", fontsize=10)
# ax_scatter.xaxis.set_label_coords(0.5, -0.1)
# ax_scatter.yaxis.set_label_coords(-0.1, 0.5)

# Legend subplot (bottom spanning both columns)
ax_leg = fig.add_subplot(gs[1, :])
ax_leg.axis("off")
legend_labels = ["core",  "topology", "accounting", "fair", "deadline",  "rt"]

legend_handles = []
for i, c in enumerate(legend_labels):
    # Use the marker and color for each component
    marker = marker_styles[c]
    color = component_colors[c]
    handle = plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color, markeredgecolor='black', markersize=10, linewidth=0)
    legend_handles.append(handle)
# Move the legend lower by decreasing the bbox_to_anchor y-value
ax_leg.legend(
    legend_handles,
    ["core", "topology", "acct", "fair", "deadline",  "rt"],
    loc="center",
    ncol=6,
    # fontsize=7,
    bbox_to_anchor=(0.45, -6),  # moved further down
    columnspacing=0.5,
# INSERT_YOUR_CODE
    handletextpad=0, borderpad=0,  # make legend patch separation smaller
    frameon=False,
)
# plt.subplots_adjust(hspace=0.06, bottom=0.3)  # increased bottom margin to fit legend

# INSERT_YOUR_CODE
plt.subplots_adjust(left=0.06, right=0.98, top=0.85, bottom=0.5) 

# plt.tight_layout(pad = 0)
plt.savefig("sched_loc_by_component.pdf")
