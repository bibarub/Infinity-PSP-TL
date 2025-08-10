Scene files
============
TODO

Special Sequences
============

%N - New line

%K - wait for keypress

%P - pagebreak

%O - another pagebreak sequence. Used in fullscreen text

%p - appears right before decision blocks.

%V - wait until voice line is over

%LL / %LC / %LR - align to left, center, or right

%TS[3 digits][text]%TE - links text to TIPS

%FS[text]%FE - text fades in as 1 block, instead of letter-by-letter

%C[4 hex digits] - color

%T030 - delay. WARNING: On pc it has %T[\d\d] (2 digits) format, but on psp it needs to have 3 digits!

%X070 - Fixed offset from line start (also 010, 050 in game texts)

%XS[2 digits], %XE - %XS sets fixed character width. %XE resets it.

%n - ??? (in BOOT.BIN)

%S - ??? (in BOOT.BIN) (usually %n%S or %N%S)


BOOT.BIN
============

To disasm BOOT.BIN with prxtool:
`tools/prxtool -n tools/psp-NID-Prometheus.xml -o boot-disasm.txt -w workdir/BOOT.BIN`

`readelf -a BOOT.BIN` info about elf structure

Text occurrences:

Don't forget to add/subtract A0 to table values, which is an elf header size

table - text locations

12bb8c: - 12116c:1243d0(123fb0 jap) (approx) - section with text;
  0x12144c - scrolling menu text, delimited by new lines (%N), ends at 0x12871c.
136760:136aa0 - 12483с:128620
136ac0: sample text block, used in settings

137528:141520 - large empty area. Test if this can be used as an scratchpad/area for long strings.


The engine has a limit of 480 simultaneous characters on the scene, which causes crashes when the buffer is overflown. The workaround is to insert more %K%P sequences to the text.
@bibarub: this may further be restricted by the amount of visual effects currently applied. mainly affects full-screen text sequences in never7.


init.bin
============

file has many(all?) same strings as the pc version of init.bin + all the TIPS + the chronology + other stuff

tables:
<br>
1140:1d38 - covers "names/init" section
<br>
7610:7f78 - TIPS
<br>
90dc:ac98 - Chronology

We skip all these sections:
```python3
    if 0x47f0 <= table_offs < 0x5350: continue
    if 0x7f90 <= table_offs < 0x871c: continue
    if 0x7520 <= table_offs < 0x7610: continue
```

ba68:dc40 names and init.txt content. This also is the first text occurrence in file.
<br>
dc40: - file names(don't modify!)
<br>
12b57:12ca3 - song-related stuff
<br>
12ca3:130ea - (Endings?)
<br>
130ea: - a strange untranstlated text block. Strings start with イラスト：左 (GoogTransl: 'Illustration:Left')
<br>
134de: - Song lyrics
<br>
14c30:2464c - Tips. They are ordered differently to the pc version.
<br>
26be8: - Chronology start
<br>

BTW, analyzing this file revealed that developers actually transliterated characters' names this way:
```
うしろのしょうめんのぼく／Uni
鏡の中のワタシ／Cocoro
天より墜ちたオレ／Satoru
```
(proof: 0x260a0 in init.bin)

Fonts
============

The game uses FONT00 (lzss-compressed .FOP), found in etc.afs, as a main font.

See folder `text/font/` for scripts.

Game engine adds additional space between glyphs in scene texts. This has been
fixed (additional spacing removed) by one of the patches in `boot-patches.asm`.

Glyph 751 is a whitespace.

"BIP" file format
============
LZSS-compressed data with a 32-bit unsigned integer prepended to it, specifying the uncompressed file size.
Note that, in the widespread lzss.c implementation of LZSS, the whitespace character is used to fill the buffer. BIP, however, requires the buffer to be filled with NULL characters (0x0).


"CNT" file format
============
A simple container format. Starts with a 32-bit unsigned integer specifying the amount of files. It is then followed by 32-bit integers specifying the lengths of the files stored within the container.
Data in the file starts right after the header. All data is 16-bit aligned. Thus, the starting offset of data can be calculated using the following formula: ((count+1)*4+15)&~15

In games supported by this repository, CNT containers mostly hold UI elements and system sound effects, compressed to "BIP".
UI elements are 8-bit indexed GIM images, and sound effects are ADX audio files.

The "TEX" container contains copies of the SSE, INFO, TEXT, GAME, OPTION, and TIPS containers.
All containers but SSE are additionally compressed to BIP.
It seems that the aforementioned containers are only accessed through the TEX container by the game, essentially leaving the BIP files contained in etc.afs unused.

"R11" image format
============
Also called "BIP" by some people. In games supported by this project, contains an 8-bit indexed image.
The actual image is first split into 30x30 chunks. Then, the chunks are extended to 32x32 by appending a 1px "frame", consisting of pixels from other chunks.
The chunks are then placed in the initial order (for CG/BG) into an image with a width of 512 pixels (fixed).

Most BG and all CG can be converted to PNG with the "r11_to_png.py" script. Sprite conversion is only supported for Never7 (with the exception of a few Yuka sprites), as sprites in other games are stored in a different variation of the format.
The "to_r11.py" script handles image conversion to the "R11" format. Only 480x360 images are supported.

GIM format
============
Graphics format found in some T2P files after they are decompressed.
Can be converted to png with GimConv (Proprietary Sony tool, Google it).

TIM2 format
============

Graphics format found in some T2P files after they are decompressed.


Useful links
============

HOME menu language: http://bbs.blacklabel-translations.com/showthread.php?tid=35&pid=84

TIM2 format: http://wiki.vg-resource.com/wiki/TIM2
