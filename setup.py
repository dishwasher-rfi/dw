# -*- coding: utf-8 -*-
# This file is part of
#
# Dish Washer - RFI cleaning tool for single dish radiotelescopes data
#
# Copyright (C) 2014-2015 - IRA-INAF
#
# Authors: Federico Cantini <cantini@ira.inaf.it>
#          Marco Bartolini <bartolini@ira.inaf.it>
#
# Mantainer: Francesco Bedosti <bedosti@ira.inaf.it>, Alessandra Zanichelli <a.zanichelli@ira.inaf.it>, Marco Bartolini <m.bartolini@ira.inaf.it>, Federico Cantini <cantini@ira.inaf.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from distutils.command.install import install as _install


def _install_libdw(dir):
    from subprocess import call
    from os import chdir
    chdir("libdw")
    call(["echo","Running","configure..."])
    call(["./autogen.sh"])
    call(["./configure","CFLAGS=-O2","JFLAGS=-O2","FFLAGS=-O2","CFLAGS=-fopenmp","LDFLAGS=-fopenmp", "LIBS=-fopenmp", "--prefix=${DW_PREFIX}"])
    call(["echo","Running","make..."])
    call(["make"])
    call(["echo","Running","make","install..."])
    call(["make","install"])
    chdir("../")

class install_libdw(_install):
    def run(self):
        self.execute(_install_libdw, (self.install_lib,),
                     msg="Installing libdw...")

        _install.run(self)

setup(
      name = "dw",
      version = "1.0",
      url = "http://www.example.com", #TODO: add a url
      description = "DishWasher - RFI cleaning tool fo single dish radiotelecope data",
      author = "Federico Cantini, Enrico Favero, Marco Bartolini",
      author_email = "cantini@ira.inaf.it, efavero@ira.inaf.it, bartolini@ira.inaf.it",
      maintainer = "Francesco Bedosti, Alessandra Zanichelli, Marco Bartolini, Federico Cantini",
      mantainer_email = "bedosti@ira.inaf.it, a.zanichelli@ira.inaf.it, m.bartolini@ira.inaf.it, cantini@ira.inaf.it",
      license = "gpl-3.0",
      packages = ["dw",
                  "dw.core",
                  "dw.gui",
                  "dw.flag",
                  "bpc",
                  "recurrence",],
      package_dir = { "dw" : "dw" }, #TODO: move sources in src
      package_data={"dw": ['data/*']},
      scripts = ["scripts/dwgui",
                 "scripts/bpcgui",
                 "scripts/writemetadata.py",
                 "scripts/readmeta.py"], #TODO: move executables in scripts
      requires = ["Cython(>0.13,<0.21)",
                  "tables(>=3.1.1)",
                  "PyQt4",
                  "guidata(>=1.6.1)",
                  "guiqwt(>=2.3.1)",], #TODO: add dependencies here
#      data_files = [("bitmaps", "gui/DW.png")],
      cmdclass={'install_libdw': install_libdw},
     )
