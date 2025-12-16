import json
import argparse
from matplotlib import pyplot as plt
from matplotlib import gridspec
import numpy as np
from util import *
from component_count import component_count

def get_versions(min_version="v3.3", max_version="v6.18", step = 5):
    # List all tags
    tag_lines = system_output(
        f"git -C {LINUX_MAINLINE_DIR} tag -l v[2-6]*"
    ).splitlines()
    tags = [tag for tag in tag_lines if '.' in tag and '-rc' not in tag and '-tree' not in tag]

    # Filter tags by min and max version and select based on the step
    min_vt = version_tuple(min_version)
    max_vt = version_tuple(max_version)
    filtered_tags = sorted(
        [tag for tag in tags if min_vt <= version_tuple(tag) <= max_vt],
        key=version_tuple
    )[::-1][::step][::-1]

    return filtered_tags

def count_loc(version):
    system(f"git -C {LINUX_MAINLINE_DIR} checkout -fq {version}")
    if compare_versions(version, "v3.2"):
        sched_dir = LINUX_MAINLINE_DIR / "kernel"
        sched_pattern = lambda fn: fn.startswith("sched") and fn.endswith(".c")
    else:
        sched_dir = LINUX_MAINLINE_DIR / "kernel/sched"
        sched_pattern = lambda fn: fn != "Makefile"
    
    loc_result = {component: 0 for component in COMPONENT_SET}
    for fn in filter(sched_pattern, os.listdir(sched_dir)):
        component = file_to_component[fn]
        if component not in COMPONENT_SET:
            continue
        path = os.path.join(sched_dir, fn)
        loc = 0
        with open(path, encoding="latin1", errors="ignore") as f:
            loc += sum(1 for _ in f)
        loc_result[component] += loc
    return loc_result

