from util import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def collect_trigger_condition_data():
    data = read_data()
    hashes = list(data.keys())

    group_trigger_condition_counts = {} # comb of groups: count 

    for hash in hashes:
        trigger_conditions = data[hash]["trigger_condition"]
        comb = [0, 0, 0, 0]
        for trigger_condition in trigger_conditions:
            group = TRIGGER_CONDITION_TO_GROUP[trigger_condition]
            comb[GROUP_TO_IDX_TRIGGER_CONDITION[group]] = 1
        group_trigger_condition_counts[tuple(comb)] = group_trigger_condition_counts.get(tuple(comb), 0) + 1

    unique_combs = list(group_trigger_condition_counts.keys())
    sorted_combs = sorted(unique_combs, key=lambda x: (sum(x), -int(''.join(map(str, x)), 2)))
    return sorted_combs, [group_trigger_condition_counts[comb] for comb in sorted_combs]

def plot_trigger_condition_data(sorted_combs, sorted_counts):
    fig = plt.figure(figsize=(4.5, 1.6))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.05)

    # Top subplot: bar chart
    ax_bar = fig.add_subplot(gs[0])
    bars = ax_bar.bar(np.arange(len(sorted_counts)), sorted_counts, width=0.7, color='#5D688A')

    # Add value labels on top of bars
    for i, (bar, count) in enumerate(zip(bars, sorted_counts)):
        height = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{int(count)}', ha='center', va='bottom', fontsize=9)

    # Configure the bar chart
    ax_bar.set_ylabel('#Bugs')
    ax_bar.set_ylim(0, max(sorted_counts) * 1.15)
    ax_bar.set_xlim(-0.5, len(sorted_counts) - 0.5)
    ax_bar.set_xticks([])

    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.spines['bottom'].set_visible(False)
    ax_bar.grid(axis='y', alpha=0.3, linestyle='--')

    # Bottom subplot: set membership matrix
    ax_matrix = fig.add_subplot(gs[1])

    # Draw circles and lines for each combination
    for col_idx, comb in enumerate(sorted_combs):
        # Draw circles for all categories
        for row_idx in range(len(sorted_combs[0])):
            ellipse = plt.matplotlib.patches.Ellipse(
                (col_idx, row_idx), width=0.25, height=0.5, 
                facecolor='lightgray' if comb[row_idx] == 0 else '#5D688A', 
                edgecolor='gray' if comb[row_idx] == 0 else 'black', 
                linewidth=0.8, zorder=2, 
                transform=ax_matrix.transData)
            ax_matrix.add_patch(ellipse)

        # Draw connecting line between active categories
        y_coords = [i for i, val in enumerate(comb) if val == 1]
        x_coords = [col_idx] * len(y_coords)
        ax_matrix.plot(x_coords, y_coords, 'o-', color='#5D688A', 
                       linewidth=1, markersize=0, zorder=4)

    # Configure the matrix subplot
    ax_matrix.set_xlim(-0.5, len(sorted_counts) - 0.5)
    ax_matrix.set_ylim(-0.5, len(sorted_combs[0]) - 0.5)
    ax_matrix.set_yticks(range(len(sorted_combs[0])))
    ax_matrix.set_yticklabels([TRIGGER_CONDITION_ID_TO_LABELS[i] for i in range(len(sorted_combs[0]))])
    ax_matrix.set_xticks([])
    ax_matrix.invert_yaxis()

    for spine in ax_matrix.spines.values():
        spine.set_visible(False)

    for i in range(len(sorted_combs[0])):
        ax_matrix.axhline(i, color='lightgray', linestyle='--', alpha=0.5, zorder=0)

    fig.savefig(RESULT_DIR / 'trigger_condition.pdf', bbox_inches='tight', pad_inches=0.01)

if __name__ == "__main__":
    sorted_combs, sorted_counts = collect_trigger_condition_data()
    print(sorted_combs)
    print(sorted_counts)
    plot_trigger_condition_data(sorted_combs, sorted_counts)
