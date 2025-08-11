#!/bin/sh

[ -z "$GAME" ] && export GAME=e17

if  [ -z "$GIMCONV" ]; then
	if [ -e "./tools/GimConv/GimConv.exe" ] &&
		command -v "wine" >/dev/null 2>&1
	then
		export GIMCONV="wine ./tools/GimConv/GimConv.exe"
	elif command -v "gimconv" >/dev/null 2>&1
	then
		export GIMCONV="gimconv"
	fi
fi

unpack_bipcnt () {
	p=$(dirname $1)
	f=$(basename $1 .BIP)
	./bin/decompressbip $1 $p/$f.CNT || exit 1
	./bin/unpack_cnt $p/$f.CNT $p/$f/ || exit 1
}
bin_to_gim () {
	p=$(dirname $1)
	f=$(basename $1 .BIN)
	ext=$2
	[ -z "$ext" ] && ext=GIM
	mv $1 $p/$f.$ext
	[ -n "$GIMCONV" ] && $GIMCONV $p/$f.$ext -o $f.PNG || exit 1
}

for i in ${GAME}_etc/*.BIP; do
	[ -e $i ] || continue
	f=$(basename $i .BIP)
	[ "$f" = "TEX" ] && continue
	unpack_bipcnt $i || exit 1
	[ "$f" != "MAP" ] && [ "$f" != "SSE" ] && [ "$f" != "GAME" ] &&
		for j in ${GAME}_etc/$f/*.BIN; do
			bin_to_gim $j || exit 1
		done
done
for i in ${GAME}_etc/GAME/*.BIN; do
	[ -e $i ] || continue
	f=$(basename $i .BIN)
	if [ "$f" = "026" ]; then
		./bin/unpack_cnt $i ${GAME}_etc/GAME/$f/
		for j in ${GAME}_etc/GAME/$f/*.BIN; do
			bin_to_gim $j || exit 1
		done
	else
		bin_to_gim $i GIM || exit 1
	fi
done
for i in ${GAME}_etc/MAP/*.BIN; do
	[ -e $i ] || continue
	bin_to_gim $i TM2 || exit 1
done
for i in ${GAME}_etc/SSE/*.BIN; do
	[ -e $i ] || continue
	f=$(basename $i .BIN)
	mv $i ${GAME}_etc/SSE/$f.ADX
	command -v ffmpeg >/dev/null 2>&1 &&
		(ffmpeg -y -i ${GAME}_etc/SSE/$f.ADX ${GAME}_etc/SSE/$f.flac || exit 1)
done
if [ -e ${GAME}_etc/TEX.BIP ]; then
	./bin/decompressbip ${GAME}_etc/TEX.BIP ${GAME}_etc/TEX.CNT || exit 1
	./bin/unpack_cnt ${GAME}_etc/TEX.CNT ${GAME}_etc/TEX/ || exit 1
	mv ${GAME}_etc/TEX/000.BIN ${GAME}_etc/TEX/SSE.CNT
	mv ${GAME}_etc/TEX/001.BIN ${GAME}_etc/TEX/INFO.BIP
	mv ${GAME}_etc/TEX/002.BIN ${GAME}_etc/TEX/TEXT.BIP
	mv ${GAME}_etc/TEX/003.BIN ${GAME}_etc/TEX/GAME.BIP
	mv ${GAME}_etc/TEX/004.BIN ${GAME}_etc/TEX/OPTION.BIP
	mv ${GAME}_etc/TEX/005.BIN ${GAME}_etc/TEX/TIPS.BIP
	for i in ${GAME}_etc/TEX/*.BIN; do
		[ -e $i ] || continue
		bin_to_gim $i || exit 1
	done
	for i in ${GAME}_etc/TEX/*.BIP; do
		[ -e $i ] || continue
		f=$(basename $i .BIP)
		unpack_bipcnt $i || exit 1
		[ "$f" != "GAME" ] && 
			for j in ${GAME}_etc/TEX/$f/*.BIN; do
				bin_to_gim $j || exit 1
			done
	done
	for i in ${GAME}_etc/TEX/GAME/*.BIN; do
		[ -e $i ] || continue
		f=$(basename $i .BIN)
		if [ "$f" = "026" ]; then
			./bin/unpack_cnt $i ${GAME}_etc/TEX/GAME/$f/
			for j in ${GAME}_etc/TEX/GAME/$f/*.BIN; do
				bin_to_gim $j || exit 1
			done
		else
			bin_to_gim $i GIM || exit 1
		fi
	done
	./bin/unpack_cnt ${GAME}_etc/TEX/SSE.CNT ${GAME}_etc/TEX/SSE/ || exit 1
	for i in ${GAME}_etc/TEX/SSE/*.BIN; do
		f=$(basename $i .BIN)
		mv $i ${GAME}_etc/TEX/SSE/$f.ADX
		command -v ffmpeg >/dev/null 2>&1 &&
			(ffmpeg -y -i ${GAME}_etc/TEX/SSE/$f.ADX ${GAME}_etc/TEX/SSE/$f.flac || exit 1)
	done
fi
