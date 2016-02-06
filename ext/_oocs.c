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
 */

#include <Python.h>
#include "_oocs.h"

static PyObject *
_oocsext_runlevel(PyObject *self, PyObject *args) {
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

#if PY_MAJOR_VERSION >= 3
static char oocsext_doc[] =
"";

static struct PyModuleDef oocsext_module = {
        PyModuleDef_HEAD_INIT,
        "_oocsext",   /* name of module */
        oocsext_doc,  /* module documentation, may be NULL */
        -1,           /* size of per-interpreter state of the module,
                         or -1 if the module keeps state in global variables. */
        PyOOCSExtMethods
};

PyMODINIT_FUNC
PyInit__oocsext(void) {
        return PyModule_Create(&oocsext_module);
}

#else

void
init_oocsext(void) {
        (void) Py_InitModule("_oocsext", PyOOCSExtMethods);
}
#endif

int
main(int argc, char *argv[]) {
        /* Initialize the Python interpreter */
        Py_Initialize();
}
