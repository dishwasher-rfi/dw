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
writemetadata.py
================

Utility to write metadata in hdf data files
"""

import time
import calendar
from numpy import interp as np_interp

import dw.core.io as dwio

META_DICT_KEYS = ['azim', 'elev', 'asc', 'decl', 'name', 'local_osc']

def date_to_epoch(date):
    l = date.split('.')
    epoch_int = float(calendar.timegm(time.strptime(l[0], '%Y-%m-%d %H:%M:%S')))
    epoch_dec = float('.'+l[1])

    return epoch_int+epoch_dec

class Meta(object):

    def __init__(self, meta_file):
        self.meta_file = meta_file
        self.pointer = 1

    def open_meta(self):
        self.meta_file_h = open(self.meta_file)

    def close_meta(self):
        self.meta_file_h.close()

    def get_meta(self):
        metadata = []
        for line in self.meta_file_h:
            elem = {}
            sl = line.split('\t')
            elem['date'] = sl[0]
            elem['epoch'] = date_to_epoch(sl[0])
            sli = 0
            for key in META_DICT_KEYS:
                sli = sli +1
                elem[key] = sl[sli]
            metadata.append(elem)

        self.metadata = metadata

    def get_meta_d(self):
        metadata = {}
        metadata['date'] = []
        metadata['epoch'] = []
        for key in META_DICT_KEYS:
            metadata[key] = []

        for line in self.meta_file_h:
            sl = line.split('\t')
            metadata['date'].append(sl[0])
            metadata['epoch'].append(date_to_epoch(sl[0]))
            sli = 0
            for key in META_DICT_KEYS:
                sli = sli +1
                metadata[key].append(sl[sli])

        self.metadata = metadata

    def get_meta_interp_v(self, epoch_time_l):
        self.meta_int = {}
        for key in [key for key in META_DICT_KEYS if 'name' != key]:
            self.meta_int[key] = np_interp(epoch_time_l,
                                             self.metadata['epoch'],
                                             self.metadata[key] )

        for epoch_time in epoch_time_l:
         idx, self.meta_int['name'] = min(enumerate(self.metadata['epoch']),
                                          key=lambda x: abs(x[1]-epoch_time))
        return self.meta_int

    def get_meta_interp_1(self, epoch_time):
        if (epoch_time < self.metadata['epoch'][0]) or (epoch_time > self.metadata['epoch'][-1]):
            print ("WARNING: Observation time outside metadata range")
            return -1

        if self.metadata['epoch'][self.pointer-1] > epoch_time:
            self.pointer = 1


        while self.metadata['epoch'][self.pointer] < epoch_time:
            self.pointer = self.pointer + 1
            if self.pointer > len(self.metadata['epoch']):
                return -1

        meta_int = {}
        for key in [key for key in META_DICT_KEYS if 'name' != key]:
                    meta_int[key] = np_interp(epoch_time,
                                     [self.metadata['epoch'][self.pointer-1],self.metadata['epoch'][self.pointer]],
                                     [self.metadata[key][self.pointer-1], self.metadata[key][self.pointer]])


        if  (self.metadata['epoch'][self.pointer] - epoch_time) > (epoch_time - self.metadata['epoch'][self.pointer-1]):
            meta_int['name'] = self.metadata['name'][self.pointer]
        else:
            meta_int['name'] = self.metadata['name'][self.pointer-1]

        return meta_int

    def get_meta_interp(self, epoch_time_l):
        meta_int_array = {}
        for key in META_DICT_KEYS:
            meta_int_array[key] = []

        for epoch_time in epoch_time_l:
            meta_int = self.get_meta_interp_1(epoch_time)
            for key in META_DICT_KEYS:
                meta_int_array[key].append(meta_int[key])

        return meta_int_array


class Data(object):

    def __init__(self, data_file):
        self.data_io = dwio.HdfIO()
        self.data_file = data_file

    def open_data(self):
        self.data_file_h = self.data_io.data_open(self.data_file)

    def close_data(self):
        self.data_io.close(self.data_file_h)

    def get_datasets(self):
        self.datasets = self.data_io.get_datasets(self.data_file_h)

    def upd_dataset(self, dataset, m):
        ep_list = self.data_io.get_epoch_time_scale(dataset)

        meta_dict = m.get_meta_interp(ep_list)
        self.data_io.upd_columns(self.data_file_h,
                                 dataset,
                                 start = 0,
                                 stop = len(meta_dict['azim']),
                                 step = 1,
                                 columns=[meta_dict['azim'], meta_dict['elev'],meta_dict['asc'],meta_dict['decl'],meta_dict['name'],meta_dict['local_osc']],
                                 names=['azim','elev','asc','decl','name','local_osc'])




if __name__ == '__main__':
    import sys

    data_file = sys.argv[1]
    meta_file = sys.argv[2]

    d = Data(data_file)
    m = Meta(meta_file)

    d.open_data()
    m.open_meta()

    m.get_meta_d()
    d.get_datasets()

    for dataset in d.datasets:
        d.upd_dataset(dataset.th, m)


    d.close_data()
    m.close_meta()
