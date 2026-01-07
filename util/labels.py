CONSEQUENCE_TO_OBSERVABILITY = {
    'Crash':                                        'Func. Crash/Hang', 
    'lockup / hang':                                'Func. Crash/Hang', 
    'Memory Leak':                                  'Policy. Benign', 
    'security vulnerability':                       'Func. Non-fatal',
    'data corruption':                              'Func. Non-fatal',
    'Functionality (CFS bandwidth)':                'Func. Non-fatal',
    'Functionality (Deadline enforce / admission control)': 'Func. Non-fatal',
    'Functionality (Trace or account)':             'Func. Non-fatal',
    'Functionality (config / feature not enabled/disabled)': 'Func. Non-fatal',
    'Functionality (cpu allowed, or cpuiso)':       'Func. Non-fatal',
    'Functionality (hotplug)':                      'Func. Non-fatal',
    'Functionality (property change fail)':         'Func. Non-fatal',
    'Functionality (response error)':               'Func. Non-fatal',
    'Functionality (starvation)':                   'Func. Non-fatal',
    'Functionality (task state change failure)':    'Func. Non-fatal',
    'Performance (Policy violation, balance, work conserving)': 'Policy. With Effect',
    'Performance (Policy violation, cpufreq control)': 'Policy. With Effect',
    'Performance (Policy violation, fairness)':     'Policy. With Effect',
    'Performance (Policy violation, impact from lower priority task)': 'Policy. With Effect',
    'Performance (Policy violation, locality)':     'Policy. With Effect',
    'Performance (Policy violation, sched overhead)': 'Policy. With Effect',
    'Performance (energy efficiency, capacity fit)': 'Policy. With Effect',
    'No impact (coding rule)':                      'Policy. Benign',
    'No impact (duplicate call)':                   'Policy. Benign',
    'No impact (self correcting)':                  'Policy. Benign',
    'No impact (unnecessary check or warning)':     'Policy. Benign',
}

OBSERVABILITY_TO_IDX = {
    'Func. Crash/Hang': 0,
    'Func. Non-fatal': 1,
    'Policy. With Effect': 2,
    'Policy. Benign': 3,
}

OBSERVABILITY_ID_TO_LABELS = {
    0: 'Func. Crash/Hang',
    1: 'Func. Non-fatal',
    2: 'Policy. With Effect',
    3: 'Policy. Benign',
}

WARNING_TO_IDX = {
    'panic': 0,
    'warning': 1,
    'silent': 2,
}

# Map consequence descriptions for functionality
CONSEQUENCE_TO_GROUP_FUNC = {
    'Crash': 'Crash/Hang', 
    'lockup / hang': 'Crash/Hang', 
    'Functionality (CFS bandwidth)': 'Sched Attr',
    'Functionality (Deadline enforce / admission control)': 'Sched Attr',
    'Functionality (Trace or account)': 'Trace',
    'Functionality (config / feature not enabled/disabled)': 'Config',
    'Functionality (cpu allowed, or cpuiso)': 'Sched Attr',
    'Functionality (hotplug)': 'Hotplug',
    'Functionality (property change fail)': 'Sched Attr',
    'Functionality (response error)': 'Return Val',
    'Functionality (starvation)': 'Starvation',
    'Functionality (task state change failure)': 'Task State',
}

GROUP_TO_IDX_FUNC = {
    'Crash/Hang': 0,
    'Starvation': 1,
    'Sched Attr': 2,
    'Config': 3,
    'Hotplug': 4,
    'Task State': 5,
    'Return Val': 6,
    'Trace': 7,
}

# Map consequence descriptions for policy
CONSEQUENCE_TO_GROUP_POLICY = {
    'Performance (Policy violation, sched overhead)': 'Sched Cost',
    'Performance (Policy violation, balance, work conserving)': 'Balance',
    'Performance (Policy violation, cpufreq control)': 'Freq Ctrl',
    'Performance (Policy violation, fairness)': 'Fairness',
    'Performance (Policy violation, impact from lower priority task)': 'Class Prio',
    'Performance (Policy violation, locality)': 'Locality',
    'Performance (energy efficiency, capacity fit)': 'Energy Eff',
}

GROUP_TO_IDX_POLICY = {
    'Sched Cost': 0,
    'Balance': 1,
    'Freq Ctrl': 2,
    'Fairness': 3,
    'Class Prio': 4,
    'Locality': 5,
    'Energy Eff': 6,
}

