#!/usr/bin/env python3

import sys
import struct
import r11

f = open(sys.argv[1], "rb")
f.seek(0x60)
o = struct.unpack("<I", f.read(4))[0]
f.seek(o)

songs = []
while (o := struct.unpack("<I", f.read(4))[0]) != 0:
    songs.append(o)

lyrics = []
for i in songs:
    f.seek(i)
    lyrics.append([])
    proto = []
    while True:
        text_offset, timecode = struct.unpack("<2I", f.read(8))
        if text_offset == 0: break
        proto.append((timecode, text_offset))
    for j in proto:
        f.seek(j[1])
        b = f.read(128)
        while b'\0' not in b:
            b += f.read(128)
        lyrics[-1].append((j[0], r11.r11_bytes_to_str(b.split(b'\0')[0], "ru").replace("\"", "\\\"")))
f.close()

print("jukebox = [")
for i in lyrics:
    print(f"    [")
    for j in i:
        print(f"        ({j[0]}, r\"{j[1]}\"),")
    print("    ],")
print("]")
