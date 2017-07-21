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
dw.core.dw_logging
================

Setup command logging
"""

from os.path import expanduser, exists
from os import makedirs
from time import strftime
import logging

# Log dir existence check ##
if not exists(expanduser('~')+"/.dw"):
    makedirs(expanduser('~')+"/.dw")
#########################################################

TIME_STRING = strftime("%Y_%m_%d_%H:%M:%S")
#########################################################

command_log = logging.getLogger('DW_comm')
command_log.setLevel(logging.INFO)

# create console handler and set level to debug
log_file = expanduser('~')+"/.dw/DW_"+TIME_STRING+".comm.log"
ch = logging.FileHandler(log_file)
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s \t %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
command_log.addHandler(ch)
#########################################################
fun_call_logger = logging.getLogger('DW_funCall')
fun_call_logger.setLevel(logging.INFO)

# create console handler and set level to debug
log_file = expanduser('~')+"/.dw/DW_"+TIME_STRING+".funCall.log"
chf = logging.FileHandler(log_file)
chf.setLevel(logging.INFO)

# create formatter
formatterf = logging.Formatter('%(asctime)s \t %(message)s')

# add formatter to ch
chf.setFormatter(formatterf)

# add ch to logger
fun_call_logger.addHandler(chf)
