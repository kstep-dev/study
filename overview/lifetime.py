from util import *
import matplotlib.pyplot as plt

def collect_lifetime_data():
    data = read_data()
    hashes = list(data.keys())

    lifetime_data = {k: [] for k in COMPONENT_SET}
    for hash in hashes:
        components = get_components(hash)
        for component in components:
            diff = get_date_diff(hash, data[hash]["buggy_hash"])
            lifetime_data[component].append(diff.days)
        
    for component in COMPONENT_SET:
        lifetime_data[component] = sorted(lifetime_data[component])
    return lifetime_data

def plot_lifetime_data(lifetime_data):
    fig, axes = plt.subplots(1, 2, figsize=(4.5, 1.2), sharex=True, sharey=True)
    colors = plt.cm.tab20.colors

    foundation = ["core", "topology", "account"]
    policy = ["fair", "rt", "deadline"]

    ax0 = axes[0]
    for idx, component in enumerate(foundation):
        y_vals = [i / len(lifetime_data[component]) * 100 for i in range(len(lifetime_data[component]))]
        ax0.plot(lifetime_data[component], y_vals, label=component, color=colors[idx])
    ax0.set_title("(a) Scheduler Framework", fontsize=9)

    ax1 = axes[1]
    for idx, component in enumerate(policy):
        y_vals = [i / len(lifetime_data[component]) * 100 for i in range(len(lifetime_data[component]))]
        ax1.plot(lifetime_data[component], y_vals, label=component, color=colors[idx])
    ax1.set_title("(b) Scheduler Classes", fontsize=9)

    for ax in axes:
        ax.set_xlim(1, 7000)
        ax.set_ylim(0, 105)
        ax.set_xlabel("Bug lifetime (days)", labelpad=0, fontsize=9)
        ax.set_ylabel("% of bugs", fontsize=9)
        ax.set_xscale('log')
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0", "50", "100"])
        ax.tick_params(axis = 'both', length=1, labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper left', frameon=False, 
                borderpad=0, handlelength=0.5, handletextpad=0.2, 
                labelspacing=0.15, ncol = 2, columnspacing=0.5,
                fontsize=8)

    plt.tight_layout(pad=0.0, rect=[0, 0, 1, 0.98])
    save_figure_variants(fig, "Fig5_lifetime")


if __name__ == "__main__":
    lifetime_data = collect_lifetime_data()
    print(lifetime_data)
    plot_lifetime_data(lifetime_data)
