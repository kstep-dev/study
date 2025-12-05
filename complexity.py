import os
import subprocess
import matplotlib.pyplot as plt
import json

file_to_component = {
    # Scheduler Foundations: Core
    "sched.c": "core",
    "sched_features.h": "core",

    "sched_clock.c": "clock",
    "sched_autogroup.c": "topology",
    "sched_autogroup.h": "topology",
    "sched_idletask.c": "special tasks",
    "sched_stoptask.c": "special tasks",

    # Scheduler Foundations: Account
    "sched_stats.c": "accounting",

    # debug
    "sched_debug.c": "debug",

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

    "clock.c": "clock",
    "auto_group.c": "topology",
    "auto_group.h": "topology",
    "topology.c": "topology",
    "autogroup.c": "topology",
    "autogroup.h": "topology",
    "core_sched.c": "topology",
    "build_policy.c": "topology",
    "build_utility.c": "topology",

    "smp.h": "topology",
    "idle_task.c": "special tasks",
    "idle.c": "special tasks",
    "stop_task.c": "special tasks",

    "cpufreq.c": "CPU behavior control",
    "cpufreq_schedutil.c": "CPU behavior control",
    "isolation.c": "CPU behavior control",

    # Scheduler Foundations: Account
    "stats.c": "accounting",
    "stats.h": "accounting",
    "cputime.c": "accounting",
    "cpuacct.c": "accounting",
    "cpuacct.h": "accounting",
    "psi.c": "accounting",

    # debug
    "debug.c": "debug",

    # Scheduling Policy: Fair
    "fair.c": "fair",
    "proc.c": "fair",

    # Scheduling Policy: PELT
    "pelt.c": "Load estimation",
    "pelt.h": "Load estimation",
    "loadavg.c": "Load estimation",
    "sched-pelt.c": "Load estimation",
    "sched-pelt.h": "Load estimation",

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
    "membarrier.c": "mem",
}

components = set(file_to_component.values())

def get_versions(linux_dir, min_version="v3.0", max_version="v6.17"):
    """
    List all tags in linux_dir matching v3.0 to v6.x, 
    sorted in version order (oldest to newest).
    """
    # List all tags
    tag_lines = subprocess.check_output(
        ['git', '-C', linux_dir, 'tag', '-l', 'v[2-6]*'],
        text=True
    ).splitlines()
    # Filter tags within the version range
    tags = []
    for tag in tag_lines:
        if '.' not in tag:
            continue
        # Remove '-rc' suffices for version compare, exclude -rc releases
        if '-rc' in tag:
            continue
        # Lexical check for min/max, fallback to sort by git tag order at the end
        tags.append(tag)
    # Sort using git tag order for correctness
    tags = subprocess.check_output(
        ['git', '-C', linux_dir, 'tag', '--list'] + tags,
        text=True
    ).split()
    # Only keep those >= min_version and <= max_version
    def version_tuple(v):
        # parse out v3.0 -> [3,0]
        v = v.lstrip('v').split('-')[0].split('.')
        try:
            return tuple(int(x) for x in v)
        except:
            return (0,0,0)
    min_vt = version_tuple(min_version)
    max_vt = version_tuple(max_version)
    filtered = []
    for tag in tags:
        vt = version_tuple(tag)
        if min_vt <= vt <= max_vt:
            print(tag)
            filtered.append(tag)
    filtered = sorted(filtered, key=version_tuple)
    return filtered

def count_sched_loc(linux_dir):
    """
    For each version, check out the tag, then sum lines of code for files in kernel/sched
    Returns: list of (version_tag, loc_count)
    """
    original_head = subprocess.check_output(['git', '-C', linux_dir, 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
    versions = get_versions(linux_dir)
    
    results = {}
    for tag in versions:
        # Checkout the tag (detached HEAD)
        subprocess.check_call(['git', '-C', linux_dir, 'checkout', '-fq', tag])
        # For Linux 3.0, 3.1, 3.2, count kernel/sched*.c; otherwise, count kernel/sched/*
        if tag in ["v3.0", "v3.1", "v3.2"]:
            # Schedule .c files in kernel/ for these versions
            sched_dir = os.path.join(linux_dir, 'kernel')
            sched_pattern = lambda fn: fn.startswith("sched") and fn.endswith(".c")
        else:
            sched_dir = os.path.join(linux_dir, 'kernel', 'sched')
            sched_pattern = lambda fn: fn != "Makefile"

        if os.path.exists(sched_dir):
            result = {component: 0 for component in components}
            for fn in filter(sched_pattern, os.listdir(sched_dir)):
                if fn not in file_to_component.keys():
                    print(f"File {fn} not in file_to_component")
                    continue
                component = file_to_component[fn]
                if component not in components:
                    print(f"Component {component} not in components")
                    continue
                path = os.path.join(sched_dir, fn)
                loc = 0
                with open(path, encoding="latin1", errors="ignore") as f:
                    loc += sum(1 for _ in f)
                result[component] += loc
            print(tag, result)
            results[tag] = result
    # Restore original HEAD
    subprocess.check_call(['git', '-C', linux_dir, 'checkout', '-fq', original_head])
    return results

if __name__ == "__main__":
    # Set the path of your linux/ repo (should be a local git repo)
    LINUX_DIR = "linux_mt"

    data = count_sched_loc(LINUX_DIR)
    with open("sched_loc.json", "w") as f:
        json.dump(data, f)
    # plot_sched_loc(LINUX_DIR)
