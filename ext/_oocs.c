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
 * The function utmp_get_runlevel() is Copyright 2010 Lennart Poettering
 */

#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <errno.h>

#ifndef __USE_GNU
# define __USE_GNU  1
#endif
#include <utmpx.h>

#include "_oocs.h"

int utmp_get_runlevel(int *runlevel, int *previous) {
        struct utmpx *found, lookup = { .ut_type = RUN_LVL };
        int r;
        const char *e;

        assert(runlevel);

        /* If these values are set in the environment this takes
         * precedence. Presumably, sysvinit does this to work around a
         * race condition that would otherwise exist where we'd always
         * go to disk and hence might read runlevel data that might be
         * very new and does not apply to the current script being
         * executed. */

        e = getenv("RUNLEVEL");
        if (e && e[0] > 0) {
                *runlevel = e[0];

                if (previous) {
                        /* $PREVLEVEL seems to be an Upstart thing */

                        e = getenv("PREVLEVEL");
                        if (e && e[0] > 0)
                                *previous = e[0];
                        else
                                *previous = 0;
                }

                return 0;
        }

        if (utmpxname(_PATH_UTMPX) < 0)
                return -errno;

        setutxent();

        found = getutxid(&lookup);
        if (!found)
                r = -errno;
        else {
                int a, b;

                a = found->ut_pid & 0xFF;
                b = (found->ut_pid >> 8) & 0xFF;

                *runlevel = a;
                if (previous)
                        *previous = b;

                r = 0;
        }

        endutxent();

        return r;
}

static PyObject * _oocsext_runlevel(PyObject *self, PyObject *args) {
        int runlevel;

        if (utmp_get_runlevel(&runlevel, NULL) < 0) {
                PyErr_SetString(PyExc_OSError, "Unknown runlevel");
                return NULL;
        }
        return Py_BuildValue("c", runlevel <=0 ? 'N' : runlevel);
}

static PyMethodDef PyOOCSExtMethods[] = {
        { "runlevel", _oocsext_runlevel, METH_VARARGS,
          "Print the current SysV runlevel." },
        { NULL, NULL, 0, NULL }        /* Sentinel */
};

PyMODINIT_FUNC init_oocsext(void) {
        (void) Py_InitModule("_oocsext", PyOOCSExtMethods);
}


int main(int argc, char *argv[]) {
        Py_SetProgramName(argv[0]);
        Py_Initialize();
}
