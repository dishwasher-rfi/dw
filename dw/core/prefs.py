# This file is part of
#
# Dish Washer - RFI cleaning tool for single dish radiotelescopes data
#
# Copyright (C) 2014-2015 - IRA-INAF
#
# Authors: Federico Cantini <cantini@ira.inaf.it>
#          Marco Bartolini <bartolini@ira.inaf.it>
#
# Mantainer: Federico Cantini <cantini@ira.inaf.it>
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
dw.core.prefs
=============

Set global gui preferencies

Global variables
----------------

HDF flagset compression parameters (see pytables doc for details)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* HDF_COMP_LIB: Compression library for HDF output
* HDF_COMP_LEV: Compression level for HDF output
* HDF_SHUFFLE: Whether to use or not "shuffle" filter togheter with compression

Default values for flagging sets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* FLAG_TRUE: Value for flagged "pixels" in flag matrices
* FLAG_FALSE: Value for unflagged "pixels" in flag matrices

* CLOCK: Data acquisition board clock
"""

HDF_COMP_LIB = 'zlib'
HDF_COMP_LEV = 1
HDF_SHUFFLE = True

FLAG_TRUE = 1
FLAG_FALSE = 0

CLOCK =  1.0 / 200000000