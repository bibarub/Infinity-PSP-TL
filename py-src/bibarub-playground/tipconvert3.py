#!/usr/bin/env python3

import os
import sys

import r11.tipsparser

def newlines(s):
    s = s.replace("%N", "\n")
    if s.endswith("\n"): s = s[:-1] + "%N"
    return s

game = "r11"

init_txt = f"/home/bibarub/Infinity-PSP-TL/text/other-psp-{game}-ru/init.bin.utf8.txt"
tips_txt = f"/home/bibarub/Infinity-PSP-TL/text/tips-psp-{game}.txt"
tips = r11.tipsparser.parse_tip_file(tips_txt)

if game == "r11":
    seg_tips_table = [0x7610, 0x7F78]
elif game == "e17":
    seg_tips_table = [0x65C4, 0x6EE4]
elif game == "n7":
    seg_tips_table = [0x7FBC, 0x8808]

with open(init_txt, "r", encoding="utf-8-sig") as f:
    initlines = f.read().splitlines()

tips_start = f";{seg_tips_table[0]:x};"
tips_end = f";{seg_tips_table[1]-8:x};"
tips_start_line, tips_end_line = None, None
for i, line in enumerate(initlines):
    if tips_start_line and tips_end_line: break
    if line.startswith(tips_start):
        tips_start_line = i
        continue
    if line.startswith(tips_end):
        tips_end_line = i+1
        continue
#print(tips_start_line, tips_end_line)
if not (tips_start_line and tips_end_line):
    print("failed to find tip boundary lines")
    sys.exit()
tiplines = filter(None, initlines[tips_start_line:tips_end_line+1])
previous_offset = None
i = 0
ru_title, ru_pages = None, []
fout = open("out.txt", "w", encoding="utf-8-sig")
def flush_tip():
    global ru_title, ru_pages
    tip = tips[i]
    fout.write("#"*100+"\n~tip~"+str(i)+"\n")
    for t in [("jp", tip.title.jp, tip.pages.jp), ("en", tip.title.en, tip.pages.en),
            ("cn", tip.title.cn, tip.pages.cn), ("ru", ru_title, ru_pages)]:
        lang, title, pages = t
        if not (title and pages): continue
        fout.write("~"+lang+"\n"+title+"\n")
        for j, p in enumerate(pages):
            fout.write("~"+lang+"~"+str(j)+"\n")
            fout.write(newlines(p))
            fout.write("\n~"+lang+"~"+str(j)+"~\n")
        fout.write("\n")
    fout.write("#"*100+"\n\n")
    ru_pages = []
for line in tiplines:
    if line[0] == ";":
        if line.startswith(";dupe:"):
            print(f"{previous_offset:x}: dupes must be removed")
            sys.exit()
        _, offset, _, ruline = line.split(";", 3)
        offset = int(offset, 16)
        if previous_offset:
            offset_diff = offset-previous_offset
            if offset_diff == 12:
                flush_tip()
                i += 1
            elif offset_diff == 4:
                ru_page = newlines(ruline)
                ru_pages.append(ru_page)
                previous_offset = offset
                continue
            else:
                print(previous_offset, offset)
                sys.exit()
        ru_title = ruline
        previous_offset = offset
    # elif jp_pages:
        # en_line = line.replace("%N", "\n")
        # if en_line[-1] == "\n": en_line = en_line[:-1]
        # en_pages.append(en_line)
    # elif jp_title:
        # en_title = line
flush_tip()
fout.close()
