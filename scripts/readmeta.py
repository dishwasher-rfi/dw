#!/usr/bin/env python

# Copyright (C) 2014 - IRA-INAF
#
# Authors: Federico Cantini <cantini@ira.inaf.it>
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
readmeta.py
================

Utility to read metadata from hdf data files
"""


import time
import calendar
from numpy import round as np_round
from guidata.py3compat import to_text_string
import dw.core.io as dwio
CLOCK =  1.0 / 200000000

if __name__ == '__main__':
    import sys

    data_file = sys.argv[1]
    data_io = dwio.HdfIO()
    data_file_h = data_io.data_open(data_file)
    datasets = data_io.get_datasets(data_file_h)

    print ("File name: "+data_file)

    for dataset in datasets:
        print ("Table: "+to_text_string(dataset.th))
        gain = None
        shift = None
        integration = None
        print ("Time from epoch \t UT time \t\t\t\t gain \t integration \t shift")
        for row in dataset.th.iterrows():
            if (row['gain'] != gain) or (row['integration'] != integration) or (row['shift'] != shift):
#                print (str(row['time'])+" "+str(row['subtime'])+" "+
                ut_time = time.gmtime(row['time'])
                ut_msec = str(np_round(row['subtime']*CLOCK, 3)).split('.')
                print (str(np_round(row['time']+row['subtime']*CLOCK, 3))+" \t\t "+
                       str(ut_time.tm_year)+" "+
                       str(ut_time.tm_mon)+" "+
                       str(ut_time.tm_mday)+" "+
                       str(ut_time.tm_hour)+":"+
                       str(ut_time.tm_min)+":"+
                       str(ut_time.tm_sec)+"."+ ut_msec[1] + "\t "+
                       str(row['gain'])+" \t "+
                       str(row['integration'])+" \t\t "+
                       str(row['shift']))

                gain = row['gain']
                integration = row['integration']
                shift = row['shift']
        print "\n\r"

    print "\n\r"

    data_io.close(data_file_h)




