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

foundation_components = ["core", "clock", "topology",  "accounting"]
policy_components = ["pelt", "fair", "rt", "deadline"]

# Dictionary to hold diffs per component
diffs_foundation = []
diffs_policy = []
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
            if any(x in components for x in foundation_components):
                diffs_foundation.append(diff.days)
            if any(x in components for x in policy_components):
                diffs_policy.append(diff.days)

# Prepare the plot
plt.figure(figsize=(4.5,1.4))
colors = plt.cm.tab10.colors
print(len(diffs_foundation))
print(len(diffs_policy))
plt.plot(sorted(diffs_foundation), [i / len(diffs_foundation) * 100 for i in range(len(diffs_foundation))], 
        label="Scheduler Foundation", linestyle="--",
        color="#31326F")
plt.plot(sorted(diffs_policy), [i / len(diffs_policy) * 100 for i in range(len(diffs_policy))], 
        label="Scheduling Policy", 
        color="#4FB7B3")
plt.legend()

# plt.xscale('log')
plt.yticks([0, 25, 50, 75, 100])
plt.ylim(0, 105)
plt.xlim(0, 6000)
plt.legend(loc="upper left")
plt.xscale('log')
plt.xlim(1, 10000)  # set xlim so that log scale works (no 0)

plt.xlabel("Bug lifetime (days)")
plt.ylabel("Percent of bugs")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout(pad = 0)
plt.savefig("buggy_time.pdf")





