import csv
import pandas as pd
from util import *

def parse_multi_value(x):
    # Parse possibly quoted, comma-separated strings.
    if pd.isna(x):
        return []
    parts, curr, in_quotes = [], '', False
    for char in str(x):
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            if curr.strip():
                parts.append(curr.strip().strip('"'))
            curr = ''
        else:
            curr += char
    if curr.strip():
        parts.append(curr.strip().strip('"'))
    return [p.strip() for p in parts if p.strip()]

def read_data():
    results = {}
    with open(DATA_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hash = row["hash"]
            root_cause = row["root cause"]
            trigger_condition = parse_multi_value(row["Trigger condition"])
            discover = row["discover"]
            prevention = parse_multi_value(row["afterfix"])
            consequence = parse_multi_value(row["consequence"])
            visibility = row["visibility"]
            results[hash] = {
                "root_cause": root_cause, 
                "trigger_condition": trigger_condition, 
                "discover": discover, 
                "prevention": prevention, 
                "consequence": consequence, 
                "visibility": visibility
            }

    return results