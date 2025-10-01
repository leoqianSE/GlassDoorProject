import csv

def openCVS(filename):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        return rows
