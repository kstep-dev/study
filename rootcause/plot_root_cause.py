import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

CONSEQUENCE_TO_GROUP = {
    'Crash': 'Func. Crash/Hang', 
    'lockup / hang': 'Func. Crash/Hang', 
    'Memory Leak': 'Policy. With Effect', 
    'security vulnerability': 'Func. Non-fatal.',
    'data corruption': 'Func. Non-fatal.',
    'Functionality (CFS bandwidth)': 'Func. Non-fatal.',
    'Functionality (Deadline enforce / admission control)': 'Func. Non-fatal.',
    'Functionality (Trace or account)': 'Func. Non-fatal.',
    'Functionality (config / feature not enabled/disabled)': 'Func. Non-fatal.',
    'Functionality (cpu allowed, or cpuiso)': 'Func. Non-fatal.',
    'Functionality (hotplug)': 'Func. Non-fatal.',
    'Functionality (property change fail)': 'Func. Non-fatal.',
    'Functionality (response error)': 'Func. Non-fatal.',
    'Functionality (starvation)': 'Func. Non-fatal.',
    'Functionality (task state change failure)': 'Func. Non-fatal.',
    'Performance (Policy violation, balance, work conserving)': 'Policy. With Effect',
    'Performance (Policy violation, cpufreq control)': 'Policy. With Effect',
    'Performance (Policy violation, fairness)': 'Policy. With Effect',
    'Performance (Policy violation, impact from lower priority task)': 'Policy. With Effect',
    'Performance (Policy violation, locality)': 'Policy. With Effect',
    'Performance (Policy violation, sched overhead)': 'Policy. With Effect',
    'Performance (energy efficiency, capacity fit)': 'Policy. With Effect',
    'No impact (coding rule)': 'Policy. Benign',
    'No impact (duplicate call)': 'Policy. Benign',
    'No impact (self correcting)': 'Policy. Benign',
    'No impact (unnecessary check or warning)': 'Policy. Benign',
}

# Root cause labels and colors (based on actual data in CSV)
rootcause_label_to_id = {
    "semantic(incorrect logic implementation making decision  update attr managetimer etc)": 1,
    "semantic(incorrect update stats)": 0,
    "semantic(maintain in-memory data structure wrong cfs tree list etc)": 0,
    "concurrency": 4,
    "memory": 5,
    "semantic(generic wrong type integer overflow etc)": 3,
}

# Shortened labels for display
rootcause_short_labels = {
    "semantic(incorrect update stats)": "States",
    # "semantic(maintain in-memory data structure wrong cfs tree list etc)": "Corrupted Data Structure",
    "semantic(incorrect logic implementation making decision  update attr managetimer etc)": "Logic",
    "concurrency": "Concurrency",
    "memory": "Memory",
    "semantic(generic wrong type integer overflow etc)": "Generic",
}

# 0: '#E49BA6',
#     1: '#FFC50F',
#     2: '#92487A',
#     # 3: '#FFD3D5',
#     3: '#658C58',
#     4: '#BBC863',
#     5: '#F5E5E1',

rootcause_id_to_colors = {
    # 0: '#473472',
    0: '#53629E',
    1: '#87BAC3',
    2: '#D6F4ED',
    3: '#B45253',
    4: '#FCB53B',
    5: '#FFE797',
}

consequence_group_to_id = {
    "Func. Crash/Hang": 0,
    "Func. Non-fatal.": 1,
    "Policy. With Effect": 2,
    "Policy. Benign": 3,
}

def parse_consequences(x):
    """Parse possibly quoted, comma-separated consequence strings."""
    if pd.isna(x):
        return []
    parts, curr, in_quotes = [], '', False
    for char in str(x):
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            if curr.strip():
                parts.append(curr.strip().strip('"'))
            curr = ''
        else:
            curr += char
    if curr.strip():
        parts.append(curr.strip().strip('"'))
    return [p.strip() for p in parts if p.strip()]

