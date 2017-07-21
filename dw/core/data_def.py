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
dw.core.data_def
================

Implement data structure, convenient methods and functions to access the data
and command logging

Functions
---------
* dw_version - Return the package version
* to2D - Return a 2D array where each row is the 1D array in input

Classes
-------
* DWData - implement data structure and convenient methods to access the data
"""

from __future__ import print_function

from numpy import zeros as np_zeros
from numpy import max as np_max
from numpy import concatenate
from numpy import linspace as np_linspace
from numpy import divide as np_divide
#from numpy import array as np_array
from numpy import arctan as np_arctan
from numpy import sqrt as np_sqrt
from numpy import polynomial as poly
from numpy import errstate as np_errstate
from numpy import true_divide as np_true_divide
from numpy import isfinite as np_isfinite
from scipy import interpolate as inter
from astropy.time import Time

import dw
import dw.core.commands as dwcomm
#import dw.flag.widget as dwwidg
import dw.flag.rfi_dect_func as rfi_dect
import dw.core.prefs as prefs

file_type_default = 'fits'
############################################################################


def dw_version():
    """Return the package version"""
    return dw.__version__

def to2D(array, n_ch):
    """Return a 2D array where each row is the 1D array in input

    array: numpy 1D array
    n_ch: integer number of columns of the output array

    return a 2D numpy array
    """
    array2D = np_zeros((len(array), n_ch))
    for ii in range(len(array)):
        if array[ii] != 0:
            array2D[ii, :] = array[ii]

    return array2D

def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np_errstate(divide='ignore', invalid='ignore'):
        c = np_true_divide( a, b )
        c[ ~ np_isfinite( c )] = 0  # -inf inf NaN
    return c

class DWObs(object):

    """implement observation directory structure and convenient methods to access the files
    *Methods*


    """

    def __init__(self):
        """Initialize the observation structure"""
        self.dir_name = None
        self.files_type = None
        self.dirh = None
        self.fileh = None
        self.dw_io = None
        self.dir_datasets = None
        self.feeds = None
        self.sections = None
        self.polars = None
        self.dssel = [0, 0, 0]
        #self.working_dataset = None

    def open_dir(self, dir_name, files_type=file_type_default):
        """Invoke the dir open command

        dir_name: path to observation directory
        """
        dwcomm.OpenDirCommand(self, dir_name, files_type)

    def list2choices(self, clist):
        choices = []
        for c in enumerate(clist):
            try:
                int(c[1])
                item = (str(c[1]), str(c[1]))
            except:
                item = (str(c[0]), str(c[1]))
            choices.append(item)
        return choices

    def get_median_data(self, ldatasets, section, pol, lrangei, lranges, lexcluded):
        ltable = []
        for i_dataset in ldatasets:
            table = self.dir_datasets[i_dataset].th
            ltable.append(table)
        data_l = self.dw_io.get_median(ltable, section, pol, lrangei, lranges, lexcluded)
        self.dssel = [0, section, pol]
        return data_l

    def get_flag_curve(self, file_name, section):
        flagc = self.dw_io.get_flagc(file_name, section)
        return flagc

    def get_fit(self, fit_type, data, order, smooth, degree, begin, end, weight=None):
        z1 = np_zeros(begin)
        z2 = np_zeros(len(data[0])-end)
        if end == 0:
            end = None
        x = data[0][begin:end]
        y = data[1][begin:end]
        if weight is not None:
            weight = weight[begin:end]
        if fit_type == "spline":
            f = inter.UnivariateSpline(x, y, w=weight, k=order, s=smooth)
        else:
            f = poly.Chebyshev.fit(x, y, degree, w=weight)
        res = y-f(x)
        nfit = f(x)/np_max(f(x))
        corr = concatenate((z1, nfit, z2))
        fitc = [x, f(x), corr, res]
        return fitc

    def fitfile(self, file_name, fit):
        dwcomm.FitFile(self, file_name, fit)

    def applycorr(self, file_name, filelist=None):
        dwcomm.ApplyCorr(self, file_name, filelist)

class DWData(object): # CLIENT class ##########################################

    """implement data structure and convenient methods to access the data

    *Methods*
    * __init__ - inizilize the data structure
    * open_data - invoke the file open command
    * close - Invoke the command to flush data to file and close it
    * new_flagset - Invoke the command to create new flagging set
    * deflag_flagset - Deflag existing dataset
    * get_flagsets - Invoke the command to retrieve flagging sets
    * merge_flagsets - Invoke the command to merge flagsets
    * del_flagset - Invoke the command to delete a flagging set
    * man_flag - invoke the command to set data flagged
    * dataset2np_array - return the selected dataset values
    * polaset2np_array - return the selected polarimeter dataset values (ALPHA)
    * flagset2np_array - return a numpy 2D array containing the selected flagset
    * flagsets2np_array - return a list of numpy 2D array containing the flagsets of the selected dataset
    * get_time_scale - return the selected dataset time scale values
    * get_freq_scale - return the selected dataset channels frequency values
    * get_bandwidth - Return the dataset bandwidth
    * get_ascension - retrieve right ascension data
    * get_azimuth - retrieve azimuth data
    * get_declination - retrieve declination data
    * get_elevation - retrieve elevation data
    * get_source - retrieve source name data
    * get_on_track - retrieve source tracking flag
    * get_ut - return the time scale in UT
    * upd_freq_scale_off - update the starting value of the frequency scale of a dataset (RUDIMENTAL)
    * get_rfi_dect_algorithms - return a dictionary of RFI detection implemented algorithms, description and parameters
    * auto_flag_init - invoke the command to initialize the selected RFI detection algorithm
    * auto_flag_get_params - return the dictionary of the current parameters of the selected RFI detection algorithm
    * auto_flag_upd_params - update the parameters of the selected RFI detection algorithm
    * auto_flag_get_out - return a list of available out options and adictionary containing available output options and whether they are selected or not for the selected RFI detection algorithm
    * auto_flag_compute - Invoke the command to run the selected RFI detection algorithm and write the returned flag matrix in the data file
    """

    def __init__(self):
        """Inizilize the data structure"""
        self.file_name = None # file name
        self.file_type = None # file type
        self.fileh = None # file handle
        self.cfile_name = None # correction file name
        self.cfileh = None # correction file handle
        self.dw_io = None # IO class instance
        self.datasets = [] # Datasets list
        self.dect_alg = self.get_rfi_dect_algorithms()
        self.selected_dect_alg = None
        self.working_dataset = None
        self.correction = False

###############################################################################
###############################################################################
#    def getGroups(self, root_group):
#        command = GetHdfGroupsCommand(self, root_group)
#        Invoker.execute(command, inspect.stack()[1][4][0][0:-1])
#        return command.groups_list
#
#    def getTables(self, group):
#        command = GetHdfTablesCommand(self, group)
#        Invoker.execute(command, inspect.stack()[1][4][0][0:-1])
#        return command.tables_list
# Data file Opening ###########################################################
    def open_data(self, file_name, file_type=file_type_default):
        """Invoke the file open command

        file_name: path to the opening file
        file_type: file format (default: fyle_type_default)
        """
        dwcomm.OpenCommand(self, file_name, file_type)
#        Invoker.execute(command, inspect.stack()[1][4][0][0:-1])
###############################################################################
    def close(self):
        """ Invoke the command to flush data to file and close it
        """

        dwcomm.CloseCommand(self)

    def new_flagset(self, i_dataset, flag_areas = None, feed=None, section=None, pola=None):
        """Invoke the command to create new flagging set

        i_dataset: index of the dataset table
        flag_areas: list of rectangular areas to be set as flagged (ymin, ymax, xmin, xmax)
        """

        dwcomm.NewFlagSetCommand(self, i_dataset, flag_areas, feed, section, pola)
        self.get_flagsets(i_dataset)

    def upd_flagset(self, i_dataset, k_flagset, flag_areas, flag_value = prefs.FLAG_TRUE):
        """Invoke the command to update an existing flagging set

        i_dataset: index of the dataset table
        k_flagset: key of the flagset in the dictionary
        flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        flag_value: flag value to set to
        """
        self.get_flagsets(i_dataset)
        dwcomm.UpdFlagSetCommand(self, i_dataset, k_flagset, flag_areas, flag_value)

    def deflag_flagset(self, i_dataset, k_flagset, flag_areas):
        """Deflag existing dataset

        i_dataset: index of the dataset table
        k_flagset: key of the flagset in the dictionary
        flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        """
        self.upd_flagset(i_dataset, k_flagset, flag_areas, flag_value = prefs.FLAG_FALSE)

    def array_flagset(self, i_dataset, flag_arrays = None):
        """Invoke the command to create new flagging set from an array list

        i_dataset: index of the dataset table
        flag_arrays: list of flag arrays
        """
        dwcomm.ArrayFlagSetCommand(self, i_dataset, flag_arrays)
        self.get_flagsets(i_dataset)

    def get_flagsets(self, i_dataset):
        """Invoke the command to retrieve flagging sets

        i_dataset: index of the dataset table
        """

        dwcomm.GetFlagSetsCommand(self, i_dataset)

    def merge_flagsets(self, i_dataset, k_flagsets):
        """Invoke the command to merge flagsets

        i_dataset: index of the dataset table
        k_flagsets: list of keys of flagging set tables
        """
        dwcomm.MergeFlagSetsCommand(self, i_dataset, k_flagsets)

    def del_flagset(self, i_dataset, k_flagset):
        """Invoke the command to delete a flagging set

        i_dataset: index of the dataset table
        k_flagset:  key of the flagset in the dictionary
        """

        dwcomm.DelFlagSetCommand(self, i_dataset, k_flagset)

    def del_sel_flag(self, i_dataset, rect_area, pola):
        """Invoke the command to remove the flag areas intesected
        by a rectangular area

        i_dataset: index of the dataset table
        rect_area: rectangualar area
        pola: working polarization
        """

        dwcomm.DelSelFlagCommand(self, i_dataset, rect_area, pola)

    def propag_flagtable(self, filelist):
        """Propagate the flag table to other files

        filelist: list of files
        """

        dwcomm.PropagFlag(self, filelist)

    def propag_tofeed(self, i_dataset, k_flagset, feedlist):
        """Propagate a flag to other feeds

        feedlist: list of feeds
        """

        dwcomm.PropagToFeeds(self, i_dataset, k_flagset, feedlist)

###############################################################################
    def dataset2np_array(self, i_dataset):
        """Return a numpy 2D array or a list of numpy 2D arrays containing the selected dataset
        (ALPHA)
        i_dataset: index of the dataset table
        """
        integration = self.dw_io.get_integration(self.datasets[i_dataset].th)
        if self.correction == False:
            data_l = self.dw_io.get_data(self.datasets[i_dataset].th)
        else:
            data_l = self.dw_io.get_cdata(self.datasets[i_dataset].th, self.cfileh)

        if len(data_l) == 1:
            return np_divide(data_l[0].transpose(),integration).transpose()
        else:
            El = np_divide((data_l[0] + 0.001).transpose(),integration).transpose()
            Er = np_divide((data_l[1] + 0.001).transpose(),integration).transpose()
            return [El, Er]

    def polaset2np_array(self, i_dataset):
        """Return a list of numpy 2D array containing the selected dataset

        i_dataset: index of the dataset table
        """
        integration = self.dw_io.get_integration(self.datasets[i_dataset].th)
        if self.correction == False:
            data_l = self.dw_io.get_data(self.datasets[i_dataset].th)
        else:
            data_l = self.dw_io.get_cdata(self.datasets[i_dataset].th, self.cfileh)

        El = np_divide((data_l[0] + 0.001).transpose(),integration).transpose()
        Er = np_divide((data_l[1] + 0.001).transpose(),integration).transpose()
        stk_q = np_divide((data_l[2] + 0.001).transpose(),integration).transpose()
        stk_u = np_divide((data_l[3] + 0.001).transpose(),integration).transpose()
        stk_i = El + Er
        stk_v = El - Er
        stk_phi = 0.5 * np_arctan( div0(stk_u, stk_q) )
        stk_p   = stk_u * stk_u + stk_q*stk_q + stk_v*stk_v
        stk_p   = np_sqrt( stk_p )
        stk_p   = div0(stk_p, stk_i)
        stk_p[stk_p>=100] = 0.0
        #stk_p   = np_array([ 0.0 if x >= 100 else x for x in stk_p ])

        return [El, Er, stk_q, stk_u] #, stk_i, stk_v, stk_phi, stk_p]

    def flagset2np_array(self, i_dataset, k_flagset):
        """Return a numpy 2D array containing the selected flagset

        i_dataset: index of the dataset table
        k_flagset:  key of the flagset in the dictionary
        """
        return self.dw_io.get_data(self.datasets[i_dataset].flagsets[k_flagset])

    def flagsets2np_array(self, i_dataset):
        """Return a list of numpy 2D array containing the flagsets of the
        selected dataset

        i_dataset: index of the dataset table
        """
        flagsets = {}
        keys = self.datasets[i_dataset].flagsets.keys()
        for key in keys:
            flagsets[key] = self.flagset2np_array(i_dataset, key)

        return flagsets

    def open_correction_file(self, file_name):
        """Invoke the command to open the correction file

        file_name: path to the opening file
        """
        dwcomm.OpenCorrection(self, file_name)

    def toggle_correction(self):
        """Invoke the command to toggle the data correction

        """
        dwcomm.ToggleCorrection(self)

    def get_time_scale(self, i_dataset):
        """Return a numpy 1D array containing the time values of the selected
           dataset samples

        i_dataset: index of the dataset table
        """
        return self.datasets[i_dataset].time_scale

    def get_freq_scale(self, i_dataset):
        """Return a numpy array containing the frequency values of the
           selected dataset channels

        i_dataset: index of the dataset table
        """
        return self.datasets[i_dataset].freq_scale

    def get_bandwidth(self, i_dataset):
        """Return the dataset bandwidth

        i_dataset: index of the dataset table
        """
        return self.datasets[i_dataset].bandwidth

    def get_ascension(self, i_dataset):
        """Return the 'per sample' dataset right ascension

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_ascension(self.datasets[i_dataset].th)

    def get_azimuth(self, i_dataset):
        """Return the 'per sample' dataset azimuth

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_azimuth(self.datasets[i_dataset].th)

    def get_declination(self, i_dataset):
        """Return the 'per sample' dataset declination

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_declination(self.datasets[i_dataset].th)

    def get_elevation(self, i_dataset):
        """Return the 'per sample' dataset elevation

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_elevation(self.datasets[i_dataset].th)

    def get_source(self, i_dataset):
        """Return the 'per sample' dataset source name

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_source(self.datasets[i_dataset].th)

    def get_on_track(self, i_dataset):
        """Return the 'per sample' dataset source tracking flag

        i_dataset: index of the dataset table
        """
        return self.dw_io.get_on_track(self.datasets[i_dataset].th)

    def get_ut(self, i_dataset):
        """Return the time scale in UT

        i_dataset: index of the dataset table
        """
        ut_string = []
        epoch_time = self.dw_io.get_epoch_time_scale(self.datasets[i_dataset].th)
        for time in epoch_time:
            ut_time = Time(time, format='mjd')
            ut_string.append(ut_time.iso)
        return ut_string

    def get_flagset_meta(self, i_dataset, k_flagset):
        """Return a dict containg flag set metadata

        i_dataset: index of the dataset table
        k_flagset:  key of the flagset in the dictionary
        """

        meta_dict = {}
        for meta in ['algorithm','params','flagresult']:
            try:
                meta_dict[meta] = self.dw_io.get_table_meta(self.datasets[i_dataset].flagsets[k_flagset],
                                                            meta)
            except AttributeError:
                meta_dict[meta] = ""

        return meta_dict

    def upd_freq_scale_off(self, i_dataset, zero_value):
        """Update the starting value of the frequency scale of a dataset
        (RUDIMENTAL)
        i_dataset: index of the dataset table
        zero_value: offset
        """
        self.datasets[i_dataset].freq_scale = np_linspace(zero_value,
                                            zero_value+self.datasets[i_dataset].bandwidth,
                                            self.datasets[i_dataset].n_channels+1)

    def get_rfi_dect_algorithms(self):
        """Return a dictionary of RFI detection implemented algorithms, description
           and parameters
        """
        implement_dict = {}

        implement_list = rfi_dect.FlagAlgorithm.get_implementations()
        for implementation in implement_list:
            arg_dict = implementation.get_def_params()

            implement_dict[implementation] = {'name': implementation.name,
                                              'description': implementation.description,
                                              'params': arg_dict
                                             }

        return implement_dict

    def auto_flag_init(self, i_dataset, dect_algorithm, **usr_param):
        """Invoke the command to initialize the selected RFI detection algorithm

        i_dataset: index of the dataset table
        dect_algorithm: RFI detection algorithm class reference
        usr_param: selected algorithm dict parameters
        """
        dwcomm.AutoFlagInitCommand(self, i_dataset, dect_algorithm, **usr_param)

    def auto_flag_get_params(self):
        """Return the dictionary of the current parameters of the
        selected RFI detection algorithm
        """
        return self.selected_dect_alg.get_params()

    def auto_flag_upd_params(self, **par_dict):
        """Update the parameters of the selected RFI detection algorithm
        """
        self.selected_dect_alg.upd_params_values(**par_dict)

    def auto_flag_get_out(self):
        """Return a list of available out options and adictionary containing
        available output options and whether
        they are selected or not for the selected RFI detection algorithm
        """
        out_avail = self.selected_dect_alg.get_avail_output()
        out_options = {}
        for out in out_avail:
            out_options[out] = self.selected_dect_alg.is_out_selected(out)

        return out_avail, out_options

    def auto_flag_compute(self, out_labels = None, save = True):
        """Invoke the command to run the selected RFI detection algorithm and
           write the returned flag matrix in the data file

           out_labels: list of ouput labels
        """
        dwcomm.AutoFlagComputeCommand(self, out_labels, save)
        if save == False:
            return self.working_dataset, self.last_flag_list

    def auto_flag_save(self, i_dataset, flag_arrays):

        dwcomm.ArrayFlagSetCommand(self, i_dataset, flag_arrays)
