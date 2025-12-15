from util import *

if __name__ == "__main__":
    if LINUX_MAINLINE_DIR.exists():
        print(f"Linux mainline directory already exists at {LINUX_MAINLINE_DIR}")
    else:
        system(f"git clone https://github.com/torvalds/linux {LINUX_MAINLINE_DIR}")

    if not LINUX_ROOT_DIR.exists():
        LINUX_ROOT_DIR.mkdir(parents=True)

    if LINUX_DIRs[0].exists():
        print(f"Linux stable master directory already exists at {LINUX_DIRs[0]}")
    else:
        system(f"git clone https://github.com/gregkh/linux {LINUX_DIRs[0]}")

    for i in range(1, len(LINUX_DIRs)):
        if LINUX_DIRs[i].exists():
            print(f"Linux stable {i} directory already exists at {LINUX_DIRs[i]}")
        else:
            system(f"cd {LINUX_DIRs[0]} && git worktree prune -v")
            # print(f"cd {LINUX_DIRs[0]} && git worktree add {LINUX_DIRs[i]} {LINUX_DIRs[i].name}")
            system(f"cd {LINUX_DIRs[0]} && git worktree add {LINUX_DIRs[i]} {LINUX_DIRs[i].name}")

    print("Linux directories set successfully")
