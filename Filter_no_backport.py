import csv

with open("sched_fixes.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        buggy_tag = row.get("buggy_tag", "")
        backports = row.get("backport", "")
        trees = row.get("tree", "")

        # parse backport and tree fields, splitting by ';'
        backport_list = [x for x in backports.split(";") if x] if backports else []
        tree_list = [x for x in trees.split(";") if x] if trees else []

        last_backport = backport_list[-1] if backport_list else ""
        last_tree = tree_list[-1] if tree_list else ""

        print(f"buggy_tag: {buggy_tag}, last_backport: {last_backport}, last_tree: {last_tree}")
