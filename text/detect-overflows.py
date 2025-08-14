#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re

def main():
  # Standard psp engine limit is 480 --dreambottle
  # bibarub: depending on how many visual effects are currently applied,
  # the amount of characters the game can handle is decreased further,
  # as the GE command buffer may overflow.
  # for Never7, i found the maximum "safe" amount of characters to be ~370.
  # just in case, i set the warning threshold even lower, to 350.
  warn_chars_screen = 350;
  warn_chars_line = 45*4;

  game = os.environ["GAME"] if "GAME" in os.environ else "e17"
  lang = os.environ["TL_SUFFIX"] if "TL_SUFFIX" in os.environ else "en"

  fdir = f"mac-{game}-{lang}-only-utf8"
  files = os.listdir(fdir);

  for fname in files:
    f = open(os.path.join(fdir, fname), "r", encoding="UTF-8")
    lns = f.readlines()
    f.close()
    print(fname)

    chars = 0;
    lines = 0;
    clear = True;

    for i, line in enumerate(lns):
      if clear:
        clear=False
        chars=0
        lines=0

      line = line[:-1] # strip \n
      allseq = re.findall(r"(?:%[KkPpNnOVW]|%\d{3}|%T\d{3}|%C[\dA-F]{4}|%X\d{3}|%TS\d{3}|%TE|%F[SE]|%L[CLR])+", line);
      if (allseq):
        if allseq[-1].endswith("%P") or allseq[-1].endswith("%p") or allseq[-1].endswith("%O"):
          clear = True;
        for seq in allseq:
          line = line.replace(seq, "", 1);

      if ("%" in line):
        # % sequence wasn't cut out for some reason
        print (i+1, ":", line, ':', allseq)

      chars+=len(line)
      lines+=1;
      if (chars > warn_chars_screen):
        print("Line %d (%d): %d chars in last %d lines."
              % (i+1, (i+1)*3+3, chars, lines))
        print ("'%s'" % line)
      # if (len(line) > warn_chars_line):
      #   print(("Line  %d: %d chars on the line!") % (i+1, len(line)))



if __name__ == '__main__':
  main();
