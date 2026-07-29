#!/usr/bin/env python3

import os

from string import ascii_letters

import r11

fw_latin = "".join(chr(ord(x)+0xff00-0x20) for x in ascii_letters)

mishaps = (0x11b0, 0x11c0, 0x11d0, 0x11f4, 0x13bc)

r11en = "text/other-psp-r11-en/init.bin.utf8.txt"
r11ru = "text/other-psp-r11-ru/init.bin.utf8.txt"

def read_init_txt(path):
    ret = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i] == "\n" or lines[i][0] == "#":
            i += 1
            continue
        if lines[i][0] in "+-=?":
            i += 2
            continue
        if lines[i][0] != ';':
            print(lines[i])
            exit()
        _, off, _len, jp = lines[i].split(";", 3)
        off = int(off, 16)
        _len = int(_len)
        jp = jp.rstrip("\n")
        en = None
        if lines[i+1] != "\n" and lines[i+1][0] != '#':
            en = lines[i+1].rstrip("\n")
            i += 1
        ret[off] = (_len, jp, en)
        i += 1
    return ret

def write_init_txt(path, _dict):
    with open(path, "w", encoding="utf-8-sig") as f:
        for off, (_len, jp, tl) in _dict.items():
            f.write(f";{off:x};{_len};{jp}\n")
            if tl:
                f.write(tl+"\n")
            f.write("\n")

def latinify(s):
    return r11.r11_bytes_to_str(r11.str_to_r11_bytes(s, "ru"), "en")

def fw_to_hw(s):
    out = ""
    for c in s:
        if c in fw_latin:
            c = chr(ord(c)-0xff00+0x20)
        out += c
    return out

def hw_to_fw(s):
    out = ""
    for c in s:
        if c in ascii_letters:
            c = chr(ord(c)+0xff00-0x20)
        out += c
    return out

def proper_tl(nice_dict, bad_dict):
    ret = {}
    for k, v in nice_dict.items():
        off = k
        _len, jp, en = v
        ru = bad_dict[k][2] or bad_dict[k][1]
        if ru != "???" and (off in mishaps or latinify(ru) in (jp, en)):
            ru = None
        if not ru and any(c in fw_latin for c in jp):
            ru = fw_to_hw(jp)
        ret[off] = (_len, jp, ru)
    return ret

def main():
    write_init_txt("out.txt", proper_tl(read_init_txt(r11en), read_init_txt(r11ru)))

if __name__ == "__main__":
    main()
