import subprocess
import os
from datetime import datetime
import json

from pathlib import Path
import logging

# Use worktrees for the target branch/tag
LINUX_MASTER_DIR = Path(os.path.abspath(os.path.join(os.getcwd(),"linux/master")))

def add_worktree(version: str, linux_master_dir: Path, linux_dir: Path):
    if linux_dir.exists():
        print(f"Linux {version} already cloned to {linux_dir}")
    else:
        os.system(f"cd {linux_master_dir} && git worktree prune -v")
        os.system(f"cd {linux_master_dir} && git worktree add {linux_dir} {version}")

original_cwd = os.getcwd()

def collect_sched_touched_files():
    """
    For the 'master' branch and the specified stable trees in the linux/ git repo,
    scan through the git commits (from 2020-01-01 to now),
    and record all touched files within 'kernel/sched'.
    For each version, we check out the branch/tag and scan its history.
    """
    linux_versions = [
        "master",
        "linux-6.12.y",
        "linux-6.6.y",
        "linux-6.1.y",
        "linux-5.15.y",
        "linux-5.10.y",
        "linux-5.4.y",
    ]

    repo_path = "linux"
    commit_titles = {}
    # unique_commit_titles = set()
    since_date = "2020-01-01"
    until_date = datetime.now().strftime("%Y-%m-%d")

    for tree in linux_versions:
        
        LINUX_WORKTREE_DIR = Path(os.path.join(original_cwd, repo_path, f"{tree}"))
        add_worktree(tree, LINUX_MASTER_DIR, LINUX_WORKTREE_DIR)

        print(LINUX_WORKTREE_DIR, LINUX_MASTER_DIR)
        os.chdir(LINUX_WORKTREE_DIR)

        # Pull latest (optional, comment out if undesired)
        # subprocess.run(["git", "pull"], check=False)
        log_cmd = [
            "git", "log",
            "--since={}".format(since_date),
            "--until={}".format(until_date),
            "--pretty=format:%H %s"
        ]
        log_cmd += ["--", "kernel/sched"]
        raw_commits = subprocess.check_output(log_cmd, text=True).splitlines()
        
        seen_titles = set()
        commit_hashes = []
        for line in raw_commits:
            if not line.strip():
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue  # skip malformed
            chash, title = parts

            if title.lower().startswith("merge") or title.lower().startswith("sched_ext"):
                continue
            title_key = title.strip().lower()
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            commit_hashes.append(chash)

        for chash in commit_hashes:
            # For this commit, check if its commit message contains "Fixes: <sha>"
            show_full_cmd = [
                "git", "show", "-s", "--format=%B", chash, "--", "kernel/sched/"
            ]
            full_msg = subprocess.check_output(show_full_cmd, text=True, errors='ignore')


            # Search for lines starting with "Fixes: " followed by a sha
            import re
            fixes_match = re.search(r"^Fixes:\s*([0-9a-fA-F]{7,40})", full_msg, re.MULTILINE)
            
            if not fixes_match:
                continue  # skip commits that are not explicit fixes or don't match keywords

            fixes_sha = fixes_match.group(1)
            # Get the commit title
            show_cmd = [
                "git", "show", "-s", "--format=%s", chash, "--", "kernel/sched/"
            ]
            output = subprocess.check_output(show_cmd, text=True).strip()

            if output:
                if output in commit_titles.keys():
                    commit_titles[output]["tree"].append(tree)
                    if chash != commit_titles[output]["hash"]:
                        commit_titles[output]["backport"].append(tree)
                else:
                    url = f"https://github.com/gregkh/linux/commit/{chash}"
                    # Get all reachable tags containing fixes_sha

                    # Avoid slow "git tag --contains" by using "git describe --tags --contains  which is much faster

                    tag_cmd = [
                        "git", "describe", "--tags", "--contains", fixes_sha
                    ]
                    describe_output = subprocess.check_output(tag_cmd, text=True).strip()
                    # git describe will output like "v4.9-rc1-20-gHEX", take the first word as tag (or up to first '-')
                    first_tag = describe_output.split('-')[0] if describe_output else ""

                    commit_titles[output] = { "hash": chash, "tree": [tree], "backport": [], "url": url, "buggy_sha": fixes_sha, "buggy_tag": first_tag  }   
                    # print(commit_titles[output])
                    if tree != "master":
                        commit_titles[output]["backport"].append(tree)

    return commit_titles

# To use:
results = collect_sched_touched_files()

print(results)
os.chdir(original_cwd)

import csv

with open("sched_fixes.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "hash", "tree", "url", "backport", "buggy_sha", "buggy_tag"])
    for title, info in results.items():
        writer.writerow([
            title,
            info["hash"],
            ";".join(info["tree"]),  # Serialize list as semicolon-separated for easier viewing
            info["url"],
            ";".join(info["backport"]),  # Serialize list as semicolon-separated for easier viewing
            info["buggy_sha"],  # Serialize list as semicolon-separated for easier viewing
            info["buggy_tag"]  # Serialize list as semicolon-separated for easier viewing
        ])
