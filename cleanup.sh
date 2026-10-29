#!/bin/sh

[ -z "$GAME" ] && export GAME=e17
[ -z "$TL_SUFFIX" ] && export TL_SUFFIX=en

rm -f assets/bg-${GAME}-${TL_SUFFIX}/*.R11
rm -f assets/ev-${GAME}-${TL_SUFFIX}/*.R11
for i in ev bg etc mac ; do rm -rf ${GAME}_${i}/; rm -rf ${GAME}_${i}_${TL_SUFFIX}/; done
[ -d "text/chapters-psp-${GAME}" ] && rm -rf text/mac-psp-${GAME}-${TL_SUFFIX}-utf8
rm -rf ${GAME}_chr/ ${GAME}_chr_mod/ ${GAME}_se/ ${GAME}_se_mod/ ${GAME}_iso_extracted/
rm -rf bin/
rm -rf workdir-${GAME}
rm -rf text/mac-${GAME}-${TL_SUFFIX}-only*/
rm -rf text/tmp-${GAME}
rm -rf text/font/${GAME} text/font/${GAME}-${TL_SUFFIX}
rm -f patch/${GAME}-${TL_SUFFIX}.xdelta
rm -f iso/${GAME}-${TL_SUFFIX}.iso
rm -rf pbp/${GAME}-${TL_SUFFIX}/
[ "$CLEANUP_TOOLS" = "true" ] && rm -rf tools/extract-xiso/build tools/armips/build tools/armips/out tools/sign_np/sign_np tools/sign_np/*.o tools/sign_np/libkirk/*.a tools/sign_np/libkirk/*.o || true
