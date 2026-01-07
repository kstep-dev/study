## Prerequisites

Before running any analyses or generating figures, ensure the following steps are completed:

1. Install the required Python dependencies:
   ```bash
   pip install -e .
   ```

2. Set up the necessary directories for Linux paths:
   ```bash
   python3 util/set_linux_dirs.py
   ```

3. Create the `result` directory to store generated outputs:
   ```bash
   mkdir result
   ```

## Generating Figures and Tables

Execute the following commands to reproduce the figures and tables presented in the paper. Please run each script from the project’s root directory.

- **Figure 4**  
  ```bash
  python3 overview/complexity.py --mode count
  python3 overview/complexity.py --mode plot
  ```

- **Table 1**  
  ```bash
  python3 overview/component_count.py
  ```

- **Figure 5**  
  ```bash
  python3 overview/lifetime.py
  ```

- **Figure 6**  
  ```bash
  python3 overview/backport.py
  ```

- **Figure 7**  
  ```bash
  python3 consequence/observability.py
  ```

- **Figure 8**  
  ```bash
  python3 consequence/consequence.py
  ```

- **Figures 9 and 10**  
  ```bash
  python3 testMethod/manifest_prevention.py
  ```

- **Figure 11**  
  ```bash
  python3 rootcause/root_cause.py
  ```

- **Figure 12**  
  ```bash
  python3 trigger/trigger_condition.py
  ```

All results, including plots and tables, will be saved in the `result` directory unless otherwise specified.