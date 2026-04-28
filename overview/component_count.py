import csv
from collections import Counter
import matplotlib.pyplot as plt
from util import *

TABLE_ROWS = [
    ("Core", "Skeleton and orchestration among sched classes", "core"),
    ("Topology", "Builds the hierarchy of scheduling domains", "topology"),
    ("Account", "CPU time accounting and cgroup CPU statistics", "account"),
    ("Fair", "Fair scheduling via vruntime and load balancing", "fair"),
    ("RT", "Fixed-priority real-time scheduling", "rt"),
    ("Deadline", "Earliest deadline wins scheduling", "deadline"),
]

def component_count():
    component_bug_counts = Counter()
    hashes = list(read_data().keys())
    for hash in hashes:
        components = get_components(hash)

        for component in components:
            component_bug_counts[component] += 1

    return component_bug_counts

def plot_component_table(component_bug_counts):
    fig, ax = plt.subplots(figsize=(10.5, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Column anchors
    x_component = 0.14
    x_resp = 0.25
    x_bug = 0.94

    # Horizontal rules
    y_top = 0.89
    y_header = 0.80
    y_group_split = 0.51
    y_bottom = 0.22
    for y in (y_top, y_header, y_group_split, y_bottom):
        ax.hlines(y, 0.03, 0.97, color="black", linewidth=1.0)

    # Header
    ax.text(x_component, 0.84, "Type", ha="center", va="center", fontsize=15, fontweight="bold", family="serif")
    ax.text(x_resp, 0.84, "Responsibilities", ha="left", va="center", fontsize=15, fontweight="bold", family="serif")
    ax.text(x_bug, 0.84, "#Bug", ha="center", va="center", fontsize=15, fontweight="bold", family="serif")

    row_ys = [0.76, 0.67, 0.58, 0.45, 0.36, 0.27]

    for y, (label, responsibility, key) in zip(row_ys, TABLE_ROWS):
        ax.text(x_component, y, label, ha="center", va="center", fontsize=15, family="serif")
        ax.text(x_resp, y, responsibility, ha="left", va="center", fontsize=15, family="serif")
        ax.text(x_bug, y, str(component_bug_counts[key]), ha="center", va="center", fontsize=15, family="serif")
        
    save_figure_variants(fig, "Tab1_component", bbox_inches="tight", pad_inches=0.03)

if __name__ == "__main__":
    component_bug_counts = component_count()
    print(component_bug_counts)
    plot_component_table(component_bug_counts)
