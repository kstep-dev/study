import csv
import numpy as np

trigger_conditions_to_id_map = {
    "Boot": 0,
    "Hotplug/Hotunplug": 1,
    "Kernel/driver Event": 2,
    "Kthread Behavior": 3,
    "Property change (per cgroup)": 4,
    "Property change (per system)": 5,
    "Property change (per thread)": 6,
    "Special topology (asym cpu)": 7,
    "Special topology (numa)": 8,
    "Special topology (other)": 9,
    "Special topology (uniprocessor noSMP)": 10,
    "Thread Behavior": 11,
    "multiple sched class": 12,
    "special config": 13,
}

trigger_counts = [0 for _ in range(14)]

def load_hash_to_trigger_condition_map(csv_path="./study-bug-set-trigger.csv"):
    """
    Reads the given CSV and returns a dictionary mapping hash to a list of trigger conditions.
    """
    hash_to_trigger = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hash_val = row['hash']
            # The column may have multiple trigger conditions separated by comma, possibly with quotes
            conds = row['Trigger condition']
            # Split on comma, but account for possible quotes
            # csv module already processes quoted fields as single string
            trigger_list = [cond.strip() for cond in conds.split(',')]
            hash_to_trigger[hash_val] = trigger_list
    return hash_to_trigger

hash_to_trigger_condition_map = load_hash_to_trigger_condition_map()

print(hash_to_trigger_condition_map)
# INSERT_YOUR_CODE
# Print all unique trigger conditions found in the CSV mapping
unique_triggers = set()
for triggers in hash_to_trigger_condition_map.values():
    unique_triggers.update(triggers)
print("Unique trigger conditions:")
for cond in sorted(unique_triggers):
    print(cond)

# matrix = np.zeros((8, len(hash_to_trigger_condition_map)))
combination_num = [0 for _ in range(16)]

# comblist_to_id = {
#     [0, 0, 0, 0]: 0,
#     [1, 0, 0, 0]: 1,
#     [0, 1, 0, 0]: 2,
#     [0, 0, 1, 0]: 3,
#     [0, 0, 0, 1]: 4,
#     [1, 0, 0, 1]: 5,
#     [0, 1, 0, 1]: 6,
#     [0, 0, 1, 1]: 7,
#     [1, 0, 1, 0]: 8,
#     [1, 0, 1, 1]: 9,
#     [0, 1, 1, 0]: 10,
#     [0, 1, 1, 1]: 11,
#     [1, 0, 1, 1]: 12,
#     [1, 1, 0, 0]: 13,
#     [1, 1, 0, 1]: 14,
#     [1, 1, 1, 0]: 15,
#     [1, 1, 1, 1]: 16,
# }
hash_to_comblist = {}
for hash, trigger_list in hash_to_trigger_condition_map.items():
    has_thread_event = 0
    has_user_event = 0
    has_kernel_event = 0
    has_special_topology = 0
    for trigger in trigger_list:
        trigger_id = trigger_conditions_to_id_map[trigger]
        if trigger_id in [11]:
            has_thread_event = 1
        elif trigger_id in [4, 5, 6, 12]:
            has_user_event = 1
        elif trigger_id in [0, 1, 2, 3]:
            has_kernel_event = 1
        elif trigger_id in [7, 8, 9, 10]:
            has_special_topology = 1
        trigger_counts[trigger_id] += 1
    # comb_id = has_thread_event * 8 + has_user_event * 4 + has_kernel_event * 2 + has_special_topology
    comb_list = [has_special_topology, has_kernel_event, has_user_event, has_thread_event]
    # print(comb_list)
    hash_to_comblist[hash] = comb_list

for i, count in enumerate(trigger_counts):
    print(i, count / len(hash_to_trigger_condition_map))
    # if i in [11]:
    #     print(i, count / trigger_counts[11])
    # elif i in [4, 5, 6, 12]:
    #     print(i, count / sum([trigger_counts[4], trigger_counts[5], trigger_counts[6], trigger_counts[12]]))
    # elif i in [0, 1, 2, 3]:
    #     print(i, count / sum([trigger_counts[0], trigger_counts[1], trigger_counts[2], trigger_counts[3]]))
    # elif i in [7, 8, 9, 10]:
    #     print(i, count / sum([trigger_counts[7], trigger_counts[8], trigger_counts[9], trigger_counts[10]]))
unique_comblists = set(tuple(cl) for cl in hash_to_comblist.values())
print("Unique comb_list combinations:")
sorted_unique_comblists = sorted(unique_comblists)
# for comb in sorted_unique_comblists:
#     print(list(comb))

