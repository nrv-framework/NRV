# docs/copy_tutorials.py

import shutil
import os

SRC = os.path.abspath("../Tutorials")
DST = os.path.abspath("tutorials")

os.makedirs(DST, exist_ok=True)

for fname in os.listdir(SRC):
    if fname.endswith(".ipynb"):
        shutil.copy(os.path.join(SRC, fname), os.path.join(DST, fname))
        print(f"Copied: {fname}")
