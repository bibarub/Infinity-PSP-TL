#define _POSIX_C_SOURCE 1
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#if defined(__unix__) || defined(__unix) || (defined(__APPLE__) && defined(__MACH__))
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <utime.h>
#include <time.h>
#elif defined(_WIN32)
#include <sys/utime.h>
#include <sys/types.h>
#include <direct.h>
#include <time.h>
#define mkdir(path, mode) _mkdir(path)
#define chdir _chdir
#define utime _utime
#define utimbuf _utimbuf
#else
#define NO_EXTENSIONS
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
    char magic[sizeof(AFS_MAGIC)];
    size_t sret;
    FILE *fin;
    unsigned i, entries, stbspos;
    struct sta *stas;
    struct stb *stbs;

#ifndef NO_EXTENSIONS
    char *jadir;
    if (argc != 2 && argc != 3) {
        printf("usage: %s in.afs [ja/]\n", argv[0]);
        return 0;
    }
    jadir = (argc == 3) ? argv[2] : NULL;
#else
    if (argc != 2) {
        printf("usage: %s in.afs\n", argv[0]);
        return 0;
    }
#endif

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

    stbspos = (stas[entries].pos != 0) ? stas[entries].pos
        : (stas[entries-1].pos + AFS_ALIGN(stas[entries-1].len));

    stbs = malloc(entries*sizeof(struct stb));
    assert(stbs);
    fseek(fin, stbspos, SEEK_SET);
    sret = fread(stbs, sizeof(struct stb), entries, fin);
    assert(sret == entries);

#ifndef NO_EXTENSIONS
    if (jadir) {
        (void)mkdir(jadir, 0755);
        if (chdir(jadir) == -1) {
            printf("failed to cd to %s\n", jadir);
            return 1;
        }
    }
#endif
    for (i = 0; i < entries; ++i) {
        char *buffer;
        FILE *fout;
#ifndef NO_EXTENSIONS
        time_t epochtime;
        struct tm time;
#endif
        if (stas[i].pos == 0) {
            continue;
        }
#ifndef NO_EXTENSIONS
        printf("-> %s\n", stbs[i].name);
#else
        printf("-> %s (%02hu.%02hu.%hu %02hu:%02hu:%02hu)\n", stbs[i].name,
            stbs[i].day, stbs[i].month, stbs[i].year, stbs[i].hour, stbs[i].minute, stbs[i].second
        );
#endif
        if (strpbrk(stbs[i].name, "/\\:")) {
            printf("unsafe filename\n");
            return 1;
        }
        fout = fopen(stbs[i].name, "wb");
        if (!fout) {
            printf("failed to create %s\n", stbs[i].name);
            return 1;
        }
        buffer = malloc(stas[i].len);
        assert(buffer);
        fseek(fin, stas[i].pos, SEEK_SET);
        sret = fread(buffer, 1, stas[i].len, fin);
        assert(sret == stas[i].len);
        sret = fwrite(buffer, 1, stas[i].len, fout);
        assert(sret == stas[i].len);
        free(buffer);
        fclose(fout);
#ifndef NO_EXTENSIONS
        time.tm_sec = stbs[i].second;
        time.tm_min = stbs[i].minute;
        time.tm_hour = stbs[i].hour;
        time.tm_mday = stbs[i].day;
        time.tm_mon = stbs[i].month-1;
        time.tm_year = stbs[i].year-1900;
        time.tm_isdst = -1;
        epochtime = mktime(&time);
        if (epochtime != -1) {
            struct utimbuf times;
            times.actime = epochtime;
            times.modtime = epochtime;
            if (utime(stbs[i].name, &times) == -1) {
                printf("failed to set time (%02hu.%02hu.%hu %02hu:%02hu:%02hu)\n",
                    stbs[i].day, stbs[i].month, stbs[i].year, stbs[i].hour, stbs[i].minute, stbs[i].second
                );
            }
        }
#endif
    }

    fclose(fin);
    free(stas);
    free(stbs);
    return 0;
}
