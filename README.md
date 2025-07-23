This project ports translations of the Infinity visual novel series to the PSP.

As of now, the following games are supported:
- Never7: English
- Ever17: English, Russian
- Remember11: English, Simplified Chinese

### Credits
Without these people, this project would not have existed.
- [Lemnisca Translations](https://web.archive.org/web/20180905090319/http://tlwiki.org/index.php?title=Never_7): English translation of Never7.
- Hirameki International, [Himmel Edition](https://www.reddit.com/r/InfinitySeries/comments/mbkbhn/ever17_himmel_edition_repost/) Team: English translation of Ever17.
- [dsp2003 & SanLtd Team](http://wks.arai-kibou.ru/ever17.php): Russian translation of Ever17.
- [R11 Translation Team](https://web.archive.org/web/20180819171103/https://tlwiki.org/?title=Remember11_-_the_age_of_infinity): English translation of Remember11.
- [R11 Gestalt Edition Team](https://old.reddit.com/r/InfinitySeries/comments/mbk11z/remember11_gestalt_edition_repost): Improved translation of Remember11.
- [dreambottle](https://github.com/dreambottle): Remember11 translation port, initial engine research and public tools for modifying the game.
- [malucart](https://github.com/malucard): Never7 translation port, BIP image format research.
- [Phantom](https://github.com/PhantomZero9): Ever17 translation edits.
- [R11 Team](https://m.vk.com/wall-76654048_1217): Cyrillic font, Russian menu translations.
- [TimTH98](https://github.com/TimTH98): Russian graphics for the Ever17 translation port.
- [Nightdavisao](https://github.com/nightdavisao): English UI graphics for Ever17.
- [MKCA](https://github.com/MKCAMK): removal of the character limit from the text log of Ever17.
- [badspot](https://github.com/badspott): English UI graphics for Never7 and Remember11, font glyphs for typographic quotation marks.
- [Qlonever](https://github.com/Qlonever): English UI graphics for Never7, Remember11 BGM research.

### Useful Links

[**Patch Downloads**](https://github.com/bibarub/Infinity-PSP-English/releases)

...

Current status
-----------

Scenes: Translated  
Append stories (N7): Okuhiko Cure and Yuka Cure are translated. Other append stories have speaker names replaced in them.  
Backgrounds/CGs (E17): Translated  
Shortcuts (init.bin): Translated  
TIPS (init.bin): Translated. Ever17 tips translation is ongoing.  
Names (init.bin): Translated  
Chronology (R11) (init.bin): Not translated in English. Translated in Chinese.  
Menus (BOOT.BIN): Translated. Help messages for the settings are not translated.  
Font (FONT00.FOP): Tweaked for English text, reduced spacing. EN glyphs are brightened and sharpened. Japanese quotation marks for speech are replaced with typographical quotes.


For Developers
-----------

This project is a bunch of scripts and programs in bash, python and C. Python and C programs unpack and repack game resources, decode text, fonts etc. Shell scripts automate the process of applying the translation. They should should work both on macos and linux.

For the full run:

1. Put your ISO at `iso/Never7-jap.iso`, `iso/Ever17-jap.iso`, or `iso/Remember11-jap.iso`

2. Set the `GAME` environment variable to `n7`, `e17`, or `r11`, depending on the game you are patching. Example: `export GAME=e17`

3. Set the `TL_SUFFIX` environment variable to `en`, `cn`, or `ru`. Language support varies by game.

4. Run `./make.sh`

5. The resulting iso will be in the `iso` folder.

`./generate-patches.sh` can be used to generate xdelta3 diff files.

`./generate-eboot-pbp.sh` can generate a EBOOT.PBP file that runs on OFW.

For further details, read the contents of shell scripts (and other source files).

##### Dependencies:

The following tools should be available in your PATH:

`7z mkisofs gcc python3 xdelta3`

The `pillow` python module should be installed, either via pip or your distro's package manager.

- `mkisofs` is a part of the `cdrtools` package.

- Brew command for macos to install dependencies: `brew install cdrtools python3 xdelta`.

- Last tested to be working with python 3.12, will likely work with later versions as well.
