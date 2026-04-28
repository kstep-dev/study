from util import *
import matplotlib.pyplot as plt
import numpy as np

def skip_count(observability, warning):
    if warning == 'panic' and observability != 'Func. Crash/Hang':
        return True
    if (warning == 'warning' or warning == 'silent') and observability == 'Func. Crash/Hang':
        return True
    return False

def collect_observability_data():
    data = read_data()
    hashes = list(data.keys())
    # Initialize a nested dictionary:
    # observability_data[component][observability][warning] = count
    observability_data = {
        component: {
            observability: {
                warning: 0
                for warning in WARNING_TO_IDX
            }
            for observability in OBSERVABILITY_TO_IDX
        }
        for component in ['total'] + COMPONENT_SET
    }
    counts = {component: 0 for component in ['total'] + COMPONENT_SET}
    for hash in hashes:
        components = get_components(hash)
        consequences = data[hash]["consequence"]
        warnings = data[hash]["visibility"]
        for component in components:
            if component == "account" and len(components) != 1:
                continue
            
            for consequence in consequences:
                observability = CONSEQUENCE_TO_OBSERVABILITY[consequence]
                if skip_count(observability, warnings):
                    continue
                observability_data[component][observability][warnings] += 1
                counts[component] +=1

        for consequence in consequences:
            observability = CONSEQUENCE_TO_OBSERVABILITY[consequence]
            if skip_count(observability, warnings):
                continue
            observability_data['total'][observability][warnings] += 1
            counts['total'] += 1

    return observability_data, counts

def get_legend_elements(legend_dict):
    legend_elements = []
    legend_labels = []
    legend_elements.append(legend_dict['Func. Crash/Hang']['elements'][0])
    legend_labels.append('Func.Crash/Hang\n    Panic')
    legend_elements.append(plt.Rectangle((0, 0), 1, 1, fc='none', ec='none', linewidth=0, alpha=0))
    legend_labels.append('')
    legend_elements.append(legend_dict['Func. Non-fatal']['elements'][0])
    legend_labels.append('Func. Non-fatal\n    Warning')
    legend_elements.append(legend_dict['Func. Non-fatal']['elements'][1])
    legend_labels.append('    Silent')
    legend_elements.append(legend_dict['Policy. With Effect']['elements'][0])
    legend_labels.append('Policy. With Effect\n    Warning')
    legend_elements.append(legend_dict['Policy. With Effect']['elements'][1])
    legend_labels.append('    Silent')
    legend_elements.append(legend_dict['Policy. Benign']['elements'][0])
    legend_labels.append('Policy. Benign\n    Warning')
    legend_elements.append(legend_dict['Policy. Benign']['elements'][1])
    legend_labels.append('    Silent')

    return legend_elements, legend_labels

def plot_observability(observability_data, counts):
    consequence_base_colors = {
        'Func. Crash/Hang': {'panic':'#BF092F', 'warning':'#FA812F', 'silent':'#80A1BA'},
        'Func. Non-fatal': {'panic':'#BF092F', 'warning':'#FA812F', 'silent':'#FFCB61'},
        'Policy. With Effect': {'panic':'#BF092F', 'warning':'#658C58', 'silent':'#BBC863'},
        'Policy. Benign': {'panic':'#BF092F', 'warning':'#7A7A73', 'silent':'#EEEEEE'},
    }

    fig, ax = plt.subplots(figsize=(5.2, 1.8))
    component_labels_reversed = ['total'] + COMPONENT_SET[::-1]
    y_pos = np.arange(len(component_labels_reversed))
    left = np.zeros(len(component_labels_reversed))
    legend_dict = {
                        obsv: {
                            'elements': [], 'labels': []
                        } for obsv in OBSERVABILITY_TO_IDX.keys()
                   }

    for obsv in OBSERVABILITY_TO_IDX.keys():
        for warning in WARNING_TO_IDX.keys():
            if skip_count(obsv, warning):
                continue
            
            # calculate the percentages of the observability for each component
            count = np.array(
                [
                    observability_data[component][obsv][warning] 
                    for component in component_labels_reversed
                ]
            )
            percentages = np.array(
                [
                    observability_data[component][obsv][warning] * 100.0 / counts[component] 
                    for component in component_labels_reversed
                ]
            )
            
            bars = ax.barh(y_pos, percentages, 1,
                        left=left, color=consequence_base_colors[obsv][warning],
                        edgecolor='gray', linewidth=0.01)
            
            legend_dict[obsv]['elements'].append(bars[0])
            legend_dict[obsv]['labels'].append(f'{warning.capitalize()}')

            # add percentage labels
            for i, (bar, pct, c) in enumerate(zip(bars, percentages, count)):
                if pct > 3:
                    x_pos = left[i] + pct / 2
                    ax.text(x_pos, bar.get_y() + bar.get_height() / 2.4,
                            f'{int(c)}', ha='center', va='center',
                            color='white' if warning != 'silent' else 'black')

            # update the left position
            left += percentages

    ax.plot([-25, 100], [0.5, 0.5], color='black', linewidth=1., linestyle='-', zorder=10, clip_on=False)

    ax.set_ylim(bottom=-0.5, top = len(component_labels_reversed) - 0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(component_labels_reversed)
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    ax.tick_params(which='both', length=0.1)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)

    legend_elements, legend_labels = get_legend_elements(legend_dict)
    # Add the legend elements
    legend = ax.legend(legend_elements, legend_labels, loc='upper center', bbox_to_anchor=(0.37, -0.),
           frameon=False, ncol=4, handlelength=0.9, columnspacing=1.3, handletextpad=-1, fontsize=9.5,
           labelspacing=0.1, borderpad=0.
           )

    # Align all legend handlers to the top of text and adjust vertical position
    for vpack in legend._legend_handle_box.get_children():
        for hpack in vpack.get_children():
            hpack.align = 'bottom'

    # Adjust handler vertical offset by modifying the text position
    for text in legend.get_texts():
        # text.set_verticalalignment('top')
        text.set_y(text.get_position()[1] - 1)
    

    plt.tight_layout(pad = 0.4)
    save_figure_variants(fig, "Fig7_observability", bbox_inches=0.0)

if __name__ == "__main__":
    observability_data, counts = collect_observability_data()
    plot_observability(observability_data, counts)
