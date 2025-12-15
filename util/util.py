import logging
import subprocess
from pathlib import Path
from datetime import datetime

PROJ_DIR = Path(__file__).parent.parent.resolve()
LINUX_ROOT_DIR = PROJ_DIR / "linux"
LINUX_MASTER_DIR = LINUX_ROOT_DIR / "master"
LINUX_MAINLINE_DIR = PROJ_DIR / "linux_mt"
RESULT_DIR = PROJ_DIR / "result"
DATA_FILE = PROJ_DIR / "data/bug_data.csv"

LINUX_DIRs = [PROJ_DIR / "linux/master", 
              PROJ_DIR / "linux/linux-v6.12.y",
              PROJ_DIR / "linux/linux-v6.6.y",
              PROJ_DIR / "linux/linux-v6.1.y",
              PROJ_DIR / "linux/linux-v5.15.y",
              PROJ_DIR / "linux/linux-v5.10.y",
              PROJ_DIR / "linux/linux-v5.4.y"]
def system(cmd: str):
    logging.info(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def system_output(cmd: str):
    logging.info(f"Running: {cmd}")
    return subprocess.check_output(cmd, shell=True, text=True)

def get_date_diff(commit1, commit2):
    date1 = system_output(f"git -C {LINUX_MAINLINE_DIR} show -s --format=%ci {commit1}").strip()
    date2 = system_output(f"git -C {LINUX_MAINLINE_DIR} show -s --format=%ci {commit2}").strip()

    date1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S %z")
    date2 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S %z")
    diff = date2 - date1
    return diff

def get_year(commit):
    out = system_output(f"git -C {LINUX_MAINLINE_DIR} show -s --format=%ad --date=format:%Y {commit}")
    return out.strip()