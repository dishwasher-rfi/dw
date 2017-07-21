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
dw.core.commands
================

Implement commands to be executed on the data structure

Functions
---------
* integration_to_seconds - Convert the integration time of each data sample to
  seconds from the beginning of dataset and return it

Classes
-------
* Command: commands intreface class
* OpenCommand: data file opening
* CloseCommand: Flush changes in the data file and close it
* NewFlagSetCommand: Create a new flagging set
* UpdFlagSetCommand: Update data in a flagging set
* GetFlagSetsCommand: Get flagging sets handles
* DelFlagSetCommand: Delete a flagging set
* MergeFlagSetsCommand: Merge two or more flagging sets
* ArrayFlagSetCommand: Create a new flagging set from a 2D flag matrix
* AutoFlagInitCommand: Init RFI detection algorithm
* AutoFlagComputeCommand: Flag data using the selected algorithm
"""

import inspect
from functools import reduce
from operator import add
from numpy import round as np_round
from numpy import cumsum as np_cumsum
from numpy import insert as np_insert
from numpy import linspace as np_linspace

import dw.core.io as dwio
import dw.core.dw_logging as dw_logging
import dw.core.prefs as prefs


def integration_to_seconds(integration, filetype):
    """Return a 1D numpy array of seconds from the beginning of the dataset
       using the integration time of each dataset sample

    integration: numpy 1D array of data integration values
    """
    if filetype == "fits":
        return np_round(integration/1000, 3)
    else:
        clock = 1.0 / 200000000
        return np_round(integration * clock * 1024, 3)


class Command(object):# COMMAND interface #####################################

    """Command interface class

    *Methods*
    * __init__
    * _execute: log the command and execute it
    * execute: to be overridden in command implementation
    """

    def __init__(self):
        try:
          self.is_undoable
        except AttributeError:
          self.is_undoable = True

        try:
          self.is_loggable
        except AttributeError:
          self.is_loggable = True

        try:
          self.is_flag
        except AttributeError:
          self.is_flag = False

        self._execute()

    def _execute(self):
        """ Log the command and execute it
        """
        if self.is_loggable:
          # Logs the function call
          dw_logging.fun_call_logger.info(inspect.stack()[1][4][0][0:-1])
          # Logs the command and its arguments dict
          dw_logging.command_log.info(type(self).__name__+"\t"+str(self.__dict__))
        if self.is_flag:
            pass
        self.execute()

    def execute(self):
        raise NotImplemented
###############################################################################


class OpenCommand(Command):

    """Open a data file

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, file_name, file_type):
        """
        dw_data: dw.core.data_def instance
        file_name: path to data file
        file_type: file format
        """

        self.is_undoable = False
        self.file_name = file_name
        self.file_type = file_type
        self.data = dw_data
        self.data.file_name = file_name
        self.data.file_type = file_type
        super(OpenCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        if self.file_type == 'hdf':
            self.data.dw_io=dwio.HdfIO()
        elif self.file_type == 'hdf_pola':
            self.data.dw_io=dwio.HdfPolaIO()
        elif self.file_type == 'fits':
            self.data.dw_io=dwio.FitsIO()
        else:
            raise NotImplemented
        self.data.fileh = self.data.dw_io.data_open(self.file_name)
        try:
            self.data.data_type_dict = self.data.dw_io.check_data_type(self.data.fileh)
        except:
            pass
        self.data.datasets = self.data.dw_io.get_datasets(self.data.fileh)

        for i_dataset in xrange(len(self.data.datasets)):
            time = integration_to_seconds(np_cumsum(
                    self.data.dw_io.get_integration(self.data.datasets[i_dataset].th)),
                    self.file_type)
            self.data.datasets[i_dataset].time_scale = np_insert(time, 0, 0)

            self.data.datasets[i_dataset].local_osc = self.data.dw_io.get_first_osc(self.data.datasets[i_dataset].th)
            self.data.datasets[i_dataset].frequency = self.data.dw_io.get_frequency(self.data.datasets[i_dataset].th)

            self.data.datasets[i_dataset].freq_scale = np_linspace(self.data.datasets[i_dataset].frequency,
                                            self.data.datasets[i_dataset].frequency+self.data.datasets[i_dataset].bandwidth,
                                            self.data.datasets[i_dataset].n_channels+1)
            self.data.datasets[i_dataset].feed_section = self.data.dw_io.get_feed_section(self.data.fileh, self.data.datasets[i_dataset].th)
            try:
                self.data.datasets[i_dataset].t = "Feed"+str(self.data.datasets[i_dataset].feed_section[0])+" - Section"+str(self.data.datasets[i_dataset].feed_section[1])
            except:
                pass
            self.data.datasets[i_dataset].flagsets = {}


class OpenDirCommand(Command):

    def __init__(self, bc_data, dir_name, files_type):

        self.is_undoable = False
        self.dir_name = dir_name
        self.files_type = files_type
        self.data = bc_data
        self.data.dir_name = dir_name
        self.data.files_type = files_type
        super(OpenDirCommand, self).__init__()

    def execute(self):

        if self.files_type == 'hdf':
            self.data.dw_io = dwio.HdfIO()
        elif self.files_type == 'hdf_pola':
            self.data.dw_io = dwio.HdfPolaIO()
        elif self.files_type == 'fits':
            self.data.dw_io = dwio.FitsIO()
        else:
            raise NotImplemented
        self.data.dirh = self.data.dw_io.dir_tree(self.dir_name)
        self.data.flist = self.data.dw_io.filelist(self.data.dirh)
        self.data.dir_datasets = self.data.dw_io.get_fdatasets(self.data.flist)
        self.data.sections = self.data.dw_io.get_sections(self.data.dir_datasets[0].th[0])
        self.data.polars = self.data.dw_io.get_polars(self.data.dir_datasets[0].th)

        for i_dataset in xrange(len(self.data.dir_datasets)):
            self.data.dir_datasets[i_dataset].title = "Scan"+str(self.data.dw_io.get_scanid(self.data.dir_datasets[i_dataset].th))+".Subscan"+str(self.data.dw_io.get_subscanid(self.data.dir_datasets[i_dataset].th))
            self.data.dir_datasets[i_dataset].selected = True

class FitFile(Command):

    def __init__(self, data, file_name, fit):
        self.is_undoable = False
        self.file_name = file_name
        self.data = data
        self.data.dw_io = data.dw_io
        self.fit = fit
        super(FitFile, self).__init__()

    def execute(self):
        try:
            self.data.dw_io.new_fit_file(self.data, self.file_name, self.fit)
        except:
            self.data.dw_io.upd_fit_file(self.data, self.file_name, self.fit)

class ApplyCorr(Command):
    def __init__(self, data, file_name, filelist):
        self.file_name = file_name
        self.filelist = filelist
        self.data = data
        self.data.dw_io = data.dw_io
        super(ApplyCorr, self).__init__()

    def execute(self):
        self.data.dw_io.applycorr(self.data, self.file_name, self.filelist)

class OpenCorrection(Command):
    def __init__(self, data, file_name):
        self.data = data
        self.file_name = file_name
        super(OpenCorrection, self).__init__()

    def execute(self):
        self.data.dw_io.opencorr(self.data, self.file_name)

class ToggleCorrection(Command):
    def __init__(self, data):
        self.data = data
        super(ToggleCorrection, self).__init__()

    def execute(self):
        try:
            self.data.cfileh
        except:
            raise IOError('No correction loaded! Open a correction file!')

        if self.data.correction == False:
            self.data.correction = True
        else:
            self.data.correction = False

class PropagFlag(Command):
    def __init__(self, data, filelist):
        self.data = data
        self.file_name = self.data.fileh
        self.filelist = filelist
        super(PropagFlag, self).__init__()

    def execute(self):
        self.data.dw_io.propag_flag_table(self.file_name, self.filelist)

class PropagToFeeds(Command):
    def __init__(self, dw_data, i_dataset, k_flagset, feedlist):
        self.data = dw_data
        self.fileh = self.data.fileh
        self.i_dataset = i_dataset
        self.k_flagset = k_flagset
        self.feedlist = feedlist
        super(PropagToFeeds, self).__init__()

    def execute(self):
        nop = self.data.datasets[self.i_dataset].flagsets[self.k_flagset][2]
        for feed in self.feedlist:
            self.data.dw_io.propag_to_feed(self.fileh, nop, feed)

class CloseCommand(Command):

    """Flush changes in the data file and close it

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data):
        """
        dw_data: dw.core.data_def instance
        """

        self.data = dw_data
        super(CloseCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        self.data.dw_io.close(self.data.fileh)

class NewFlagSetCommand(Command):

    """Create a new flagging set

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, flag_areas = None, feed=None, section=None, pola=None, add_to_dict = True):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        add_to_dict: if True add the flagset handle to the data structure
        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.flag_areas = flag_areas
        self.feed = feed
        self.section = section
        self.pola = pola
        super(NewFlagSetCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        (key, flagh) = self.data.dw_io.new_flagset(self.data.fileh,
                                    self.data.datasets[self.i_dataset].th,
                                    self.data.datasets[self.i_dataset].n_samples,
                                    self.data.datasets[self.i_dataset].n_channels,
                                    self.flag_areas, self.feed, self.section,
                                    self.pola)

        self.data.datasets[self.i_dataset].flagsets[key] = flagh

class UpdFlagSetCommand(Command):

    """Update data in a flagging set

    *Methods*
    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, k_flagset, flag_areas, flag_value = prefs.FLAG_TRUE):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        k_flagset:  key of the flagset in the dictionary
        flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        flag_value: flag value to set to
        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.k_flagset = k_flagset
        self.flag_areas = flag_areas
        self.flag_value = flag_value
        super(UpdFlagSetCommand, self).__init__()

    def execute(self):
        """Execute the command"""
        self.data.dw_io.upd_flagset(self.data.datasets[self.i_dataset].flagsets[self.k_flagset],
                                    self.data.datasets[self.i_dataset].n_samples,
                                    self.data.datasets[self.i_dataset].n_channels,
                                    self.flag_areas,
                                    self.flag_value)

class GetFlagSetsCommand(Command):

    """Get flagging sets handles

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        """

        self.data = dw_data
        self.i_dataset = i_dataset
        super(GetFlagSetsCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        self.data.datasets[self.i_dataset].flagsets = self.data.dw_io.get_flagsets(
                self.data.fileh, self.data.datasets[self.i_dataset].th)[0]
        self.data.datasets[self.i_dataset].flagsets_rif = self.data.dw_io.get_flagsets(
            self.data.fileh, self.data.datasets[self.i_dataset].th)[1]
        #print self.data.datasets[self.i_dataset].flagsets

class DelFlagSetCommand(Command):

    """Delete a flagging set

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, k_flagset):
        """
        dw_data: dw.core.data_def instance

        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.k_flagset = k_flagset
        super(DelFlagSetCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        self.data.dw_io.del_table(self.data.fileh,
                self.data.datasets[self.i_dataset].flagsets[self.k_flagset])

class DelSelFlagCommand(Command):
    """Delete Flags intesected by rectangular area

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, rect_area, pola):
        """
        dw_data: dw.core.data_def instance

        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.rect_area = rect_area
        self.pola = pola
        super(DelSelFlagCommand, self).__init__()

    def execute(self):
        """Execute the command"""

        self.data.dw_io.del_sel_flags(self.data.fileh,
                                      self.data.datasets[self.i_dataset].feed_section[0],
                                      self.data.datasets[self.i_dataset].feed_section[1],
                                      self.pola, self.rect_area)

class MergeFlagSetsCommand(Command):

    """Merge two ore more flagging sets

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, k_flagsets):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        k_flagsets: list of indexes of flagsets to merge
        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.k_flagsets = k_flagsets
        super(MergeFlagSetsCommand, self).__init__()


    def execute(self):
        """Execute the command"""

        #Retrieve data
        flag_data = []
        for k_flagset in self.k_flagsets:
            flag_data.append(self.data.dw_io.get_data(
                self.data.datasets[self.i_dataset].flagsets[k_flagset]))

        #Merge data
        new_flag = reduce(add, flag_data)
        new_flag = (new_flag>0).astype(int)

        #Delete old flag data tables
        for k_flagset in self.k_flagsets:
            self.data.dw_io.del_table(self.data.fileh,
                self.data.datasets[self.i_dataset].flagsets[k_flagset])

        #Write new flag table
        self.data.dw_io.new_flagset_from_array(
                                    self.data.fileh,
                                    self.data.datasets[self.i_dataset].th,
                                    self.data.datasets[self.i_dataset].n_samples,
                                    self.data.datasets[self.i_dataset].n_channels,
                                    new_flag)

