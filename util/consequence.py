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