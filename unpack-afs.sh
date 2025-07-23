#!/bin/bash
# extract all the japanese gametext.
#
GIMCONV="./tools/GimConv/GimConv.exe"
DECOMPRESS="./bin/decompressbip"
UNPACK_AFS="./bin/unpack_afs"
UNPACK_CNT="./bin/unpack_cnt"

[ -z "$GAME" ] && export GAME=e17
[ -z "$TL_SUFFIX" ] && export TL_SUFFIX=en

RES_DIR="${GAME}_iso_extracted/PSP_GAME/USRDIR"
WORK_DIR="./workdir-${GAME}"

unpack_afs () {
	echo Unpacking $1.afs
	$UNPACK_AFS $WORK_DIR/$1.afs ${GAME}_$1/ || exit 1
}

unpack_cnt () {
	echo Unpacking $1.CNT
	mkdir -p ${GAME}_etc/$1
	$UNPACK_CNT ${GAME}_etc/$1.CNT ${GAME}_etc/$1/ || exit 1
}

mkdir -p $WORK_DIR
cp ${GAME}_iso_extracted/PSP_GAME/SYSDIR/BOOT.BIN $WORK_DIR/BOOT.BIN
#mv ${GAME}_iso_extracted/PSP_GAME/SYSDIR/EBOOT.BIN $WORK_DIR/EBOOT.BIN

cp $RES_DIR/mac.afs $WORK_DIR/mac.afs
cp $RES_DIR/etc.afs $WORK_DIR/etc.afs
cp $RES_DIR/init.bin $WORK_DIR/init.bin

([ "$GAME" = "e17" ] || [ -d "assets/se-${GAME}" ]) && cp $RES_DIR/se.afs $WORK_DIR/se.afs
[ -d "assets/bg-${GAME}-${TL_SUFFIX}" ] && cp $RES_DIR/bg.afs $WORK_DIR/bg.afs
[ -d "assets/ev-${GAME}-${TL_SUFFIX}" ] && cp $RES_DIR/ev.afs $WORK_DIR/ev.afs

[ "$GAME" = "e17" ] && unpack_afs se

PKG=mac
rm -rf ${GAME}_$PKG/
unpack_afs $PKG
echo "Decompressing..."
#for i in text/chapters-psp/[A-Z0-9]*_[0-9]*.txt ; do
for i in ${GAME}_mac/*.BIP; do
	#f=$(basename $i .txt)
	f=$(basename $i .BIP)
	#echo "Decompressing $f"
	$DECOMPRESS ${GAME}_$PKG/$f{.BIP,.SCN} || exit 1
done
$DECOMPRESS ${GAME}_$PKG/SHORTCUT{.BIP,.SCN} || exit 1

PKG=etc
rm -rf ${GAME}_$PKG/
unpack_afs $PKG
#for i in $PKG/*.T2P ; do
#	f=$(basename $i .T2P)
#	$DECOMPRESS $PKG/$f{.T2P,.GIM} || exit 1
#	$GIMCONV $PKG/$f.GIM -o $f.png -e17
#done
for i in ${GAME}_$PKG/*.FOP ; do
	f=$(basename $i .FOP)
	$DECOMPRESS ${GAME}_$PKG/$f{.FOP,.FNT} || exit 1
done
for i in assets/etc-${GAME}-${TL_SUFFIX}/*/ ; do
	[ -d "$i" ] || continue
	f=${i%%/}; f=${f##*/}
	if [ ! -d "${GAME}_etc/TEX" ] && ([ "$f" = "INFO" ] || [ "$f" = "TEXT" ] ||
		[ "$f" = "GAME" ] || [ "$f" = "OPTION" ] || [ "$f" = "TIPS" ] || [ "$f" = "SSE" ])
	then
		$DECOMPRESS ${GAME}_etc/TEX{.BIP,.CNT} || exit 1
		unpack_cnt TEX || exit 1
	fi
	$DECOMPRESS ${GAME}_etc/$f{.BIP,.CNT} || exit 1
	unpack_cnt $f || exit 1
done

mkdir -p text/font/${GAME}
cp ${GAME}_$PKG/FONT00.FNT text/font/${GAME}/FONT00.FNT

#PKG=bg
#rm -rf ${GAME}_$PKG/
#unpack_afs $PKG
#for i in ${GAME}_$PKG/*.BIP; do
#	f=$(basename $i .BIP)
#	#echo "Decompressing $f"
#	$DECOMPRESS ${GAME}_$PKG/$f{.BIP,.R11} || exit 1
#done
#for i in ${GAME}_$PKG/*.T2P; do
#		f=$(basename $i .T2P)
#		#echo "Decompressing $f"
#		$DECOMPRESS ${GAME}_$PKG/$f{.T2P,.GIM} || exit 1
#done

cd text/font/${GAME}
python3 ../../../py-src/extract_font.py pnghalf || exit 1
cd ../../..

$DECOMPRESS $WORK_DIR/init.bin $WORK_DIR/init.dec
