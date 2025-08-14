#!/usr/bin/env python3

# this script takes images from the "edited" folder, figures out which pixels in them were "erased" compared to the originals,
# and then outputs the coordinates of different pixels into a text file as a python dictionary.

# for editing the images, i use the "Magic Wand" tool in Paint.NET with "Tolerance" set to 0% and "Flood Mode" set to "Global".
# after using the tool, i invert the selection (Ctrl+I), select the "Eraser" tool (Hardness 100%, Spacing 1%, Unsmoothed path, Aliased rendering),
# and erase pixels that look out of place.

import os
import sys
from PIL import Image, ImageChops

n7_chr = "\\\\wsl$\\Ubuntu\\home\\binarin\\Infinity-PSP-TL\\n7_chr"
edited = "C:\\Users\\binarin\\Desktop\\edited"
out_file = os.path.join(edited, "sprite_nullify_coords.py")

fout = open(out_file, "w", encoding="ascii", newline="\n")
fout.write("nullify_coords = {\n")
for fname in os.listdir(edited):
    fname = fname.upper()
    name, ext = os.path.splitext(fname)
    if not ext.upper() == ".PNG": continue
    if len(name) >= 7 and name[-1] in ('N', 'D'):
        name = name[:-1]
    new = Image.open(os.path.join(edited, fname)).convert("RGBA")
    og = Image.open(os.path.join(n7_chr, fname)).convert("RGBA")
    diff = [i for i, x in enumerate(ImageChops.difference(og, new).getdata()) if x[3] != 0]
    width = og.width
    og.close()
    new.close()
    if diff:
        fout.write(f"    \"{name}\": (")
        for p in diff:
            x, y = p%width, p//width
            fout.write(f"({x}, {y}), ")
        fout.write("),\n")
fout.write("}\n")
fout.close()