class ArrayFlagSetCommand(Command):

    """Create a new flagging set from a 2D flag matrix

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, flag_arrays):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        flag_arrays: list of flagging arrays
        """

        self.data = dw_data
        self.i_dataset = i_dataset
        self.flag_arrays = flag_arrays
        super(ArrayFlagSetCommand, self).__init__()


    def execute(self):
        """Execute the command"""

        for flag_array in self.flag_arrays:
            self.data.dw_io.new_flagset_from_array(self.data.fileh,
                                                   self.data.datasets[self.i_dataset].th,
                                                   self.data.datasets[self.i_dataset].n_samples,
                                                   self.data.datasets[self.i_dataset].n_channels,
                                                   flag_array.flag_data,
                                                   flag_array.feed,
                                                   flag_array.section,
                                                   flag_array.pola,
                                                   name_prefix = flag_array.algorithm,
                                                   algorithm = flag_array.algorithm,
                                                   params = flag_array.params,
                                                   flagresult = flag_array.flagresult)

###############################################################################
class AutoFlagInitCommand(Command):

    """Init RFI detection algorithm

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, i_dataset, algorithm, **args_dict):
        """
        dw_data: dw.core.data_def instance
        i_dataset: index of the dataset table
        algorithm: RFI detection algorithm class reference
        args_dict: dictionary of selected algorithm's parameters
        """

        self.is_flag = True
        self.data = dw_data
        self.i_dataset = i_dataset
        self.algorithm = algorithm
        self.args_dict = args_dict
        super(AutoFlagInitCommand, self).__init__()

    def execute(self):
        """Execute the command"""
        if self.data.correction == False:
            data_matrix = self.data.dw_io.get_data(self.data.datasets[self.i_dataset].th)
        else:
            data_matrix = self.data.dw_io.get_cdata(self.data.datasets[self.i_dataset].th, self.data.cfileh)
        self.data.selected_dect_alg = self.algorithm(data_matrix, **self.args_dict)
        self.data.working_dataset = self.i_dataset

class AutoFlagComputeCommand(Command):

    """Flag data using the selected algorithm

    *Methods*
    * __init__
    * execute: execute the command
    """

    def __init__(self, dw_data, out_labels = None, save = True):
        """
        dw_data: dw.core.data_def instance
        out_labels: list of ouput labels
        """

        self.is_flag = True
        self.data = dw_data
        self.out_labels = out_labels
        self.save = save
        self.data.last_flag_list = None
        super(AutoFlagComputeCommand, self).__init__()

    def execute(self):
        """Execute the command"""
        if self.out_labels:
            self.data.selected_dect_alg.set_output(self.out_labels)
        flag_list = self.data.selected_dect_alg.compute().values()
        for flag in flag_list:
            flag.feed = self.data.datasets[self.data.working_dataset].feed_section[0]
            flag.section = self.data.datasets[self.data.working_dataset].feed_section[1]
        if self.save == True:
            ArrayFlagSetCommand(self.data, self.data.working_dataset, flag_list)
        else:
            self.data.last_flag_list = flag_list
###############################################################################
