#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261122 (Python 3.13, stdlib only).

The image is built by build_entry.py from art/*.webp and saved as
entry.png beside this file. This program copies it to the grader's
output directory: /output/entry.png, or $MAKEFUN_OUTPUT_DIR when set.
No network, no randomness: every run writes the same bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUT, "entry.png"))
print("wrote", os.path.join(OUT, "entry.png"))
