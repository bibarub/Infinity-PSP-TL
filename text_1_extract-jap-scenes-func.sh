#!/bin/sh
[ -z "$GAME" ] && export GAME=e17
extract_scene () {
	echo "Extracting scene $1 text"
	# process translation files
	./bin/extract_scene_text ${GAME}_mac/$1.SCN text/tmp-${GAME}/mac-psp-jp/$1.txt || exit 1
}

mkdir -p text/tmp-${GAME}/mac-psp-jp/
