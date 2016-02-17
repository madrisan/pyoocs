/*
 * License: GPLv3+
 * Copyright (c) 2016 Davide Madrisan <davide.madrisan@gmail.com>
 *
 * C extension for PyOOCS.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * The functions systemd_is_init and systemd_active are Copyright Red Hat, Inc.
 *
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <libgen.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int systemd_is_init() {
        char *path = realpath("/sbin/init", NULL);
        char *base = NULL;

        if (!path)
                return 0;
        base = basename(path);
        if (!base)
                return 0;
        if (strcmp(base, "systemd"))
                return 0;

        return 1;
}

int systemd_active() {
        struct stat a, b;

        if (lstat("/sys/fs/cgroup", &a) < 0)
                return 0;
        if (lstat("/sys/fs/cgroup/systemd", &b) < 0)
                return 0;
        if (a.st_dev == b.st_dev)
                return 0;
        if (!systemd_is_init())
                return 0;

        return 1;
}
