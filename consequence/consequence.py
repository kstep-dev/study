from util import * 
import numpy as np
import matplotlib.pyplot as plt

def collect_consequence_data(consequence_mapping, group_to_idx):
    data = read_data()
    hashes = list(data.keys())

    group_warning_counts = np.zeros((len(group_to_idx), len(WARNING_TO_IDX)), dtype=int)
    
    print(group_warning_counts.shape)

    for hash in hashes:
        consequences = data[hash]["consequence"]
        warnings = data[hash]["visibility"]
        for consequence in consequences:
            if consequence not in consequence_mapping.keys():
                continue
            group_name = consequence_mapping[consequence]
            group_idx = group_to_idx[group_name]
            group_warning_counts[group_idx, WARNING_TO_IDX[warnings]] += 1

    # Sort by total
    total_counts = group_warning_counts.sum(axis=1)
    sorted_indices = np.argsort(-total_counts)
    sorted_group_warning_counts = group_warning_counts[sorted_indices, :]

    idx_to_groupname = {v: k for k, v in group_to_idx.items()}
    sorted_group_names = [idx_to_groupname[i] for i in sorted_indices]

    return sorted_group_warning_counts, sorted_group_names

def plot_stacked_bars(ax, sorted_group_warning_counts, sorted_group_names, 
                      title, warning_colors):
    warning_types = ["panic", "warning", "silent"]
    bottom = np.zeros(len(sorted_group_names))

    for i in range(len(warning_types)):
        for j in range(len(sorted_group_names)):
            count = sorted_group_warning_counts[j, i]
            if count > 0:
                ax.bar(j, count, bottom=bottom[j], width=0.8, 
                       color=warning_colors[i])
                bottom[j] += count

    ax.set_xticks(range(len(sorted_group_names)))
    ax.set_xticklabels(sorted_group_names, rotation=40, ha='right')
    ax.set_title(title, fontsize=10)
    if title == "(a) Functionality Bugs":
        ax.set_ylabel("#Bugs")
    else:
        ax.set_ylabel("")
        ax.set_yticks([])
    ax.set_ylim(0, 55)

    # Add count labels
    for i in range(len(sorted_group_names)):
        y = 0
        for j in range(len(warning_types)):
            count = sorted_group_warning_counts[i, j]
            if count > 5:
                ax.text(i, y + count/2, str(count), ha='center', va='center', 
                       fontsize=9, color="white" if j==0 else "black")
    

if __name__ == "__main__":
    fig, (ax1, ax2) = plt.subplots(1, 2, 
                                   figsize=(5.2, 0.8), 
                                   gridspec_kw={'wspace': 0.05, 'width_ratios': [1, 1]}
                                   )
    sorted_group_warning_counts, sorted_group_names = collect_consequence_data(CONSEQUENCE_TO_GROUP_FUNC, GROUP_TO_IDX_FUNC)
    plot_stacked_bars(ax1, sorted_group_warning_counts, sorted_group_names, "(a) Functionality Bugs", ["#BF092F", "#FA812F", "#FFCB61"])
    sorted_group_warning_counts, sorted_group_names = collect_consequence_data(CONSEQUENCE_TO_GROUP_POLICY, GROUP_TO_IDX_POLICY)
    plot_stacked_bars(ax2, sorted_group_warning_counts, sorted_group_names, "(b) Policy Bugs", ["#BF092F", "#658C58", "#BBC863"])
    plt.tight_layout(pad=0.)
    plt.savefig(RESULT_DIR / "consequence.pdf", bbox_inches='tight', pad_inches=0.01)