import numpy as np

# Create a horizontal stacked bar chart showing percentage of each method under each observability group.
# counts: a matrix in shape of (observability_groups, methods) methods can be manifest, prevention, root cause, etc.
def plot_stacked_bar_percentage(ax, legend_ax, counts, colors, labels, y_labels, legend_args):
    # Prepare data: calculate percentages
    data = []
    for method_idx in range(len(counts[0])):
        method_percentages = []
        for observability_idx in range(len(counts)):
            total_bugs = sum(counts[observability_idx])
            method_count = counts[observability_idx][method_idx]
            percentage = (method_count / total_bugs * 100) if total_bugs > 0 else 0
            method_percentages.append(percentage)
        data.append(method_percentages)
    
    # Create horizontal stacked bar chart
    y = np.arange(len(counts))
    left = np.zeros(len(counts))
    bars = []
    for method_idx, method_data in enumerate(data):
        bar = ax.barh(y, method_data, 1, label=labels[method_idx], left=left, color=colors[method_idx][0], edgecolor='gray', linewidth=0.01)
        bars.append(bar)
        left += method_data
    
    # Add count annotations
    for method_idx, method_data in enumerate(data):
        for observability_idx, percentage in enumerate(method_data):
            if percentage > 2:  # Only show if there are bugs
                x_pos = sum(data[k][observability_idx] for k in range(method_idx)) + percentage / 2
                y_pos = y[observability_idx]                
                ax.text(x_pos, y_pos, str(counts[observability_idx][method_idx]), 
                       ha='center', va='center', fontsize=8, 
                       color=colors[method_idx][1])

    # the plot settings for the bar chart
    ax.set_ylim(bottom=-0.5, top = len(counts) - 0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([y_labels[i] for i in y], rotation=0)
    ax.invert_yaxis()
    ax.tick_params(which='both', length=0.1)

    ax.set_xlim(0, 100)
    ax.set_xticks([])

    # Add legend
    handles = [bar[0] for bar in bars]
    legend_ax.legend(handles, [labels[i] for i in range(len(labels))],
                     loc="center left",  frameon=False, 
                     **legend_args)

    return