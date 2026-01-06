pip install -e .
python3 util/set_linux_dirs.py

python3 overview/backport.py
python3 overview/lifetime.py
python3 overview/complexity.py --mode count
python3 overview/complexity.py --mode plot
python3 overview/component_count.py

python3 consequence/observability.py
python3 consequence/consequence.py