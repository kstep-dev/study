from .util import *
import os

file_to_component = {
    # Scheduler Framework: Core
    "sched.c": "core",
    "sched_features.h": "core",
    "sched_clock.c": "core",
    "sched_idletask.c": "core",
    "sched_stoptask.c": "core",
    "core.c": "core",
    "sched.h": "core",
    "features.h": "core",
    "syscalls.c": "core",
    "clock.c": "core",
    "idle_task.c": "core",
    "idle.c": "core",
    "stop_task.c": "core",
    "cpufreq.c": "core",
    "cpufreq_schedutil.c": "core",
    "isolation.c": "core",
    "membarrier.c": "core",
    "rq-offsets.c": "core",

    # Scheduler Framework: Topology
    "sched_autogroup.c": "topology",
    "sched_autogroup.h": "topology",
    "auto_group.c": "topology",
    "auto_group.h": "topology",
    "topology.c": "topology",
    "autogroup.c": "topology",
    "autogroup.h": "topology",
    "core_sched.c": "topology",
    "build_policy.c": "topology",
    "build_utility.c": "topology",
    "smp.h": "topology",

    # Scheduler Framework: Account
    "sched_stats.c": "account",
    "sched_debug.c": "account",
    "stats.c": "account",
    "stats.h": "account",
    "cputime.c": "account",
    "cpuacct.c": "account",
    "cpuacct.h": "account",
    "debug.c": "account",

    # Scheduling Policy: Fair
    "sched_fair.c": "fair",

    # Scheduling Policy: RT (Real Time)
    "sched_rt.c": "rt",
    "sched_cpupri.c": "rt",
    "sched_cpupri.h": "rt",


    # Scheduling Policy: Fair
    "fair.c": "fair",
    "proc.c": "fair",

    # Scheduling Policy: PELT
    "pelt.c": "core",
    "pelt.h": "core",
    "loadavg.c": "core",
    "sched-pelt.c": "core",
    "sched-pelt.h": "core",

    # Scheduling Policy: RT (Real Time)
    "rt.c": "rt",
    "cpupri.c": "rt",
    "cpupri.h": "rt",

    # deadline
    "deadline.c": "deadline",
    "cpudeadline.c": "deadline",
    "cpudeadline.h": "deadline",

    # wait
    "wait.c": "wait",
    "completion.c": "wait",
    "swait.c": "wait",
    "wait_bit.c": "wait",

    # ext
    "ext.c": "ext",
    "ext.h": "ext",
    "ext_idle.c": "ext",
    "ext_idle.h": "ext",
    "ext_internal.h": "ext",

    "psi.c": "psi",
}

COMPONENT_ORDER = {
    "core": 0,
    "topology": 1,
    "account": 2,
    "fair": 3,
    "deadline": 4,
    "rt": 5,
}

COMPONENT_SET = set(file_to_component.values()) - {"wait", "ext", "psi"}
COMPONENT_SET = sorted(COMPONENT_SET, key=lambda x: COMPONENT_ORDER[x])

def get_components(commit):
    out = None
    for linux_dir in [LINUX_MAINLINE_DIR] + LINUX_DIRs:
        try:
            out = system_output(
                f"git -C {linux_dir} show --pretty= --name-only {commit} -- kernel/sched/"
            )
            break
        except subprocess.CalledProcessError:
            continue
    if out is None:
        logging.error(f"Failed to get components for commit {commit}")
        exit(1)

    files = [l.strip() for l in out.splitlines() if l.strip()]
    files = [os.path.basename(p) for p in files]
    components = set()
    for f in files:
        components.add(file_to_component[f])
    return components