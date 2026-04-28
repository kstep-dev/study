from util import *
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.colors import ListedColormap, BoundaryNorm

def collect_backport_data():
    # Each commit will be a column, each version is a row
    reversed_linux_versions = LINUX_VERSIONS[::-1]
    data = read_data()
    backport_matrix = np.zeros((len(reversed_linux_versions), len(data)), dtype=int)
    
    years = defaultdict(lambda: 0)
    for col, hash in enumerate(data.keys()):
        tree_versions = data[hash]["tree"]
        backport_versions = data[hash]["backport"]
        buggy_version = data[hash]["buggy_tag"]

        for row, version in enumerate(reversed_linux_versions):
            print(version, buggy_version)
            if version in tree_versions:
                backport_matrix[row, col] = 1
            if version in backport_versions:
                backport_matrix[row, col] = 2
            if backport_matrix[row, col] == 0:
                if compare_versions(version, buggy_version) > 0:
                    backport_matrix[row, col] = 3
        
        nonzero_rows = np.where(backport_matrix[:, col] == 3)[0]
        if len(nonzero_rows) == 1 and nonzero_rows[0] in [0, 6]:
            backport_matrix[nonzero_rows[0], col] = 0
        
        years[get_year(hash) if get_year(hash) > "2020" else "2020"] += 1

    return backport_matrix, years

def plot_backport_matrix(backport_matrix):
    reversed_linux_versions = LINUX_VERSIONS[::-1]

    plt.figure(figsize=(5, 1.6))
    cmap = ListedColormap(['#ffffff', '#4f98c6', '#184478', '#FF6C0C'])
    bounds = [0, 1, 2, 3, 4]
    norm = BoundaryNorm(bounds, cmap.N)

    im = plt.imshow(backport_matrix, aspect='auto', cmap=cmap, norm=norm, interpolation='nearest')
    plt.yticks(range(len(reversed_linux_versions)), reversed_linux_versions)
    plt.xticks([])

    # plot the cbar
    cbar = plt.colorbar(
        im, 
        ticks=[0, 1, 2, 3], 
        boundaries=bounds, 
        orientation='horizontal', 
        pad=0.03,
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

    # plot the years ticks and texts
    sum = 0
    origin_ylim = plt.ylim()
    origin_xlim = plt.xlim()
    for year in years.keys():
        plt.plot([sum - 0.5, sum - 0.5], [-1, -0.5], color='black', clip_on=False)
        plt.text(sum + 3, -1, str(year), ha='left', va='center', color='black', fontsize=10, rotation=0)
        sum += years[year]
    plt.plot([sum - 0.5, sum - 0.5], [-1, -0.5], color='black', clip_on=False)
    plt.ylim(origin_ylim[0], origin_ylim[1])
    plt.xlim(origin_xlim[0], origin_xlim[1])

    plt.tight_layout(pad=0.3)
    save_figure_variants(plt.gcf(), "Fig6_backport_matrix", dpi=1000)

if __name__ == "__main__":
    backport_matrix, years = collect_backport_data()
    print(backport_matrix, years)
    plot_backport_matrix(backport_matrix)
