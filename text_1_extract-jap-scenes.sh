#!/bin/bash

. ./text_1_extract-jap-scenes-func.sh

[ -z "$GAME" ] && export GAME=e17
[ -z "$TL_SUFFIX" ] && export TL_SUFFIX=en

if [ "$GAME" = "n7" ]; then
	for i in n7_mac/USER[0-9]*.SCN; do
		f=$(basename $i .SCN)
		[ -e text/mac-psp-n7-${TL_SUFFIX}-utf8/$f.txt ] && continue
		extract_scene $f
	done
fi
if [ -d text/chapters-psp-${GAME} ]; then
	./text_1_extract-jap-scenes-full.sh
fi
echo "Done."
