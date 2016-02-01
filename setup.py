NAME = 'pyoocs'
VERSION = '0'
DESCRIPTION = "Out of Compliance Scanner for Linux"

LONG_DESCRIPTION = """\
PyOOCS is a customizable and modular security scanner for Linux.

This project is at an early stage of development and only a few
modules are currently available:

 - environment: checks the root environment
 - filesystem: checks for mandatory filesystems and mount options
      and for system files permissions
 - kernel: check the kernel runtime configuration
 - packages: make some checks on installed packages and rpm database
 - services: check whether a list of services are running or not
 - sudo: checks for root rights given to users and security issues

The checks are configurable via a JSON file.

In particular three different output formats are supported:

 - console: print the output to the console
 - json: print the output to the console, but in json format
 - html: run an http server for displaying the result of the scan.

The html mode is intended for debug and testing only.
Use the script oocs-htmlviewer.py instead."""

AUTHOR = "Davide Madrisan"
AUTHOR_EMAIL = "davide.madrisan@gmail.com"
LICENSE = "GPL"
PLATFORMS = "Linux"
URL = "https://github.com/madrisan/pyoocs"

from distutils.core import setup, Extension
from distutils.command.install_scripts import install_scripts

class oocs_install_scripts(install_scripts):
    def run(self):
        install_scripts.run(self)

_oocs = Extension('_oocs', sources = ['ext/_oocs.c'])

if __name__ == '__main__':

    setup (
        name = NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        license = LICENSE,
        platforms = PLATFORMS,
        url = URL,
        scripts = ['pyoocs.py', 'pyoocs-htmlviewer.py'],
        packages = ['oocs'],
        ext_modules = [_oocs],
        cmdclass = { 'install_scripts': oocs_install_scripts })