comblist_to_id = {comb: i for i, comb in enumerate(sorted_unique_comblists)}
comblist_count = [0 for _ in range(len(sorted_unique_comblists))]

for hash, comb_list in hash_to_comblist.items():
    comblist_count[comblist_to_id[tuple(comb_list)]] += 1

print("comblist_count:")
for i, count in enumerate(comblist_count):
    print(f"Combination {sorted_unique_comblists[i]}: {count}")

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle
from matplotlib.lines import Line2D

# Prepare data for UpSet-style plot
categories = ['Special Topology', 'KernelSpace Event', 'Sched Attribute', 'Workload Behavior']
n_categories = len(categories)

# Sort combinations by number of triggers needed (ascending), then by binary value, then by count (descending)
def tuple_to_binary_value(t):
    """Convert tuple like (0,1,0,1) to binary integer value"""
    return int(''.join(map(str, t)), 2)

sorted_data = sorted(zip(sorted_unique_comblists, comblist_count), 
                     key=lambda x: (sum(x[0]), tuple_to_binary_value(x[0]), -x[1]))
sorted_combs, sorted_counts = zip(*sorted_data)

# Swap columns 6 and 7 (indices 5 and 6)
sorted_combs = list(sorted_combs)
sorted_counts = list(sorted_counts)
sorted_combs[5], sorted_combs[6] = sorted_combs[6], sorted_combs[5]
sorted_counts[5], sorted_counts[6] = sorted_counts[6], sorted_counts[5]

# Create figure with GridSpec
fig = plt.figure(figsize=(4.5, 1.6))
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.05)

# Top subplot: bar chart
ax_bar = fig.add_subplot(gs[0])
x_positions = np.arange(len(sorted_counts))
bars = ax_bar.bar(x_positions, sorted_counts, width=0.7, color='#5D688A')

# Add value labels on top of bars
for i, (bar, count) in enumerate(zip(bars, sorted_counts)):
    height = bar.get_height()
    ax_bar.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{int(count)}', ha='center', va='bottom', fontsize=9)

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
ax_matrix.set_xlim(-0.5, len(sorted_counts) - 0.5)
ax_matrix.set_ylim(-0.5, n_categories - 0.5)

# Draw circles and lines for each combination
for col_idx, comb in enumerate(sorted_combs):
    active_rows = [i for i, val in enumerate(comb) if val == 1]
    
    # Draw circles for all categories
    for row_idx in range(n_categories):
        if comb[row_idx] == 1:
            # Filled flattened ellipse for active category
            ellipse = plt.matplotlib.patches.Ellipse(
                (col_idx, row_idx), width=0.25, height=0.5, 
                facecolor='#5D688A', edgecolor='black', linewidth=0.8, zorder=3, transform=ax_matrix.transData)
        else:
            # Empty flattened ellipse for inactive category
            ellipse = plt.matplotlib.patches.Ellipse(
                (col_idx, row_idx), width=0.25, height=0.5, 
                facecolor='lightgray', edgecolor='gray', linewidth=0.8, zorder=2, transform=ax_matrix.transData)
        ax_matrix.add_patch(ellipse)
    # Draw connecting line between active categories
    if len(active_rows) > 1:
        y_coords = active_rows
        x_coords = [col_idx] * len(y_coords)
        ax_matrix.plot(x_coords, y_coords, 'o-', color='#5D688A', 
                      linewidth=1, markersize=0, zorder=4)

# Set y-axis labels (categories)
ax_matrix.set_yticks(range(n_categories))
ax_matrix.set_yticklabels(categories)
ax_matrix.set_xticks([])

# Style the matrix subplot
ax_matrix.spines['top'].set_visible(False)
ax_matrix.spines['right'].set_visible(False)
ax_matrix.spines['bottom'].set_visible(False)
ax_matrix.spines['left'].set_visible(False)
ax_matrix.tick_params(left=False, bottom=False)

# Add horizontal grid lines for readability
for i in range(n_categories):
    ax_matrix.axhline(i, color='lightgray', linestyle='--', alpha=0.5, zorder=0)

# Add title
# fig.suptitle('Trigger Condition Combinations (UpSet Diagram)', 
#             fontsize=14, fontweight='bold', y=0.98)

plt.savefig('trigger_upset_diagram.pdf', bbox_inches='tight', pad_inches=0.00)
plt.savefig('trigger_upset_diagram.png', bbox_inches='tight', pad_inches=0.00)
plt.show()

print(f"\nTotal combinations visualized: {len(sorted_counts)}")
print(f"Total bugs: {sum(sorted_counts)}")
