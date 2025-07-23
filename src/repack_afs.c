#define _POSIX_C_SOURCE 1
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#if defined(__unix__) || defined(__unix) || (defined(__APPLE__) && defined(__MACH__))
#include <limits.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#elif defined(_WIN32)
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#define stat _stat
#ifndef PATH_MAX
#define PATH_MAX _MAX_PATH
#endif
#else
#define NO_TIME
#define PATH_MAX 1000
#endif

#define AFS_ALIGN(x) ((x+0x7ff)&~0x7ff) /* 2048(0x800)-byte alignment */
#define AFS_MAGIC "AFS"

#pragma pack(push, 1)
struct sta {
    unsigned pos;
    unsigned len;
} /* __attribute__((packed)) */;
#pragma pack(pop)

#pragma pack(push, 1)
struct stb {
    char name[32];
    unsigned short year;
    unsigned short month;
    unsigned short day;
    unsigned short hour;
    unsigned short minute;
    unsigned short second;
    unsigned len;
} /* __attribute__((packed)) */;
#pragma pack(pop)

int main(int argc, char *argv[]) {
    char *endir, magic[sizeof(AFS_MAGIC)];
    size_t sret;
    FILE *fin, *fout;
    unsigned i, entries, pos;
    struct sta *stas;
    struct stb *stbs;

    if (argc != 4) {
        printf("usage: %s in.afs out.afs en/\n", argv[0]);
        return 0;
    }
    endir = argv[3];

    fin = fopen(argv[1], "rb");
    if (!fin) {
        printf("failed to open %s\n", argv[1]);
        return 1;
    }

    sret = fread(magic, 1, sizeof(AFS_MAGIC), fin);
    assert(sret == sizeof(AFS_MAGIC));
    if (memcmp(magic, AFS_MAGIC, sizeof(AFS_MAGIC)) != 0) {
        printf("not an AFS archive\n");
        return 1;
    }

    sret = fread(&entries, sizeof(unsigned), 1, fin);
    assert(sret == 1);

    stas = malloc((entries+1)*sizeof(struct sta));
    assert(stas);
    sret = fread(stas, sizeof(struct sta), entries+1, fin);
    assert(sret == entries+1);

    stbs = malloc(entries*sizeof(struct stb));
    assert(stbs);
    fseek(fin, stas[entries].pos, SEEK_SET);
    sret = fread(stbs, sizeof(struct stb), entries, fin);
    assert(sret == entries);

    fout = fopen(argv[2], "wb");
    if (!fout) {
        printf("failed to open %s\n", argv[2]);
        return 1;
    }

    sret = fwrite(AFS_MAGIC, 1, sizeof(AFS_MAGIC), fout);
    assert(sret == sizeof(AFS_MAGIC));
    sret = fwrite(&entries, sizeof(unsigned), 1, fout);
    assert(sret == 1);
    pos = AFS_ALIGN(8+(entries+1)*sizeof(struct sta));
    for (i = 0; i < entries; ++i) {
        FILE *fh;
        char *buffer, name[PATH_MAX+31+1];
        int len;

        if (stas[i].pos == 0) {
            continue;
        }

        /* opening and mapping the file from the table */
        if ((strlen(endir) + strlen(stbs[i].name) + 2) > PATH_MAX) {
            printf("file path is too long! %s/%s\n", endir, stbs[i].name);
            return 1;
        }
        sprintf(name, "%s/%s", endir, stbs[i].name);
        fh = fopen(name, "rb");
        if (fh) {
#ifndef NO_TIME
            struct stat filestat;
            struct tm *modtime;
#endif
            printf("<- %s\n", stbs[i].name);
            fseek(fh, 0, SEEK_END);
            len = ftell(fh);
            assert(len > 0);
            rewind(fh);
            buffer = malloc(len);
            assert(buffer);
            sret = fread(buffer, 1, len, fh);
            assert((int)sret == len);
            fclose(fh);
#ifndef NO_TIME
            if (stat(name, &filestat) != -1) {
                modtime = localtime(&filestat.st_mtime);
                if (modtime) {
                    stbs[i].year = modtime->tm_year+1900;
                    stbs[i].month = modtime->tm_mon+1;
                    stbs[i].day = modtime->tm_mday;
                    stbs[i].hour = modtime->tm_hour;
                    stbs[i].minute = modtime->tm_min;
                    stbs[i].second = modtime->tm_sec;
                } else {
                    printf("failed to localize time\n");
                }
            } else {
                printf("failed to get file stat\n");
            }
#endif
        } else {
            fseek(fin, stas[i].pos, SEEK_SET);
            /* or just copying the current content */
            len = stas[i].len;
            buffer = malloc(len);
            assert(buffer);
            sret = fread(buffer, 1, len, fin);
            assert((int)sret == len);
        }

        stas[i].pos = pos;
        stas[i].len = len;
        stbs[i].len = len;

        fseek(fout, pos, SEEK_SET);
        sret = fwrite(buffer, 1, len, fout);
        assert((int)sret == len);
        pos += AFS_ALIGN(len);

        free(buffer);
    }
    fclose(fin);
    stas[entries].pos = pos;
    stas[entries].len = sizeof(struct stb)*entries;
    fseek(fout, 8, SEEK_SET);
    sret = fwrite(stas, sizeof(struct sta), entries+1, fout);
    assert(sret == entries+1);
    fseek(fout, stas[entries].pos, SEEK_SET);
    sret = fwrite(stbs, sizeof(struct stb), entries, fout);
    assert(sret == entries);
    fseek(fout, AFS_ALIGN(stas[entries].pos+stas[entries].len)-1, SEEK_SET);
    fputc(0, fout);

    free(stas);
    free(stbs);
    fclose(fout);
    return 0;
}
