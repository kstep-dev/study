import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

import util
# Get version names (ordered, as in get_fixes.py)
linux_versions = [
    "master",
    "linux-6.12.y",
    "linux-6.6.y",
    "linux-6.1.y",
    "linux-5.15.y",
    "linux-5.10.y",
    "linux-5.4.y",
]
linux_versions.reverse()

# Read fixes data
fixes = []
with open("sched_fixes.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Each row: title, hash, tree, url, backport, buggy_sha, buggy_tag
        # tree and backport are ";" separated lists
        trees = row["tree"].split(";") if row["tree"] else []
        components = util.get_components(row["hash"])
        if "ext" in components or "wait" in components or "mem" in components or "psi" in components:
            continue
        fixes.append({
            "title": row["title"],
            "hash": row["hash"],
            "tree": trees,
            "url": row["url"],
            "backport": row["backport"].split(";") if row["backport"] else [],
            "buggy_tag": row["buggy_tag"],
            "components": components
        })

# Each commit will be a column, each version is a row
fixes_sorted = fixes
n_commits = len(fixes_sorted)
n_versions = len(linux_versions)

matrix = np.zeros((n_versions, n_commits), dtype=int)

years = []
for col, fix in enumerate(fixes_sorted):
    for row, v in enumerate(linux_versions):
        if v in fix["tree"]:
            matrix[row, col] = 1
        if v in fix["backport"]:
            matrix[row, col] = 2

    years.append(util.get_year(fix["hash"]))

    # Additional logic for plotting 3 according to the given rule
    # Find the top-most version in tree/backport (smallest row index, due to reversed version order: oldest at row 0)
    all_versions = fix["tree"] + fix["backport"]
    # print(all_versions)
    if all_versions and fix["buggy_tag"]:
    #     # Only consider versions from linux_versions
        all_versions_in_list = [x for x in all_versions if x in linux_versions]
        if all_versions_in_list:
            last_idx = min(linux_versions.index(x) for x in all_versions_in_list if x in linux_versions)
            if linux_versions[last_idx] == "master":
                last_version_main = 6
                last_version_minor = 18
            else:
                last_version_main = int(linux_versions[last_idx][6:-2].split(".")[0])
                last_version_minor = int(linux_versions[last_idx][6:-2].split(".")[1])
            if "~" in fix["buggy_tag"]:
                buggy_version_main = int(fix["buggy_tag"].split("~")[0][1:].split(".")[0])
                buggy_version_minor = int(fix["buggy_tag"].split("~")[0][1:].split(".")[1])
            else:
                buggy_version_main = int(fix["buggy_tag"][1:].split(".")[0])
                buggy_version_minor = int(fix["buggy_tag"][1:].split(".")[1])

            # print(last_idx, linux_versions[last_idx], last_version, fix["buggy_tag"], buggy_version)
            rows_to_mark = []
            for row, version in enumerate(linux_versions):
                if version == "master": continue
                version_main = int(version[6:-2].split(".")[0])
                version_minor = int(version[6:-2].split(".")[1])
                if [version_main, version_minor] < [last_version_main, last_version_minor] and [version_main, version_minor] >= [buggy_version_main, buggy_version_minor]:
                    # if matrix[row, col] == 0:
                    # if (row == 6 and matrix[5, col] != 3):
                    #     continue
                    # print(version, linux_versions[last_idx], fix["buggy_tag"], fix["hash"])
                    rows_to_mark.append(row)                    
                    # matrix[row, col] = 3
            
            if len(rows_to_mark) == 0 or (len(rows_to_mark) == 1 and rows_to_mark[0] == 0):
                continue
            print(fix["hash"], fix["components"], fix["title"], rows_to_mark)
            for row in rows_to_mark:
                matrix[row, col] = 3


plt.figure(figsize=(5, 1.6))
# im = plt.imshow(matrix, aspect='auto', cmap='Blues', interpolation='none')
# plt.xlabel("Fix Commits Index (sorted by time)", labelpad=1)
# plt.ylabel("Kernel version (tree)")

# Set y tick labels to version numbers only (remove 'linux-' or 'master')
yticklabels = [v.replace("linux-", "") if v != "master" else "master" for v in linux_versions]
plt.yticks(range(n_versions), yticklabels)

plt.tick_params(axis='x', which='major', pad=0.1, length=2)


# Define a discrete colormap with 3 distinct colors (no gradient)
cmap = ListedColormap(['#ffffff', '#4f98c6', '#184478', '#FCB53B'])  # example: white, blue, dark blue, black
bounds = [0, 1, 2, 3, 4]  # to separate 0, 1, 2, 3 as blocks
norm = BoundaryNorm(bounds, cmap.N)

im = plt.imshow(matrix, aspect='auto', cmap=cmap, norm=norm, interpolation='nearest')  # overwrite with new cmap/norm

# plt.xticks([i for i in range(0, n_commits, 20)], [str(i) for i in range(0, n_commits, 20)])
plt.xticks([])
print(years)
# Mark the year in the figure. We assume 'years' is a list with year labels for each column (commit).
# We'll put a vertical line (or annotation) at the first commit of each new year.
years = sorted(years, reverse=True)
if isinstance(years, list) and len(years) == n_commits:
    last_year = None
    last_idx = 0
    for idx, year in enumerate(years):
        if year != last_year and year >= "2020":
            # Draw a vertical line and annotate the year
            # plt.axvline(x=idx-0.5, color='red', linestyle='--', linewidth=1, alpha=0.7, zorder=0)
            origin_ylim = plt.ylim()
            plt.plot([idx, idx], [-2, -0.5], color='black', clip_on=False)
            plt.ylim(origin_ylim[0], origin_ylim[1])
            plt.text(idx + 3, -1.2, str(year), ha='left', va='center', color='black', fontsize=10, rotation=0, zorder=5)
            last_year = year
            last_idx = idx
origin_ylim = plt.ylim()
plt.plot([idx, idx], [-3, -0.5], color='black', clip_on=False)
plt.ylim(origin_ylim[0], origin_ylim[1])
cbar = plt.colorbar(
    im, 
    ticks=[0, 1, 2, 3], 
    boundaries=bounds, 
    orientation='horizontal', 
    pad=0.03,
    # fraction=0.08
)
positions = [0.5, 1.5, 2.5, 3.5]
labels = ['No bug', 'Mainline fixed', 'Backport fixed', 'Backport miss']

cbar.set_ticks([])
colors = ['black', 'black', 'white', 'black']

for pos, label in zip(positions, labels):
    cbar.ax.text(
        pos, 0.5, label,
        ha='center', va='center',
        fontsize=10,
        color=colors[int(pos-0.5)],
        transform=cbar.ax.transData
    )

# Crop the whitespace on the right of the colorbar by adjusting its position
# Get the current position of the colorbar axes
# box = cbar.ax.get_position()
# Make it a bit narrower and move left
# cbar.ax.set_position([box.x0, box.y0 - 0.015, box.width, box.height])

plt.tight_layout(pad=0.3)
plt.savefig("bug_versions.pdf", dpi = 1000)
