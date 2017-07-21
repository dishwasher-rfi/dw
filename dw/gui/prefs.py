# This file is part of
#
# Dish Washer - RFI cleaning tool for single dish radiotelescopes data
#
# Copyright (C) 2014 - IRA-INAF
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
dw.gui.prefs
============

Set global gui preferencies

Global variables
----------------
*X_SECTION_POS: Position of the x cross section plot [top, bottom]
*Y_SECTION_POS: Position of the y cross section plot [left, right]
*X_LABEL_PHYSICS: X axes label for physics measure unit
*Y_LABEL_PHYSICS: Y axes label for physics measure unit
*X_LABEL_ARBITRARY: X axes label for arbitrary measure unit
*Y_LABEL_ARBITRARY: Y axes label for arbitrary measure unit
*AXES_PHYS_UNIT: Default measure units for plots
"""

X_SECTION_POS = 'bottom'
Y_SECTION_POS = 'right'

X_LABEL_PHYSICS = 'MHz'
Y_LABEL_PHYSICS = 'Seconds'

X_LABEL_ARBITRARY = 'Channels'
Y_LABEL_ARBITRARY = 'Samples'

AXES_PHYS_UNIT = True

FLAG_SELECTED_CONFIRM = True
