import util

import csv
import subprocess
import os
from collections import Counter

fixes_file = "filtered_sched_fixes.csv"
linux_dir = "linux/master"

component_bug_counts = Counter()

with open(fixes_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        commit = row["hash"]
        components = util.get_components(commit)

        # Each bug (commit) counts for all the components it touches
        for component in components:
            component_bug_counts[component] += 1

# Print the number of bugs (fixes) per component
print("Bug count per component:")
for component, count in component_bug_counts.items():
    print(f"  {component}: {count}")