def get_consequence_to_rootcauses(csv_file="study-bug-set-rootcause.csv"):
    """
    Returns a dict mapping consequence group -> {root cause: count}
    """
    consequence_to_rootcauses = {}
    df = pd.read_csv(csv_file, low_memory=False)
    
    # Find the root cause column (might be named differently)
    rootcause_col = None
    for col in df.columns:
        if 'root' in col.lower() or 'cause' in col.lower():
            rootcause_col = col
            break
    
    if rootcause_col is None:
        print("Available columns:", df.columns.tolist())
        # Try to use column by index if name not found
        rootcause_col = df.columns[5] if len(df.columns) > 5 else df.columns[-1]
    
    print(f"Using root cause column: {rootcause_col}")
    
    for _, row in df.iterrows():
        rootcause = str(row[rootcause_col]).strip()
        if pd.isna(row[rootcause_col]) or rootcause == 'nan':
            continue
            
        consequences_str = row['consequence']
        consequences = parse_consequences(consequences_str)
        
        for consequence in consequences:
            if consequence not in CONSEQUENCE_TO_GROUP:
                continue
            group = CONSEQUENCE_TO_GROUP[consequence]
            if group not in consequence_to_rootcauses:
                consequence_to_rootcauses[group] = {}
            
            if rootcause not in consequence_to_rootcauses[group]:
                consequence_to_rootcauses[group][rootcause] = 1
            else:
                consequence_to_rootcauses[group][rootcause] += 1
    
    return consequence_to_rootcauses

# Load data
consequence_rootcause_map = get_consequence_to_rootcauses()
print("Consequence to Root Cause mapping:")
print(consequence_rootcause_map)

# Create a single plot showing consequence vs root cause
fig, ax = plt.subplots(figsize=(4.5, 1.3))

# Get sorted consequence groups (reversed for horizontal bars)
consequence_groups = sorted(consequence_rootcause_map.keys(), 
                           key=lambda x: consequence_group_to_id[x], reverse=True)

# Collect all unique root causes
all_rootcauses = set()
for rootcauses_dict in consequence_rootcause_map.values():
    all_rootcauses.update(rootcauses_dict.keys())

# Sort root causes by predefined order if they exist in our mapping
all_rootcauses = sorted(all_rootcauses, 
                        key=lambda rc: rootcause_label_to_id.get(rc, 999))

# Prepare data: calculate percentages
data = []
for rootcause in all_rootcauses:
    rootcause_percentages = []
    for group in consequence_groups:
        total_bugs = sum(consequence_rootcause_map[group].values())
        rootcause_count = consequence_rootcause_map[group].get(rootcause, 0)
        percentage = (rootcause_count / total_bugs * 100) if total_bugs > 0 else 0
        rootcause_percentages.append(percentage)
    data.append(rootcause_percentages)

# Create horizontal stacked bar chart
y = np.arange(len(consequence_groups))
height = 0.8

# Generate colors for each root cause
colors = [rootcause_id_to_colors[rootcause_label_to_id.get(rc, -1)] for rc in all_rootcauses]

# Plot horizontal stacked bars
left = np.zeros(len(consequence_groups))
bars = []
# Store actual counts for annotations
actual_counts = []
for i, (rootcause, rootcause_data) in enumerate(zip(all_rootcauses, data)):
    # Calculate actual counts from percentages
    counts_for_rootcause = []
    for j, group in enumerate(consequence_groups):
        total_bugs = sum(consequence_rootcause_map[group].values())
        count = consequence_rootcause_map[group].get(rootcause, 0)
        counts_for_rootcause.append(count)
    actual_counts.append(counts_for_rootcause)
    
    # Use short label for legend
    display_label = rootcause_short_labels.get(rootcause, rootcause)
    bar = ax.barh(y, rootcause_data, height, label=display_label, 
                  left=left, color=colors[i])
    bars.append(bar)
    left += rootcause_data

# Add count annotations
color_list = ['white', 'black', 'white', 'black', 'black', 'black']
for i, (rootcause, rootcause_data) in enumerate(zip(all_rootcauses, data)):
    for j, (percentage, count) in enumerate(zip(rootcause_data, actual_counts[i])):
        if count > 0:  # Only show if there are bugs
            # Calculate position for text
            x_pos = sum(data[k][j] for k in range(i)) + percentage / 2
            y_pos = y[j]
            
            # Only show text if percentage is large enough
            # if percentage > 5:
            ax.text(x_pos, y_pos, str(count), 
                    ha='center', va='center', fontsize=8, 
                    color=color_list[i])

# Customize plot
# ax.set_xlabel('Percentage (%)')
ax.set_yticks(y)
ax.set_yticklabels(consequence_groups, rotation=0)
ax.set_xlim(0, 100)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
ax.grid(axis='x', alpha=0.3)
ax.tick_params(which='both', length=1)

# Add legend at the bottom
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.3, -0.1), 
                   ncol=5, frameon=False, handletextpad=0.1, 
                   columnspacing=0.3, labelspacing=0.2, handlelength=0.5)

plt.tight_layout()
plt.savefig('root_cause_consequence.pdf', bbox_inches='tight', pad_inches=0.0)
plt.show()