# Map discover methods to group names
DISCOVER_TO_GROUP = {
    "Benchmark/stress test regression": "Benchmark(Perf regression)",
    "Benchmark/stress test/standard test fail": "Benchmark(Warning/Crash)",
    "Customizied test": "Customized test cases",
    "Fuzz": "Fuzzing",
    "Code Review or Internal Debug": "Inspection from developer",
    "Other kernel subsystem behavior": "Other subsystem reported",
    "User reported or In-production": "Production-user reported",
}

GROUP_TO_IDX_DISCOVER = {
    "Benchmark(Perf regression)": 0,
    "Benchmark(Warning/Crash)": 1,
    "Customized test cases": 2,
    "Fuzzing": 3,
    "Other subsystem reported": 4,
    "Production-user reported": 5,
    "Inspection from developer": 6,
}

DISCOVER_ID_TO_COLORS = {
    0: ('#473472', 'white'),
    1: ('#53629E', 'white'),
    2: ('#87BAC3', 'black'),
    3: ('#D6F4ED', 'black'),
    4: ('#FCB53B', 'white'),
    5: ('#FFE797', 'black'),
    6: ('#B45253', 'white'),
}

DISCOVER_ID_TO_LABELS = {
    0: "Benchmark(Perf regression)",
    1: "Benchmark(Warning/Crash)",
    2: "Customized test cases",
    3: "Fuzzing",
    4: "Other subsystem reported",
    5: "Production-user reported",
    6: "Inspection from developer",
}

# Map prevention methods to group names
PREVENTION_TO_GROUP = {
    "unit test": "Unit test",
    "warning": "Warning",
    "tracepoint": "Tracepoint",
    "comment": "Comment",
    "document": "Document",
    "no action": "Nothing",
}

GROUP_TO_IDX_PREVENTION = {
    "Warning": 0,
    "Tracepoint": 1,
    "Unit test": 2,
    "Document": 3,
    "Comment": 4,
    "Nothing": 5,
}

PREVENTION_ID_TO_COLORS = {
    0: ('#92487A', 'white'),
    1: ('#E49BA6', 'black'),
    2: ('#FFC50F', 'white'),
    3: ('#658C58', 'black'),
    4: ('#BBC863', 'black'),
    5: ('#F5E5E1', 'black'),
}

PREVENTION_ID_TO_LABELS = {
    0: "Warning",
    1: "Tracepoint",
    2: "Unit test",
    3: "Document",
    4: "Comment",
    5: "Nothing",
}

# Map root cause labels to IDs (based on actual data in CSV)
ROOTCAUSE_TO_GROUP = {
    "semantic(incorrect update stats)": "State",
    "semantic(maintain in-memory data structure wrong cfs tree list etc)": "State",
    "semantic(incorrect logic implementation making decision  update attr managetimer etc)": "Logic",
    "concurrency": "Concurrency",
    "memory": "Memory",
    "semantic(generic wrong type integer overflow etc)": "Generic",
}

GROUP_TO_IDX_ROOTCAUSE = {
    "State": 0,
    "Logic": 1,
    "Generic": 2,
    "Concurrency": 3,
    "Memory": 4,
}

ROOTCAUSE_ID_TO_COLORS = {
    0: ('#53629E', 'white'),
    1: ('#87BAC3', 'black'),
    2: ('#B45253', 'black'),
    3: ('#FCB53B', 'black'),
    4: ('#FFE797', 'black'),
}

ROOTCAUSE_ID_TO_LABELS = {
    0: "State",
    1: "Logic",
    2: "Generic",
    3: "Concurrency",
    4: "Memory",
}

# Map trigger conditions to group names
TRIGGER_CONDITION_TO_GROUP = {
    "Boot": "Kernel Event",
    "Hotplug/Hotunplug": "Kernel Event",
    "Kernel/driver Event": "Kernel Event",
    "Kthread Behavior": "Kernel Event",
    "Property change (per cgroup)": "User Event",
    "Property change (per system)": "User Event",
    "Property change (per thread)": "User Event",
    "Special topology (asym cpu)": "Special Topology",
    "Special topology (numa)": "Special Topology",
    "Special topology (other)": "Special Topology",
    "Special topology (uniprocessor noSMP)": "Special Topology",
    "Thread Behavior": "Thread Event",
    "multiple sched class": "User Event",
    "special config": "Kernel Event",
}

GROUP_TO_IDX_TRIGGER_CONDITION = {
    "Thread Event": 0,
    "User Event": 1,
    "Kernel Event": 2,
    "Special Topology": 3,
}

TRIGGER_CONDITION_ID_TO_LABELS = {
    0: "Workload Behavior",
    1: "Sched Attribute",
    2: "Kernel Event",
    3: "CPU Attribute",
}