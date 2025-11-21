import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json

# Load LOC data by component for all versions
with open("sched_loc.json", "r") as f:
    data = json.load(f)

# Get all components from the data (union of all component keys)
all_components = set()
for version, compdict in data.items():
    all_components.update(compdict.keys())
all_components = sorted(all_components)

all_components = ["core", "clock", "topology",  "accounting", "pelt", "fair", "rt", "deadline"]

color_map = {
    "core": "#52357B",
    "clock": "#5459AC",
    "topology": "#648DB3",
    "special tasks": "#B2D8CE",
    "CPU behavior control": "#B0DB9C",
    "accounting": "#CAE8BD",
    "pelt": "#A76545",
    "fair": "#BE3D2A",
    "rt": "#E78B48",
    "deadline": "#F5C45E",
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

import itertools
component_colors = {c: color_map[c] for c in all_components}

import numpy as np

# ==== Use gridspec to separate plot and legend ====
fig = plt.figure(figsize=(5, 2.3))
gs = gridspec.GridSpec(2, 1, height_ratios=[8, 1])

# Main bar plot
ax = fig.add_subplot(gs[0])

# x axis selection
selected_indices = list(range(0, len(versions), 3))
selected_versions = [versions[i] for i in selected_indices]

# Bar plotting
bottom = [0] * len(selected_versions)
bars = []
for i, comp in enumerate(all_components):
    heights = [loc_matrix[i][j] for j in selected_indices]
    bar = ax.bar(selected_versions, heights, label=comp, bottom=bottom, color=component_colors[comp])
    bottom = [b + h for b, h in zip(bottom, heights)]
    bars.append(bar)

# ax.set_xlabel("Linux Version")
# ax.set_ylabel("LOC")
ax.set_xlim(0 - 0.5, len(selected_versions) + 0.5)
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
        tick_labels.append(v)
ax.set_xticks(tick_indices)
ax.set_xticklabels(tick_labels, rotation=90)
# plt.setp(ax.get_xticklabels(), visible=Fals/e)  # hide xlabels for plot, draw them only on legend row

# plt.tight_layout(pad=0.5)  # leave a bit of space

# Legend subplot
ax_leg = fig.add_subplot(gs[1])
ax_leg.axis("off")
# Place the legend in the empty subplot
legend_handles = []
for c in all_components:
    # create patch for each component
    patch = plt.Rectangle((0,0),1,1, color=component_colors[c])
    legend_handles.append(patch)
ax_leg.legend(
    legend_handles,
    all_components,
    # title="Component",
    loc="center",
    ncol=4,
    # fontsize='small',
    bbox_to_anchor=(0.5, -1.3),
)
# Add xlabels for the plot below legend, in ax_leg:
# ax_leg.set_xticks(tick_indices)
# ax_leg.set_xticklabels(tick_labels, rotation=90)
# ax_leg.tick_params(axis='x', which='both', length=0)  # no tick marks

plt.subplots_adjust(hspace=0.06, bottom=0.2)

plt.tight_layout(pad=0)
plt.savefig("sched_loc_by_component.pdf")
