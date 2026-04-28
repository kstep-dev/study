## Artifact of kernel scheduler bugs study
This repository contains the source code for

**kSTEP: Characterization and Controlled Testing of Linux CPU Scheduler Bugs (OSDI '26)**

## Overview
The instructions will reproduce the key results in Figure 4-12, and Table 1. The entire process can take around 10 minutes.

## Environment

We reserved three servers ([c220g5](https://docs.cloudlab.us/hardware.html#(part._cloudlab-wisconsin)) in Cloudlab), one for each reviewer. Please add your SSH public key to the [spreadsheet](https://docs.google.com/spreadsheets/d/1HB2LAww1IrGjMe0bNfvnsGPhwDcuICfwcPPICZBJEpE/edit?usp=sharing ) next to the IP address of the server you will use.

Inside each server, you can access the bug study repo with

```bash
cd ~/project/study
```

## Prerequisites

Before running any analyses or generating figures, ensure the following steps are completed:

1. Install the required Python dependencies with `uv`:
   ```bash
   # Skip if uv has been installed
   curl -LsSf https://astral.sh/uv/install.sh | sh 
   source $HOME/.local/bin/env
   uv sync
   source .venv/bin/activate
   ```

2. Set up the necessary directories for Linux paths:
   ```bash
   python util/set_linux_dirs.py
   ```

3. Create the `result` directory to store generated outputs:
   ```bash
   mkdir result
   ```

## Generating Figures and Tables

Execute the following commands to reproduce the figures and tables presented in the paper. Please run each script from the project’s root directory.

- **Figure 4**  
  ```bash
  python overview/complexity.py --mode count
  python overview/complexity.py --mode plot
  ```

- **Table 1**  
  ```bash
  python overview/component_count.py
  ```

- **Figure 5**  
  ```bash
  python overview/lifetime.py
  ```

- **Figure 6**  
  ```bash
  python overview/backport.py
  ```

- **Figure 7**  
  ```bash
  python consequence/observability.py
  ```

- **Figure 8**  
  ```bash
  python consequence/consequence.py
  ```

- **Figures 9 and 10**  
  ```bash
  python testMethod/manifest_prevention.py
  ```

- **Figure 11**  
  ```bash
  python rootcause/root_cause.py
  ```

- **Figure 12**  
  ```bash
  python trigger/trigger_condition.py
  ```

The results are saved at ``~/project/study/result/``. You can download the plots to review them.

```bash
scp -r 'Tingjia@{ServerIP}:~/project/study/result/' /LOCAL/DIR
```
