from typing import Any

import util

import csv
import subprocess
import os
from collections import Counter

fixes_file = "sched_fixes.csv"
linux_dir = "linux/master"

import matplotlib.pyplot as plt
import numpy as np

from collections import defaultdict

foundation_components = ["core", "topology",  "accounting"]
policy_components = ["fair", "rt", "deadline"]

diff_dict = {
    "core": [],
    # "clock": [],
    "topology": [],
    "accounting": [],
    # "load est.": [],
    "fair": [],
    "rt": [],
    "deadline": [],
}

# Dictionary to hold diffs per component
diffs_foundation = []
diffs_policy = []
diff_commits = []
with open(fixes_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        commit = row["hash"]
        
        # Get files touched by this commit, limit to kernel/sched/
        components = util.get_components(commit)
        # Skip unwanted components
        if any(x in components for x in ["ext", "wait", "mem", "psi", "power"]):
            continue
        
        if row["buggy_tag"]:
            buggy_tag = row["buggy_sha"]
            diff = util.get_date_diff(buggy_tag, commit)
            for component in components:
                diff_dict[component].append(diff.days)

fig, axes = plt.subplots(1, 2, figsize=(4.2, 1.2), sharex=True, sharey=True)
colors = plt.cm.tab20.colors

foundation = ["core", "topology", "accounting"]
policy = ["fair", "rt", "deadline"]

ax0 = axes[0]
for idx, component in enumerate(foundation):
    data = sorted(diff_dict[component])
    if data:
        y_vals = [i / len(data) * 100 for i in range(len(data))]
        ax0.plot(data, y_vals, label=component, color=colors[idx])
ax0.set_title("(a) Scheduler Framework", fontsize=10)
ax0.set_xlim(1, 7000)
ax0.set_ylim(0, 105)
ax0.set_ylabel("% of bugs")
ax0.set_xlabel("Bug lifetime (days)", labelpad=0)
ax0.set_xscale('log')
ax0.set_yticks([0, 50, 100])
ax0.set_yticklabels(["0", "50", "100"])
ax0.tick_params(axis = 'both', length=1)
ax0.grid(True, linestyle='--', alpha=0.5)
ax0.legend(loc='upper left', frameon=False, borderpad=0, handlelength=0.2, handletextpad=0.2,  labelspacing=0.12, ncol = 2, columnspacing=0.5)

ax1 = axes[1]
for idx, component in enumerate(policy):
    data = sorted(diff_dict[component])
    if data:
        y_vals = [i / (len(data) - 1) * 100 for i in range(len(data))]
        ax1.plot(data, y_vals, label=component, color=colors[idx+len(foundation)])
ax1.set_title("(b) Scheduler Classes", fontsize=10)
ax1.set_xlim(1, 7000)
ax1.set_ylim(0, 105)
ax1.set_xlabel("Bug lifetime (days)", labelpad=0)
ax1.set_xscale('log')
ax1.set_yticks([0, 50, 100])
ax1.tick_params(axis = 'both', length=1)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper left', frameon=False, borderpad=0, handlelength=0.2, handletextpad=0.2, labelspacing=0.15, ncol = 2, columnspacing=0.5)
# ax1.set_yticklabels([])

plt.tight_layout(pad=0.1)
plt.savefig("buggy_time.pdf")

