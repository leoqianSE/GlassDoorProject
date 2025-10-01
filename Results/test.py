from tools import openCVS
from pathlib import Path

filename = input("Please type the CVS file name: ")
filewithpath = r".\\Results\\"
print(f"Opening file: {filename}")
rows = openCVS(filewithpath+(filename))
print("\n".join(rows[1]))