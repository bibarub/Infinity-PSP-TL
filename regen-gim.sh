#!/bin/sh

if command -v "git" >/dev/null 2>&1 && [ "$REGEN_ALL" != true ]; then
	check_replace() {
		basepath="$(dirname "$1")/$(basename "$(basename "$1" .PNG)" .png)"
		[ -e "$basepath.GIM" ] || [ -e "$basepath.gim" ] || return 0
		git ls-files --error-unmatch "$1" >/dev/null 2>&1 || return 0
		git diff --exit-code "$1" >/dev/null 2>&1 || return 0
		return 1
	}
else
	check_replace() {
		return 0
	}
fi

if  [ -z "$GIMCONV" ]; then
	if [ -e "./tools/GimConv/GimConv.exe" ] &&
		command -v "wine" >/dev/null 2>&1
	then
		export GIMCONV="wine $PWD/tools/GimConv/GimConv.exe"
	elif command -v "gimconv" >/dev/null 2>&1
	then
		export GIMCONV="gimconv"
	else
		echo "gimconv not found. set the GIMCONV environment variable accordingly."
		exit 1
	fi
fi

cd assets

for i in bg-*-*/*.PNG assets/ev-*-*/*.PNG; do
	[ -e "$i" ] || continue
	check_replace "$i" && (../py-src/thumbhelper.py "$i" || exit 1)
done
for i in etc-*-*/*/*.PNG assets/etc-*-*/*.PNG; do
	[ -e "$i" ] || continue
	check_replace "$i" && ($GIMCONV "$i" -o "$(basename "$i" .PNG).GIM" || exit 1)
done

for i in nowloading/*.png; do
	[ -e "$i" ] || continue
	check_replace "$i" && ($GIMCONV "$i" -N -o "$(basename "$i" .png).gim" || exit 1)
done

exit 0
