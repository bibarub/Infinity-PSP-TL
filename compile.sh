#!/bin/sh
SRC=./src

CFLAGS="-std=c99 -O1 -Wall -Wextra"

mkdir -p bin
gcc $CFLAGS -o bin/extract_scene_text $SRC/extract_scene_text.c && \
gcc $CFLAGS -o bin/unpack_afs $SRC/unpack_afs.c && \
gcc $CFLAGS -o bin/repack_afs $SRC/repack_afs.c && \
gcc $CFLAGS -o bin/decompressbip $SRC/decompressbip.c $SRC/lzss.c && \
gcc $CFLAGS -o bin/compressbip $SRC/compressbip.c $SRC/lzss.c && \
gcc $CFLAGS -o bin/unpack_cnt $SRC/unpack_cnt.c && \
gcc $CFLAGS -o bin/pack_cnt $SRC/pack_cnt.c || exit 1

if ! (command -v sign_np >/dev/null 2>&1 || [ -e tools/sign_np/sign_np ]); then
	rm -rf tools/sign_np/sign_np tools/sign_np/*.o tools/sign_np/libkirk/*.a tools/sign_np/libkirk/*.o
	make -C tools/sign_np || exit 1
fi
if ! (command -v armips >/dev/null 2>&1 || [ -e tools/armips/build/armips ]); then
	rm -rf tools/armips/out/
	mkdir tools/armips/out
	cmake -S tools/armips -B tools/armips/out && \
	cmake --build tools/armips/out -j$(nproc --all)
fi
