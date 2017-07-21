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


import os
import time as sys_time
import glob
from collections import OrderedDict

import pylab
from numpy import array as np_array
from numpy import sum as np_sum
from numpy import mean as np_mean
from numpy import median as np_median
from numpy import max as np_max
from numpy import concatenate as np_concatenate

import tables

import astropy.time as atime
from astropy.io import fits

import dw.core.io as dwio

CLOCK =  1.0 / 200000000
DATA_KEYS = ['channels_l', 'channels_r', 'stokes_q', 'stokes_u', 'integration_l']

class OnOff():

    def __init__(self, directory, filename):
        self.filename = filename
        self.data = {}
        for dkey in DATA_KEYS:
            self.data[dkey] = None
        self.state = None
        if filename.find('on') > -1:
            self.state = 'on'
        if filename.find('off') > -1:
            self.state = 'off'
        if filename.find('cal') > -1:
            self.state = 'cal'

        self.n_samp = None

#        if self.state == -1:
#            return -1

        self.set_time()

    def set_time(self):
        hdulist = fits.open(self.filename)
        self.t_start = atime.Time(hdulist['DATA TABLE'].data[0][0], format='mjd')
        self.t_stop = atime.Time(hdulist['DATA TABLE'].data[-1][0], format='mjd')
        hdulist.close()


def get_on_off_time(directory):
#    l_dir = os.listdir(directory)
    l_dir = glob.glob(directory+'*')
    l_dir.sort()

    on_off_dict = OrderedDict()

    for d in l_dir:

#        filenames = os.listdir(d)
        filenames = glob.glob(d+'/*fits')
#        print(filenames)

        for filename in filenames:

            on_off = OnOff(directory, filename)
            s = filename.split('/')[-1]
            s = s.split('-')
            on_off_dict[s[0]+s[1]] = on_off

    return on_off_dict

def get_pola_data(dataset, on_off, clean = True):

    for key in on_off.keys():
        t0 = on_off[key].t_start.unix
        tf = on_off[key].t_stop.unix
        for dkey in DATA_KEYS:
            on_off[key].data[dkey] = np_array([x[dkey] for x in dataset.iterrows() if ((x['time']+x['subtime']*CLOCK) > t0) and ((x['time']+x['subtime']*CLOCK) < tf)])

        if clean and on_off[key].data[DATA_KEYS[0]].shape == (0,):
            on_off.pop(key)


def diff_on_off(on_off, i_start = 0, i_stop = -1):


    if i_start<0:
        i_start = len(on_off)+i_start

    if i_stop<0:
        i_stop = len(on_off)+i_stop

    n_samp = []
    for ii in xrange(i_start, i_stop):
        n_samp.append(on_off[on_off.keys()[ii]].data[DATA_KEYS[0]].shape[0])
    n_samp = min(n_samp)
    print n_samp
    data_diff = {}
    for dkey in DATA_KEYS:
        data_diff[dkey] = []

    for ii in xrange(i_start, i_stop, 2):
        for dkey in DATA_KEYS:
            print (str(ii)+": "+ on_off[on_off.keys()[ii]].state+" "+on_off[on_off.keys()[ii+1]].state)
            data_diff[dkey].append(on_off[on_off.keys()[ii]].data[dkey][:n_samp,:]-on_off[on_off.keys()[ii+1]].data[dkey][:n_samp,:])

    for dkey in DATA_KEYS:
        data_diff[dkey] = np_median(np_array(data_diff[dkey]),0)
    return data_diff
#    for key in on_off.keys()[i_start:i_stop]:
#        pass
#################################################################
# fileh = tables.open_file(fileout, mode = "w", title = "on off")

def write_on_off_sequence(fileh, on_off, name):
    class HdfTable(tables.IsDescription):

        """Define the flagging table structure for pytables"""

        channels_l = tables.Float32Col(32)
        channels_r = tables.Float32Col(32)
        stokes_q = tables.Float32Col(32)
        stokes_u = tables.Float32Col(32)
        time = tables.Int32Col()
        subtime = tables.Int32Col()
        integration_l = tables.Int32Col()

    group = fileh.create_group("/", name, name)
    group._f_setattr('Bandwith', '800')
    group._f_setattr('Channels', '32')
    table = fileh.create_table(group, 'Data', HdfTable, 'Data')

    rowh = table.row

    for key in on_off.keys():
        for ii in xrange(on_off[key].data[DATA_KEYS[0]].shape[0]):
            for dkey in DATA_KEYS:
                rowh[dkey] = on_off[key].data[dkey][ii,:]

            rowh['integration_l'] = 25000000
            rowh['time'] = ii
            rowh['subtime'] = 0

            rowh.append()

        for dkey in DATA_KEYS:
            rowh[dkey] = 0

        rowh['integration_l'] = 25000000
        rowh['time'] = ii
        rowh['subtime'] = 0

        rowh.append()

    table.flush()

def write_on_off(fileh, data_diff, name):

    class HdfTable(tables.IsDescription):

        """Define the flagging table structure for pytables"""

        channels_l = tables.Float32Col(32)
        channels_r = tables.Float32Col(32)
        stokes_q = tables.Float32Col(32)
        stokes_u = tables.Float32Col(32)
        time = tables.Int32Col()
        subtime = tables.Int32Col()
        integration_l = tables.Int32Col()


    group = fileh.create_group("/", name, name)
    group._f_setattr('Bandwith', '800')
    group._f_setattr('Channels', '32')
    table = fileh.create_table(group, 'Data', HdfTable, 'Data')

    rowh = table.row

    for ii in xrange(data_diff[DATA_KEYS[0]].shape[0]):
        for dkey in DATA_KEYS:
            rowh[dkey] = data_diff[dkey][ii,:]

        rowh['integration_l'] = 25000000
        rowh['time'] = ii
        rowh['subtime'] = 0

        rowh.append()
    table.flush()

def append(data, state):
    outd = {}
    for dkey in DATA_KEYS:
        outd[dkey] = []

    for key in data.keys():
        for dkey in DATA_KEYS:
            if data[key].state == state:
                outd[dkey].append(data[key].data[dkey])

    for dkey in DATA_KEYS:
        outd[dkey] = np_concatenate(outd[dkey],0)

    return outd


def plot_uq(data, channel_i, channel_f):

    int_l = data['integration_l'][0]
    El = data['channels_l'][:,channel_i: channel_f]/float(int_l)
    Er = data['channels_r'][:,channel_i: channel_f]/float(int_l)
    Si = (El+Er).astype(float)
    Su = data['stokes_u'][:,channel_i: channel_f]/Si/float(int_l)
    Sq = data['stokes_q'][:,channel_i: channel_f]/Si/float(int_l)
    pylab.plot(Su,Sq,'.')

