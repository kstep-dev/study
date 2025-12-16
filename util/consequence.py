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
    'silent': 3,
}
