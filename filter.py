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
skip_components = {"ext", "wait", "mem", "psi", "power"}

with open(fixes_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        commit = row["hash"]

        # Get files touched by this commit, limit to kernel/sched/
        components = util.get_components(commit)
        # Filter out rows if any unwanted component is present
        if any(comp in skip_components for comp in components):
            continue


        # INSERT_YOUR_CODE
        print(commit, components)   
        # Copy all other rows (that pass the component filter) and save into another file
        with open("filtered_sched_fixes.csv", "a", encoding="utf-8", newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            # Write header only if the file is empty
            if fout.tell() == 0:
                writer.writeheader()
            writer.writerow(row)