def plot_complexity(versions, loc_results, component_counts):
    sorted_components = sorted(COMPONENT_SET, key=lambda x: COMPONENT_ORDER[x])
    component_colors = {
        "core": "#234C6A",
        "topology": "#AEDEFC",
        "account": "#648DB3",
        "fair": "#A72703",
        "deadline": "#FFE797",
        "rt": "#FCB53B",
        "": "#FFFFFF",
    }
    component_markers = {
        'core': 'p', 
        'fair': 's', 
        'topology': '^', 
        'deadline': 'v', 
        'account': 'o', 
        'rt': 'X'}


    # Build loc matrix: rows=components, columns=versions
    loc_matrix = []
    for version in versions:
        row = [loc_results[version][component] for component in sorted_components]
        loc_matrix.append(row)
    loc_matrix = list(zip(*loc_matrix))  # shape: comps x versions

    # Calculate percentage of codes and bugs
    percentage_of_codes = {}
    for i in range(len(sorted_components)):
        percentage_of_codes[sorted_components[i]] = loc_matrix[i][-1] / sum(loc_matrix[:][-1])
    percentage_of_bugs = {}
    for i in range(len(sorted_components)):
        percentage_of_bugs[sorted_components[i]] = component_counts[sorted_components[i]] / sum(component_counts.values())
    
    # Plot the complexity
    fig = plt.figure(figsize=(4.3, 1.3))
    gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1], height_ratios=[11, 1],  bottom=0.31, wspace=0.2)

    # Bar plot (left)
    ax = fig.add_subplot(gs[0, 0])
    bottom = [0] * len(versions)
    bars = []
    for i, comp in enumerate(sorted_components):
        heights = [loc_matrix[i][j] for j in range(len(versions))]
        bar = ax.bar(versions, heights, label=comp, bottom=bottom, color=component_colors[comp], width=0.8)
        bottom = [b + h for b, h in zip(bottom, heights)]
        bars.append(bar)
    ax.set_xlim(0 - 0.5, len(versions))
    ax.set_yticks(np.arange(0, max(bottom) + 20000, 20000))
    ax.set_yticklabels([f"{int(y/1000)}k" for y in ax.get_yticks()])
    ax.set_xticks(np.arange(0, len(versions), 1))
    ax.set_xticklabels([v[1:] for v in versions], rotation=90)
    ax.tick_params(axis='both', which='major', labelsize=8, pad=0.1)
    ax.xaxis.labelpad = 1.3
    ax.yaxis.labelpad = 1.3
    ax.set_title("(a) LoC across versions", fontsize=9, pad=1)

    # Scatter plot (right)
    ax_scatter = fig.add_subplot(gs[0, 1])
    jitter_offsets = {
        'core':   (0.00,  0.0),   
        'fair':   (0.00, -0.0),   
        'topology': (0.03, 0.03),  
        'deadline': (-0.012, 0.01), 
        'account': (0.01, 0.01), 
        'rt':    (-0.02,  0.0),
    }
    for i, comp in enumerate(sorted_components):
        x = percentage_of_codes[comp]
        y = percentage_of_bugs[comp]
        ax_scatter.scatter(x + jitter_offsets[comp][0], y + jitter_offsets[comp][1], 
                          color=component_colors[comp], 
                          marker=component_markers[comp], 
                          edgecolor='black', 
                          linewidth=0.5, 
                          label=comp, 
                          s=50, 
                          zorder=3)
    ax_scatter.axline((0, 0), slope=1, color="gray", linestyle="--", lw=1, zorder=0)
    ax_scatter.set_xlabel("% of code", fontsize=8)
    ax_scatter.set_ylabel("% of bugs", fontsize=8)
    ax_scatter.set_xlim(0, 0.50)
    ax_scatter.set_ylim(0, 0.50)
    ax_scatter.grid(axis="both", linestyle=":", alpha=0.4, zorder=0)
    ax_scatter.set_yticks([i * 0.1 for i in range(6)])
    ax_scatter.set_yticklabels([int(i * 10) for i in range(6)])
    ax_scatter.set_xticks([i * 0.1 for i in range(6)])
    ax_scatter.set_xticklabels([int(i * 10) for i in range(6)])
    ax_scatter.tick_params(axis='both', which='major', labelsize=8, pad=0.1)
    ax_scatter.xaxis.labelpad = 1.3
    ax_scatter.yaxis.labelpad = 1.3
    ax_scatter.set_title("(b) Bug vs. Code", fontsize=9, pad=1)

    # plot legend
    ax_leg = fig.add_subplot(gs[1, :])
    ax_leg.axis("off")
    legend_handles = []
    for i, comp in enumerate(sorted_components):
        marker = component_markers[comp]
        color = component_colors[comp]
        legend_handles.append(plt.Line2D([0], [0], 
                              color='w', markerfacecolor=color, 
                              marker=marker, markersize=10,
                              markeredgecolor='black', markeredgewidth=0.1))
    ax_leg.legend(legend_handles, 
                  sorted_components, 
                  fontsize=8, 
                  loc="center",
                  ncol=6,
                  bbox_to_anchor=(0.45, -5),
                  columnspacing=0.5,
                  handletextpad=0, borderpad=0,
                  frameon=False,
                  markerscale=1,
                )
    plt.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.4) 

    fig.savefig(RESULT_DIR / "complexity.pdf")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_version", type=str, default="v3.3")
    parser.add_argument("--max_version", type=str, default="v6.18")
    parser.add_argument("--step", type=int, default=5)
    parser.add_argument("--mode", choices=["count", "plot"], default="plot")
    args = parser.parse_args()

    versions = get_versions(args.min_version, args.max_version, args.step)

    if args.mode == "count":
        loc_results = {}
        for version in versions:
            loc_results[version] = count_loc(version)

        with open(RESULT_DIR / "loc_results.json", "w") as f:
            json.dump(loc_results, f)
    
    else:
        with open(RESULT_DIR / "loc_results.json", "r") as f:
            loc_results = json.load(f)
        for version, loc_result in loc_results.items():
            print(version, loc_result)
        component_counts = component_count()
        print(component_counts)
        plot_complexity(versions, loc_results, component_counts)


