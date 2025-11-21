import subprocess
import os
from datetime import datetime

file_to_component = {
    # Scheduler Foundations: Core
    "sched.c": "core",
    "sched_features.h": "core",

    "sched_clock.c": "clock",
    "sched_autogroup.c": "topology",
    "sched_autogroup.h": "topology",
    "sched_idletask.c": "core",
    "sched_stoptask.c": "core",

    # Scheduler Foundations: Account
    "sched_stats.c": "accounting",

    # debug
    "sched_debug.c": "accounting",

    # Scheduling Policy: Fair
    "sched_fair.c": "fair",

    # Scheduling Policy: RT (Real Time)
    "sched_rt.c": "rt",
    "sched_cpupri.c": "rt",
    "sched_cpupri.h": "rt",


    # Scheduler Foundations: Core
    "core.c": "core",
    "sched.h": "core",
    "features.h": "core",
    "syscalls.c": "core",

    "clock.c": "core",
    "auto_group.c": "topology",
    "auto_group.h": "topology",
    "topology.c": "topology",
    "autogroup.c": "topology",
    "autogroup.h": "topology",
    "core_sched.c": "topology",
    "build_policy.c": "topology",
    "build_utility.c": "topology",

    "smp.h": "topology",
    "idle_task.c": "core",
    "idle.c": "core",
    "stop_task.c": "core",

    "cpufreq.c": "core",
    "cpufreq_schedutil.c": "core",
    "isolation.c": "core",

    # Scheduler Foundations: Account
    "stats.c": "accounting",
    "stats.h": "accounting",
    "cputime.c": "accounting",
    "cpuacct.c": "accounting",
    "cpuacct.h": "accounting",
    "psi.c": "psi",

    # debug
    "debug.c": "accounting",

    # Scheduling Policy: Fair
    "fair.c": "fair",
    "proc.c": "fair",

    # Scheduling Policy: PELT
    "pelt.c": "load est.",
    "pelt.h": "load est.",
    "loadavg.c": "load est.",
    "sched-pelt.c": "load est.",
    "sched-pelt.h": "load est.",

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

    # mem
    "membarrier.c": "core",
}

linux_dir = f"{os.path.dirname(__file__)}/linux/master"

def get_components(commit):
    try:
        out = subprocess.check_output([
            "git", "-C", linux_dir, "show", "--pretty=", "--name-only", commit, "--", "kernel/sched/"
        ], text=True)
        files = [l.strip() for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError:
        files = []
    file_basenames = [os.path.basename(p) for p in files]
    components = set()
    for fname in file_basenames:
        if fname in file_to_component:
            components.add(file_to_component[fname])
        else:
            components.add("UNKNOWN")
    return components

def get_year(commit):
    try:
        out = subprocess.check_output([
            "git", "-C", linux_dir, "show", "-s", "--format=%ad", "--date=format:%Y", commit
        ], text=True)
        year = out.strip()
    except subprocess.CalledProcessError:
        year = ""
    return year

def get_date_diff(commit1, commit2):
    try:
        out = subprocess.check_output([
            "git", "-C", linux_dir, "show", "-s", "--format=%ci", commit1,
        ], text=True)
        date1 = out.strip()
        out = subprocess.check_output([
            "git", "-C", linux_dir, "show", "-s", "--format=%ci", commit2,
        ], text=True)
        date2 = out.strip()
        print(date1, date2)
        dt1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S %z")
        dt2 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S %z")
        diff = dt2 - dt1
    except subprocess.CalledProcessError:
        diff = ""
    return diff