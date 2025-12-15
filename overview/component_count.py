import csv
from collections import Counter
from util import *

def component_count():
    component_bug_counts = Counter()
    hashes = list(read_data().keys())
    for hash in hashes:
        components = get_components(hash)

        for component in components:
            component_bug_counts[component] += 1

    return component_bug_counts

if __name__ == "__main__":
    component_bug_counts = component_count()
    print(component_bug_counts)