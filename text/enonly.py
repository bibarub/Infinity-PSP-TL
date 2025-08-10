#!/usr/bin/env python3

import os

game = os.environ['GAME'] if 'GAME' in os.environ else 'e17'
lang = os.environ['TL_SUFFIX'] if 'TL_SUFFIX' in os.environ else "en"

if not os.path.exists(f'mac-{game}-{lang}-only-utf8'): os.mkdir(f'mac-{game}-{lang}-only-utf8')
files = os.listdir(f'mac-psp-{game}-{lang}-utf8')
for filename in files:
    with open(os.path.join(f'mac-psp-{game}-{lang}-utf8', filename), encoding='UTF-8') as f:
        lines = f.readlines()

    del lines[:3]

    enlines = []
    for i in range(len(lines) // 3):
        enlines.append(lines[i*3+2])

    with open(os.path.join(f'mac-{game}-{lang}-only-utf8', filename), 'w', encoding='UTF-8') as f:
        f.writelines(enlines)
