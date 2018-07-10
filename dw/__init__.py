# This file is part of
#
# Dish Washer - RFI cleaning tool for single dish radiotelescopes data
#
# Copyright (C) 2014 - IRA-INAF
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

"""
Dish Washer - RFI cleaning tool for single dish radiotelescopes data
====================================================================

Copyright (C) 2014 - IRA-INAF

Authors: Federico Cantini <cantini@ira.inaf.it>
         Enrico Favero <efavero@ira.inaf.it>
         Marco Bartolini <bartolini@ira.inaf.it>

Mantainer: Francesco Bedosti <bedosti@ira.inaf.it>, Alessandra Zanichelli <a.zanichelli@ira.inaf.it>, Marco Bartolini <m.bartolini@ira.inaf.it>, Federico Cantini <cantini@ira.inaf.it>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Sub-packages
------------
* dw.core - core modules: data definition, data I/O, commands implementation
* dw.flag - flagging algorithms (to be implemented)
* dw.gui  - graphical user interface
"""

import pkg_resources
__version__ =  version = pkg_resources.require("dw")[0].version
