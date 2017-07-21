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
dw.core.io
==========

Implement data I/O for different file formats

Classes
-------
* DwDataSet - Define a data structure for dataset tables
* DWIO - I/O interface class
* HdfIO - hdf5 format I/O
* FitsIO - fits format I/O
"""

import tables
#import astropy # For future developement of FitsIO
from astropy.io import fits
from numpy import round as np_round
from os import walk
import numpy as np
#from numpy import divide as np_divide
#from numpy import log10 as np_log10

import dw.core.prefs as prefs

def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c

class DwDataSet(object):

    """Define a data structure for dataset tables"""

    def __init__(self):
        self.th = None
        self.n_channels = 0
        self.n_samples = 0
        self.bandwidth = 0


class DWIO(object):

    """I/O interface class

    *Methods*
    * data_open - open the data file
    * close - Flush changes to the data file and close it
    * get_datasets - retrieve dataset tables handles
    * get_data - retrieve data
    * _get_meta - return metadata
    * get_integration - retrieve integration data
    * get_ascension - retrieve right ascension data
    * get_azimuth - retrieve azimuth data
    * get_declination - retrieve declination data
    * get_elevation - retrieve elevation data
    * get_source - retrieve source name data
    * get_on_track - retrieve source tracking flag
    * get_epoch_time_scale - retrieve seconds since the epoch
    * get_first_osc - retrieve the value of the oscillator at time 0
    * setup_new_flagset - create a new empty table in the HDF file, in the group of tableh, containing flagging data. Return the flagging table handler.
    * new_flagset - create a new table in the HDF file, in the group of data_table, containing flagging data
    * new_flagset_from_array - create a new table in the HDF file, in the group of tableh, containing flagging data. Return the flagging table handler
    * upd_flagset - update an existing flagging set
    * get_flagsets - retrieve flagging tables handels
    * get_table_meta - return table metadata
    * del_table - Delete a table from a HDF file
    * upd_columns - modify columns data

    ALL methods (except get_implementations) to be OVERRIDDEN in actual implementation
    """

    @classmethod
    def get_implementations(cls):
        """Retrieve I/O implementations
        """
        return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in s.get_implementations()]

    def data_open(self, file_name):
        """Open the data file

        file_format: path to data file
        """
        pass

    def close(self, fileh):
        """Flush changes to the data file and close it

        fileh: file handle
        """
        pass

    def get_datasets(self, fileh):
        """Retrieve dataset tables handles

        fileh: file handle
        """
        pass

    def get_data(self, table):
        """Retrieve data

        table: Table reference
        """
        pass

    def _get_meta(self, table, column):
        """Return a 1D numpy array containig the metadata in column

        table: Table reference
        column: a table column
        """
        pass

    def get_integration(self, table):
        """Return a 1D numpy array containig the integration time for each
           dataset sample

        table: Table reference
        """
        pass

    def get_ascension(self, table):
        """Return a 1D numpy array containig the right ascension value for each
           dataset sample

        table: Table reference
        """
        pass

    def get_azimuth(self, table):
        """Return a 1D numpy array containig the azimuth value for each
           dataset sample

        table: Table reference
        """
        pass

    def get_declination(self, table):
        """Return a 1D numpy array containig the declination value for each
           dataset sample

        table: Table reference
        """
        pass

    def get_elevation(self, table):
        """Return a 1D numpy array containig the elevation value for each
           dataset sample

        table: Table reference
        """
        pass

    def get_source(self, table):
        """Return a 1D numpy array containig the source name for each
           dataset sample

        table: Table reference
        """
        pass

    def get_on_track(self, table):
        """Return a 1D numpy array containig souerce tracking flag for each
           dataset sample

        table: Table reference
        """
        pass

    def get_epoch_time_scale(self, table):
        """Return a 1D numpy array of seconds since the epoch

        table: Table reference
        """
        pass

    def get_first_osc(self, table):
        """Retrieve the value of the oscillator at time 0
        (used to determine the starting value of the frequency scale)

        table: Table reference
        """

        pass

    def new_flagset(self, fileh, tableh, rows, columns, flag_areas = None,
                    feed = None, section = None, pola = None):
        """Create a new table, related to data_table, containing flagging data

           fileh: file handler
           tableh: reference to a data table
           rows: number of rows of the new flag table
           columns: number of channels
           flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        """

        pass

    def new_flagset_from_array(self, fileh, tableh, rows, columns, flag_array,
                               feed = None, section = None, pola = None,
                               name_prefix = 'Flag',
                               title = 'Flagging matrix',
                               algorithm = None,
                               params = None,
                               flagresult = None):

        """Create a new table in the HDF file, in the group of tableh,
           containing flagging data. Return the flagging table handler.

           fileh: pytables file handler
           tableh: reference to a HDF data table
           rows: number of rows of the new flag table
           columns: number of channels
           flag_array: numpy array
           name_prefix: string to use as table name prefix
           title: string to use as table title
        """

        pass

    def upd_flagset(self, flagh, rows, columns, flag_areas, flag_value = prefs.FLAG_TRUE):
        """Update values in an existing flagging set.

           flagh: reference to a HDF data table
           rows: number of rows of the flag table
           columns: number of channels
           flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
           flag_value: flag value to set to
        """
        pass

    def get_flagsets(self, fileh, tableh):
        """
           fileh: pytables file handler
           tableh: reference to a HDF data table
        """

        pass

    def get_table_meta(self, tableh, meta_label):
        """Return table metadata

           tableh: reference to a HDF data table
           meta_label: metadata name (string)
        """

        pass

    def del_table(self, fileh, tableh):
        """delete a table from a HDF file

           fileh: pytables file handler
           tableh: reference to a HDF data table
        """

        pass

    def upd_columns(self, fileh, tableh,
                    start=None, stop=None, step=None, columns=None, names=None):
        """Modify a series of columns in the row slice [start:stop:step]
        """
        pass


class HdfIO(DWIO):

    """Hdf5 file format I/O

    *Methods*
    * data_open - open the data file
    * close - Flush changes to the data file and close it
    * get_datasets - retrieve dataset tables handles
    * get_data - retrieve data
    * _get_meta - return metadata
    * get_integration - retrieve integration data
    * get_ascension - retrieve right ascension data
    * get_azimuth - retrieve azimuth data
    * get_declination - retrieve declination data
    * get_elevation - retrieve elevation data
    * get_source - retrieve source name data
    * get_on_track - retrieve source tracking flag
    * get_epoch_time_scale - retrieve seconds since the epoch
    * get_first_osc - retrieve the value of the oscillator at time 0
    * setup_new_flagset - create a new empty table in the HDF file, in the group of tableh, containing flagging data. Return the flagging table handler.
    * new_flagset - create a new table in the HDF file, in the group of data_table, containing flagging data
    * new_flagset_from_array - create a new table in the HDF file, in the group of tableh, containing flagging data. Return the flagging table handler
    * upd_flagset - update an existing flagging set
    * get_flagsets - retrieve flagging tables handels
    * get_table_meta - return table metadata
    * del_table - Delete a table from a HDF file
    * upd_columns - modify columns data
    """

    def data_open(self, file_name):
        """Return a PyTables file handle

        file_format: path to data file
        """

    # Open a file in "r+" mode (necessary to add flagging)
        fileh = tables.open_file(file_name, mode = "r+")
        return fileh

    def close(self, fileh):
        """Flush changes to the data file and close it

        fileh: PyTables file handler
        """

        fileh.flush()
        fileh.close()


    def get_datasets(self, fileh):
        """Return a list of dataset(s) tables

        fileh: PyTables file handle
        """

        datasets_list = []
        for group in fileh.walk_groups("/"):
            for a in fileh.list_nodes(group, "Table"):
                if a._v_name == "Data":
                    dataset = DwDataSet()
                    dataset.th = a
                    dataset.t = a.name
                    dataset.n_channels = a.description.channels.shape[0]
                    dataset.bandwidth = float(group._f_getattr("Bandwith"))
                    dataset.n_samples = a.shape[0]
                    dataset.time_scale = None
                    dataset.freq_scale = None
                    datasets_list.append(dataset)
        return datasets_list

    def get_data(self, table):
        """Return a 2D numpy array containig the dataset (as float)

        table: Table reference
        """
        if table.name == 'Data':
            dat = []
            dat.append(table.col('channels').astype(float))
            return dat
        elif table.name.startswith("Flag"):
            return table.col('channels').astype(float)
#        integration = self.get_integration(table)
#
#        return np_divide(data.transpose(),integration).transpose()

    def _get_meta(self, table, column):
        """Return a 1D numpy array containig the metadata in column

        table: Table reference
        column: a table column
        """
        ret = 0
        try:
            ret = table.col(column).astype(float)
        except :
            pass

        return ret

    def get_integration(self, table): #TODO: read time info from table
        """Return a 1D numpy array containig the integration time for each
           dataset sample

        table: Table reference
        """
#        return table.col('integration').astype(float)
        return self._get_meta(table, 'integration')

    def get_ascension(self, table):
        """Return a 1D numpy array containig the right ascension value for each
           dataset sample

        table: Table reference
        """
#        return table.col('asc').astype(float)
        return self._get_meta(table, 'asc')

    def get_azimuth(self, table):
        """Return a 1D numpy array containig the azimuth value for each
           dataset sample

        table: Table reference
        """
#        return table.col('azim').astype(float)
        return self._get_meta(table, 'azim')

    def get_declination(self, table):
        """Return a 1D numpy array containig the declination value for each
           dataset sample

        table: Table reference
        """
#        return table.col('decl').astype(float)
        return self._get_meta(table, 'decl')

    def get_elevation(self, table):
        """Return a 1D numpy array containig the elevation value for each
           dataset sample

        table: Table reference
        """
#        return table.col('elev').astype(float)
        return self._get_meta(table, 'elev')

    def get_source(self, table):
        """Return a 1D numpy array containig the source name for each
           dataset sample

        table: Table reference
        """
        ret = 0
        try:
            return table.col('name')
        except:
            pass

        return ret


    def get_on_track(self, table):
        """Return a 1D numpy array containig souerce tracking flag for each
           dataset sample

        table: Table reference
        """
#        return table.col('track').astype(float)
        return self._get_meta(table, 'track')

    def get_epoch_time_scale(self, table):
        """Return a 1D numpy array of seconds since the epoch

        table: Table reference
        """
        time = table.col('time').astype(float)
        subtime = table.col('subtime').astype(float)

        return np_round(time+subtime*prefs.CLOCK, 3)

    def get_first_osc(self, table):
        """Retrieve the value of the oscillator at time 0
        (used to determine the starting value of the frequency scale)

        table: Table reference
        """
        ret = 0
        try:
            ret = table.col('local_osc')[0]
        except:
            pass

        return ret

    def setup_new_flagset(self, fileh, tableh, rows, columns,
                          name_prefix = 'Flag',
                          title = 'Flagging matrix',
                          algorithm = None,
                          params = None,
                          flagresult = None):
        """Create a new empty table in the HDF file, in the group of tableh,
           containing flagging data. Return the flagging table handler.

           fileh: pytables file handler
           tableh: reference to a HDF data table
           rows: number of rows of the new flag table
           columns: number of channels
           name_prefix: string to use as table name prefix
           title: string to use as table title
           algorithm: flagging algorithm name (string)
           params: dict of flagging parameters
           flagresult: identifier of flagging set (string)

        Classes
        -------
        * HdfFlagTable - pytables flagging table
        """

        class HdfFlagTable(tables.IsDescription):

            """Define the flagging table structure for pytables"""

            channels = tables.Int8Col(columns)



        comp_filt = tables.Filters(complevel=prefs.HDF_COMP_LEV,
                                   complib=prefs.HDF_COMP_LIB,
                                   shuffle=prefs.HDF_SHUFFLE)
        group = tableh._v_parent
        try:
            subgroup = fileh.create_group(group, 'Flag', "Flagging matrices")
        except:
            for subgroup in fileh.list_nodes(group,"Group"):
                if subgroup._v_name == "Flag":
#                    print subgroup._v_name
                    break

        flagh = None
        n = 0
        while flagh is None:
            try:
                flagh = fileh.create_table(subgroup,
                                           name_prefix+str(n),
                                           HdfFlagTable,
                                           title,
                                           expectedrows=rows, #TODO: verify if it is good for compression
                                           filters=comp_filt)
            except:
                n = n+1

        if algorithm:
            flagh.attrs.algorithm = algorithm

        if algorithm:
            flagh.attrs.params = params

        if algorithm:
            flagh.attrs.flagresult = flagresult

        return flagh

    def new_flagset(self, fileh, tableh, rows, columns,
                    flag_areas = None, feed = None,
                    section = None, pola = None,
                    name_prefix = 'Flag',
                    title = 'Flagging matrix',
                    algorithm = None,
                    params = None,
                    flagresult = None):
        """Create a new table in the HDF file, in the group of tableh,
           containing flagging data. Return the flagging table handler.

           fileh: pytables file handler
           tableh: reference to a HDF data table
           rows: number of rows of the new flag table
           columns: number of channels
           flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
           name_prefix: string to use as table name prefix
           title: string to use as table title
           algorithm: flagging algorithm name (string)
           params: dict of flagging parameters
           flagresult: identifier of flagging set (string)

        """

        flagh=self.setup_new_flagset(fileh, tableh, rows, columns, name_prefix, title, algorithm, params, flagresult)

        rowh = flagh.row
        if not flag_areas:
            for ii in xrange(rows):
                rowh['channels'] = prefs.FLAG_FALSE
                rowh.append()
        else:
            for ii in xrange(rows):
                row_values = [prefs.FLAG_FALSE] * columns
                for jj in xrange(len(flag_areas)):
                    if (flag_areas[jj][0] <= ii) and (ii < flag_areas[jj][1]):
                        for xx in xrange(int(flag_areas[jj][2]),int(flag_areas[jj][3])):
                            row_values[xx] =  prefs.FLAG_TRUE
                rowh['channels'] = row_values
                rowh.append()

        flagh.flush()

        return (flagh.name, flagh)

    def new_flagset_from_array(self, fileh, tableh, rows, columns, flag_array,
                               feed = None, section = None, pola = None,
                               name_prefix = 'Flag',
                               title = 'Flagging matrix',
                               algorithm = None,
                               params = None,
                               flagresult = None):

        """Create a new table in the HDF file, in the group of tableh,
           containing flagging data. Return the flagging table handler.

           fileh: pytables file handler
           tableh: reference to a HDF data table
           rows: number of rows of the new flag table
           columns: number of channels
           flag_array: numpy array
           name_prefix: string to use as table name prefix
           title: string to use as table title
        """

        flagh=self.setup_new_flagset(fileh, tableh, rows, columns, name_prefix, title, algorithm, params, flagresult)

        rowh = flagh.row
        for ii in xrange(rows):
            rowh['channels'] = flag_array[ii,]
            rowh.append()

        flagh.flush()

        return flagh

    def upd_flagset(self, flagh, rows, columns, flag_areas, flag_value = prefs.FLAG_TRUE):
        """Update values in an existing flagging set.

           flagh: reference to a HDF data table
           rows: number of rows of the flag table
           columns: number of channels
           flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
           flag_value: flag value to set to
        """

        x_mins = []
        x_maxs = []
        for jj in xrange(len(flag_areas)):
            x_mins.append(flag_areas[jj][0])
            x_maxs.append(flag_areas[jj][1])

        row_start = min(x_mins)
        row_stop = max(x_maxs)
        row_index = row_start

        for rowh in flagh.iterrows(start = row_start, stop = row_stop):
            row_values = rowh['channels']
            for jj in xrange(len(flag_areas)):
                if (flag_areas[jj][0] <= row_index) and (row_index < flag_areas[jj][1]):
                    for xx in xrange(flag_areas[jj][2],flag_areas[jj][3]):
                        row_values[xx] =  flag_value
            rowh['channels'] = row_values
            rowh.update()

        flagh.flush()


    def get_flagsets(self, fileh, tableh):
        """Return a list of handles to flagging tables

           fileh: pytables file handler
           tableh: reference to a HDF data table
        """

        group = tableh._v_parent
        flagsets_dict = {}
        for a in fileh.list_nodes(group.Flag, "Table"):
#            flagsets_list.append(a)
            flagsets_dict[a.name] = a

        return flagsets_dict

    def get_table_meta(self, tableh, meta_label):
        """Return table metadata

           tableh: reference to a HDF data table
           meta_label: metadata name (string)
        """

        return tableh._f_getattr(meta_label)


    def del_table(self, fileh, tableh):
        """delete a table from a HDF file

           fileh: pytables file handler
           tableh: reference to a HDF data table
        """

        tableh.remove()
        fileh.flush()

    def upd_columns(self, fileh, tableh,
                    start=None, stop=None, step=None, columns=None, names=None):
        """Modify a series of columns in the row slice [start:stop:step]
        """
        tableh.modify_columns(start=start, stop=stop, step=step, columns=columns, names=names)
        fileh.flush()

class HdfPolaIO(HdfIO):
    """Hdf5 polarimeter file format I/O

    (The class override the methods of HdfIO to cope with the different data
    structure. A better solution could be to implement a HdfIO, HdfSpectIO and HfdPolaIO)

    *Methods*
    * get_datasets - retrieve dataset tables handles
    * get_data - retrieve data
    * get_integration - retrieve integration data
    """

    def get_datasets(self, fileh):
        """Return a list of dataset(s) tables

        fileh: PyTables file handle
        """

        datasets_list = []
        for group in fileh.walk_groups("/"):
            for a in fileh.list_nodes(group, "Table"):
                if a._v_name == "Data":
                    dataset = DwDataSet()
                    dataset.th = a
                    dataset.t = a.name
                    dataset.n_channels = a.description.channels_l.shape[0]
                    dataset.bandwidth = float(group._f_getattr("Bandwith"))
                    dataset.n_samples = a.shape[0]
                    dataset.time_scale = None
                    dataset.freq_scale = None
                    datasets_list.append(dataset)
        return datasets_list

    def get_data(self, table):
        """Return a list of 2D numpy array containig the dataset (as float)

        table: Table reference
        """
        return [table.col('channels_l').astype(float),
                table.col('channels_r').astype(float),
                table.col('stokes_q').astype(float),
                table.col('stokes_u').astype(float)]

    def get_integration(self, table):
        """Return a list of 1D numpy array containig the integration time for each
           dataset sample

        table: Table reference
        """
        #return [table.col('integration_l').astype(float), table.col('integration_r').astype(float)]
        return table.col('integration_l').astype(float)

class FitsIO(DWIO):

    """Fits file format I/O

    *Methods*
    * data_open - Open the data file
    * close - Flush changes to the data file and close it
    * get_datasets - Retrieve dataset tables handles
    * get_data - Retrieve data
    * gen_flag_table - Generate flag matrix from coordinates (ymin, ymax, xmin, xmax)
    * _get_meta - Return metadata
    * get_integration - Retrieve integration data
    * get_ascension - Retrieve ascension data
    * get_azimuth - Retrieve azimuth data
    * get_declination - Retrieve declination data
    * get_elevation - Retrieve elevation data
    * get_source - Retrieve source name data
    * get_on_track - Retrieve source tracking flag
    * get_epoch_time_scale - Retrieve seconds since the epoch
    * get_first_osc - Retrieve the value of the oscillator at time 0
    * setup_new_flagset - Create a new empty extension for the flag data
    * new_flagset - Save a flag data entry in the flag table

    """

    def data_open(self, file_name):
        """Open the data file

        file_name: path to data file
        """
        # Open a file in "update" mode (necessary to add flagging)
        fileh = fits.open(file_name, mode = "update")
        return fileh

    def data_open_ro(self, file_name):
        fileh = fits.open(file_name, mode = "readonly")
        return fileh

    def check_data_type(self, fileh):
        sec_a = fileh['section table'].data['id']
        d_type_a = fileh['section table'].data['type']
        bins_a = fileh['section table'].data['bins']
        dic = dict(zip(sec_a, zip(d_type_a, bins_a)))
        return dic

    def check_corr_tab(self, fileh):
        try:
            fileh['CORR DATA TABLE']
            return True
        except:
            return False

    def dir_tree(self, dir_name):
        """Open dir tree

        dir_name: path to the directory
        """
        dirh = walk(dir_name)
        return dirh

    def filelist(self, dirh):
        flist = []
        for d, s, fs in dirh:
            for f in fs:
                flist.append((f, d))
        return flist

    def new_fit_file(self, data, file_name, fit):
        prihdu = fits.PrimaryHDU()
        farrayl = []
        for f in data.dir_datasets:
            farrayl.append(f.f[1]+"/"+f.f[0])
        farray = np.array(farrayl)
        fcol = fits.Column(name='file', format='200A', array=farray)
        cols = fits.ColDefs([fcol])
        fhdu = fits.BinTableHDU.from_columns(cols)
        fhdu.header['extname'] = "FILES TABLE"
        nbin = len(data.dir_datasets[0].th[1].data.field('Ch0')[0])
        c1array = np.array(data.sections[data.sections.keys()[0]])
        c1 = fits.Column(name='section', format='J', array=c1array)
        c2 = fits.Column(name='fit_data', format=str(nbin)+'D', array=np.array([np.zeros(nbin)]*len(data.sections)))
        cols = fits.ColDefs([c1, c2])
        dhdu = fits.BinTableHDU.from_columns(cols)
        dhdu.header['extname'] = "FIT DATA TABLE"
        l = len(fit[2])
        dhdu.data.field('fit_data')[int(data.dssel[1])][l*int(data.dssel[2]):l*int(data.dssel[2])+l] = fit[2]
        hdulist = fits.HDUList([prihdu, fhdu, dhdu])
        hdulist.writeto(file_name)

    def upd_fit_file(self, data, file_name, fit):
        l = len(fit[2])
        fileh = fits.open(file_name, mode = "update")
        fileh['FIT DATA TABLE'].data.field('fit_data')[int(data.dssel[1])][l*int(data.dssel[2]):l*int(data.dssel[2])+l] = fit[2]

    def applycorr(self, data, file_name, filelist=None):
        corrfile = self.data_open_ro(file_name)
        corrdata = corrfile['fit data table'].data.field('fit_data')
        corrdatatable = fits.BinTableHDU()
        if filelist == None:
            lf = data.flist
        else:
            lf = filelist
        for f in lf:
            fileh = self.data_open(f[1]+"/"+f[0])
            try:
                datatable = fileh['data table']
                corrdatatable = fileh['data table'].copy()
                for d in enumerate(corrdata):
                    for a in enumerate(datatable.data.field('Ch'+str(d[0]))):
                        correct = np.divide(a[1], d[1])
                        corrdatatable.data.field('Ch'+str(d[0]))[a[0]] = correct
                corrdatatable.header['extname'] = 'CORR DATA TABLE'
                try:
                    fileh['CORR DATA TABLE'] = corrdatatable
                except:
                    fileh.append(corrdatatable)
                fileh.flush()
            except:
                fileh.close()

    def opencorr(self, data, file_name):
        """Open the file containig the correction data

        data: dw dataset
        file_name: the path of the correction file
        """
        try:
            corrfile = self.data_open_ro(file_name)
            corrdata = corrfile['fit data table'].data.field('fit_data')
        except:
            raise IOError('Not a correction file!')
        data.cfile_name = file_name
        data.cfileh = corrfile
        data.corrdata = corrdata

    def close(self, fileh):
        """Flush changes to the data file and close it

        fileh: file handle
        """
        fileh.flush()
        fileh.close()

    def get_datasets(self, fileh):
        """Retrieve dataset tables handles

        fileh: file handle
        """
        datasets_list = []
        for i in fileh['section table'].data.field('id'):
            dataset = DwDataSet()
            dataset.th = [fileh, fileh['data table'], "Ch"+str(i)]
            dataset.n_channels = fileh['section table'].data.field('bins')[i]
            for a in range(fileh['rf inputs'].header['naxis2']):
                if fileh['rf inputs'].data.field('section')[a] == i and fileh['rf inputs'].data.field('polarization')[a] == "LCP":
                    dataset.bandwidth = fileh['rf inputs'].data.field('bandwidth')[a]
            dataset.n_samples = fileh['data table'].header['naxis2']
            dataset.time_scale = None
            dataset.freq_scale = None
            datasets_list.append(dataset)

        if self.check_corr_tab(fileh):
            for i in fileh['section table'].data.field('id'):
                dataset = DwDataSet()
                dataset.th = [fileh, fileh['corr data table'], "Ch"+str(i)]
                dataset.n_channels = fileh['section table'].data.field('bins')[i]
                for a in range(fileh['rf inputs'].header['naxis2']):
                    if fileh['rf inputs'].data.field('section')[a] == i and fileh['rf inputs'].data.field('polarization')[a] == "LCP":
                        dataset.bandwidth = fileh['rf inputs'].data.field('bandwidth')[a]
                dataset.n_samples = fileh['corr data table'].header['naxis2']
                dataset.time_scale = None
                dataset.freq_scale = None
                datasets_list.append(dataset)

        return datasets_list

    def get_data(self, table):
        """Retrieve data

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        tab = table[1].data
        col = table[2]
        if table[1].header['extname'] == 'DATA TABLE':
            try:
                l = len(tab.field(col)[0])
            except:
                l = 1
            b = table[0]['section table'].data.field('bins')[0]
            dat = []
            if l/b == 1:
                dat.append(tab.field(col).astype(float))
            else:
                for a in xrange(l/b):
                    r = a*b
                    t = tab.field(col)[:,r:r+b].astype(float)
                    dat.append(t)
        elif table[1].header['extname'] == 'CORR DATA TABLE':
            try:
                l = len(tab.field(col)[0])
            except:
                l = 1
            b = table[0]['section table'].data.field('bins')[0]
            dat = []
            if l/b == 1:
                dat.append(tab.field(col).astype(float))
            else:
                for a in xrange(l/b):
                    r = a*b
                    t = tab.field(col)[:,r:r+b].astype(float)
                    dat.append(t)
        elif table[1].header['extname'] == 'FLAG TABLE':
            dat = self.gen_flag_table(table)
        return dat

    def get_cdata(self, table, corrfile):
        """Retrieve corrected data

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        tab = table[1].data
        col = table[2]
        corrtab = corrfile['fit data table'].data
        mask = corrtab.field('section') == int(table[2][2:])
        if table[1].header['extname'] == 'DATA TABLE':
            try:
                l = len(tab.field(col)[0])
            except:
                l = 1
            if l != len(corrtab.field('fit_data')[0]):
                raise ValueError("Corrections length don't match data length")
            b = table[0]['section table'].data.field('bins')[0]
            dat = []
            if l/b == 1:
                raise ValueError("No corrections: total power data!")
            else:
                for a in xrange(l/b):
                    r = a*b
                    t = tab.field(col)[:,r:r+b].astype(float)
                    c = corrtab[mask].field('fit_data')[:,r:r+b]
                    for i in range(len(t)):
                        t[i] = div0(t[i], c)
                    dat.append(t)
        elif table[1].header['extname'] == 'FLAG TABLE':
            dat = self.gen_flag_table(table)
        return dat

    def get_fdatasets(self, flist):
        files_list = []
        for f in flist:
            try:
                fileh = self.data_open_ro(f[1]+"/"+f[0])
                #if self.get_type(fileh) == "on/off":
                #    if self.get_offset(fileh):
                if self.set_type(fileh) == "Off":
                    file_ds = DwDataSet()
                    file_ds.th = [fileh, fileh['data table']]
                    file_ds.n_channels = fileh['section table'].data.field('bins')
                    file_ds.f = f
                    file_ds.otype = "On/Off: off source"
                    files_list.append(file_ds)
                elif self.set_type(fileh) == "On":
                    print f[0]+'is an "On Source" data file'
                #else:
                elif self.set_type(fileh) == "OTF":
                    file_ds = DwDataSet()
                    file_ds.th = [fileh, fileh['data table']]
                    file_ds.n_channels = fileh['section table'].data.field('bins')
                    file_ds.f = f
                    file_ds.otype = "OTF"
                    files_list.append(file_ds)
                else:
                    file_ds = DwDataSet()
                    file_ds.th = [fileh, fileh['data table']]
                    file_ds.n_channels = fileh['section table'].data.field('bins')
                    file_ds.f = f
                    file_ds.otype = "Unknown"
                    files_list.append(file_ds)
            except:
                #print "not a correct data file"
                pass
        return files_list

    def get_median(self, ltable, section, pol, lrange_i, lrange_s, lexcluded):
        col = "Ch"+str(section)
        b = ltable[0][0]['section table'].data.field('bins')[int(section)]
        data = np.empty(shape=[0,b])
        for table in enumerate(ltable):
            tab = table[1][1].data
            s = table[1][0]['data table'].header['naxis2']
            range_i = lrange_i[table[0]]
            range_s = lrange_s[table[0]]
            excluded = lexcluded[table[0]]
            if range_i == 0:
                range_i = int(s)/2
            if range_s == 0:
                range_s = int(s)/2
            mpol = b*int(pol)
            Mpol = b*int(pol)+b
            data_a = tab.field(col)
            sdata = data_a[np.r_[int(excluded):int(range_i),-int(range_s):-int(excluded)],mpol:Mpol].astype(float)
            data = np.vstack((data, sdata))
        med = np.median(data, axis=0)
        xax = np.array(range(b))
        return [xax, med]

    def get_flagc(self, file_name, section):
        fileh = self.data_open_ro(file_name)
        ext = fileh['flag table']
        sec = 'Ch' + str(section)
        table = [fileh, ext, sec]
        flagt = abs(self.gen_flag_table(table)-1)
        flagc = np.prod(flagt, axis=0)
        return flagc

    def gen_flag_table(self, table):
        """Generate flag matrix from coordinates (ymin, ymax, xmin, xmax)

        table: Table reference -- [fileh, fits_extension, data_section/num_operation]
        """
        if isinstance(table[2], np.int32):
            mask = table[1].data['nop'] == table[2]
        else:
            mask = table[1].data['section'] == table[2]
        flag_matrix = np.zeros((table[1].header['rows'], table[1].header['columns']))
        for a in table[1].data[mask]:
            ymin, ymax, xmin, xmax = a['flag_data'].tolist()
            flag_matrix[ymin:ymax+1,xmin:xmax+1]=prefs.FLAG_TRUE
        return flag_matrix

    def _get_meta(self, table, column):
        """Return a 1D numpy array containig the metadata in column

        table: Table reference -- [fileh, fits_extension, data_section]
        column: a table column
        """
        ret = 0
        tab = table[1].data
        try:
            ret = tab.field(column).astype(float)
        except:
            pass

        return ret

    def get_integration(self, table):
        """Return a 1D numpy array containig the integration time for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        n = table[1].header['naxis2']
        i = table[0]['section table'].header['integration']
        ret = np.empty(n)
        ret.fill(i)
        return ret

    def get_type(self, fileh):
        scantype =  fileh[0].header['subscantype']
        return scantype

    def get_signal(self, fileh):
        signal = fileh[0].header['signal']
        return signal

    def set_type(self, fileh):
        t = self.get_type(fileh)
        try: #for files without 'signal' keyword
            s = self.get_signal(fileh)
        except:
            s = 'REFERENCE'
        res = 'Unknown'
        if t == 'TRACKING':
            if s == 'SIGNAL':
                res = 'On'
            elif s == 'REFERENCE':
                res = 'Off'
        elif t == 'RA' or 'DEC' or 'AZ' or 'EL' or 'GLON' or 'GLAT' or 'GCIRCLE':
            res = 'OTF'
        return res

    def get_scanid(self, table):
        scanid = table[0][0].header['scanid']
        return scanid

    def get_subscanid(self, table):
        subscanid = table[0][0].header['subscanid']
        return subscanid

    def get_feeds(self, fileh):
        feeds = np.unique(fileh['rf inputs'].data.field('feed'))
        return feeds

    def get_sections(self, fileh):
        feeds = self.get_feeds(fileh)
        maskif = fileh['rf inputs'].data['ifchain'] == 0
        sections = {}
        for i in feeds:
            maskf = fileh['rf inputs'].data['feed'] == i
            filt = fileh['rf inputs'].data[maskif & maskf]
            sections[i] = filt.field('section')
        #sections = range(table[0]['section table'].header['naxis2'])
        return sections

    def get_feed_section(self, fileh, tableh):
        fs = self.get_sections(fileh)
        dataset = int(tableh[2].split('h')[-1])
        for f in fs.keys():
            for s in enumerate(fs[f]):
                if s[1] == dataset:
                    return (f, s[0])

    def get_polars(self, table):
        l = len(table[1].data.field("Ch0")[0])
        b = table[0]['section table'].data.field('bins')[0]
        if int(l/b) == 2:
            return ["L", "R"]
        elif int(l/b) == 4:
            return ["L", "R", "Q", "U"]

    def get_frequency(self, table):
        tab = table[0]['rf inputs'].data
        smask = tab['section'] == int(table[2][2:])
        pmask = tab['ifchain'] == 0
        filt = tab[smask & pmask]
        res = filt.field('frequency')[0]
        return res

    def get_bandwidth(self, table, section, pol):
        if pol == "Q" or pol == "U":
            pol = "L"
        tab = table[0]['rf inputs'].data
        smask = tab['section'] == int(section)
        pmask = tab['polarization'] == pol+'CP'
        filt = tab[smask & pmask]
        res = filt.field('bandwidth')[0]
        return res

    def get_ascension(self, table):
        """Return a 1D numpy array containig the right ascension value for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'raJ2000')

    def get_azimuth(self, table):
        """Return a 1D numpy array containig the azimuth value for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'az')

    def get_declination(self, table):
        """Return a 1D numpy array containig the declination value for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'decJ2000')

    def get_elevation(self, table):
        """Return a 1D numpy array containig the elevation value for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'el')

    def get_source(self, table):
        """Return a 1D numpy array containig the source name for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        n = table[1].header['naxis2']
        i = table[0][0].header['source']
        ret = np.empty(n, dtype='|S20')
        ret.fill(i)
        return ret

    def get_on_track(self, table):
        """Return a 1D numpy array containig source tracking flag for each
           dataset sample

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'flag_track')

    def get_epoch_time_scale(self, table):
        """Return a 1D numpy array of seconds since the epoch

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        return self._get_meta(table, 'time')

    def get_first_osc(self, table):
        """Retrieve the value of the oscillator at time 0
        (used to determine the starting value of the frequency scale)

        table: Table reference -- [fileh, fits_extension, data_section]
        """
        tab = table[0]['rf inputs'].data
        return tab.field('localOscillator')[0].astype(float)

    def get_offset(self, fileh):
        ao = fileh[0].header['azimuth offset']
        eo = fileh[0].header['elevation offset']
        ro = fileh[0].header['rightascension offset']
        do = fileh[0].header['declination offset']
        gloo = fileh[0].header['galacticlon offset']
        glao = fileh[0].header['galacticlat offset']
        if (ao or eo or ro or do or gloo or glao):
            offset = True
        else:
            offset = False

        return offset

    def setup_new_flagset(self, fileh, rows, columns,
                          name_prefix = 'Flag',
                          title = 'FLAG TABLE'):
        """Create a new empty extention in the FITS file to contain flagging data.
        Save in the header of the extension the shape of the data matrix (rows, columns)
        Return the flagging table handler.

        fileh: FITS file handler
        rows: Number of rows of the data matrix
        columns: Number of columns of the data matrix
        """
        c1 = fits.Column(name='nop', format='J')
        c2 = fits.Column(name='algorithm', format='A150')
        c3 = fits.Column(name='params', format='A500')
        c4 = fits.Column(name='flagresult', format='A150')
        c5 = fits.Column(name='flag_data', format='4J')
        c6 = fits.Column(name='feed', format='A10')
        c7 = fits.Column(name='section', format='A10')
        c8 = fits.Column(name='pola', format='A10')
        flag_tab = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6, c7, c8])
        flag_tab.name = title
        flag_tab.header['rows'] = rows
        flag_tab.header['columns'] = columns
        fileh.append(flag_tab)
        flagh = fileh[title].data
        return flagh

    def new_flagset(self, fileh, tableh, rows, columns,
                    flag_areas = None, feed=None,
                    section = None, pola = None,
                    name_prefix = 'Flag',
                    title = 'FLAG TABLE',
                    algorithm="Manual",
                    params=None,
                    flagresult=None):
        """Create a new entry in the flag table. If flag table not exist call setup_new_flagset.
        Return reference to flag extension and flag table.

        fileh: FITS file handler
        rows: Number of rows of the new flag table
        columns: Number of channels
        flag_areas: List of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
        section: Section of the flagging set
        algorithm: Used algorithm
        params: Parameters of the algorithm
        flagresult: Result of the flagging operation
        """

        try:
            flagh = fileh['FLAG TABLE'].data
            try:
                lop = flagh['nop'][-1]
            except:
                lop = 0
        except:
            flagh = self.setup_new_flagset(fileh, rows, columns)
            lop = 0

        params_str = ''
        if params is not None:
            if type(params) is not str:
                for k in params.keys():
                    params_str = params_str+str(k)+': '+str(params[k])+' '
            else:
                params_str = params

        row_o = flagh.shape[0]
        c1 = fits.Column(name='nop', format='J', array=np.array([lop+1]*len(flag_areas)))
        c2 = fits.Column(name='algorithm', format='A150', array=np.array([algorithm]*len(flag_areas)))
        c3 = fits.Column(name='params', format='A500', array=np.array([params_str]*len(flag_areas)))
        c4 = fits.Column(name='flagresult', format='A150', array=np.array([flagresult]*len(flag_areas)))
        c5 = fits.Column(name='flag_data', format='4J', array=np.array(flag_areas))
        c6 = fits.Column(name='feed', format='A10', array=np.array([feed]*len(flag_areas)))
        c7 = fits.Column(name='section', format='A10', array=np.array([section]*len(flag_areas)))
        c8 = fits.Column(name='pola', format='A10', array=np.array([pola]*len(flag_areas)))
        new_flag = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6, c7, c8])
        row_n = new_flag.data.shape[0]
        flag_sum = fits.BinTableHDU.from_columns(flagh.columns, nrows=row_o+row_n)
        for colname in flagh.columns.names:
            flag_sum.data[colname][row_o:] = new_flag.data[colname]
        fileh['FLAG TABLE'].data =  flag_sum.data
        #print flag_sum.data
        #print fileh.info()
        fileh.flush()
        return (fileh['FLAG TABLE'].header['EXTNAME'], fileh['FLAG TABLE'].data)

    def new_flagset_from_array(self, fileh, tableh, rows, columns, flag_array,
                               feed = None, section = None, pola = None,
                               name_prefix = 'Flag',
                               title = 'FLAG TABLE',
                               algorithm = None,
                               params = None,
                               flagresult = None):

        """
           fileh: FITS file handler
           tableh: reference to data table
           rows: number of rows of the new flag table
           columns: number of channels
           flag_array: numpy array
           name_prefix: string to use as table name prefix
           title: string to use as table title
        """
        def sweep(A):
            height = A.shape[0]
            length = A.shape[1]
            rectangles = dict()
            result = []

            for i in xrange(length):
                column = A[:, i]

                for r in rectangles.keys():
                    minone = False
                    plusone = False
                    if r[0] != 0:
                        minone = column[r[0]-1] == prefs.FLAG_TRUE
                    if r[1] != height-1:
                        plusone = column[r[1]+1] == prefs.FLAG_TRUE

                    if i == length - 1 and all([x == prefs.FLAG_TRUE for x in column[r[0]:r[1]+1]]) and (not minone and not plusone):
                        result.append((r[0], r[1], rectangles[r], i))
                    elif any([x == prefs.FLAG_FALSE for x in column[r[0]:r[1]+1]]) or minone or plusone:
                        result.append((r[0], r[1], rectangles[r], i-1))
                        del rectangles[r]

                newRectangle = False
                start = 0
                for j in xrange(height):
                    if column[j] == prefs.FLAG_TRUE and not newRectangle:
                        start = j
                        newRectangle = True
                    elif column[j] == prefs.FLAG_FALSE and newRectangle:
                        if not (start, j-1) in rectangles:
                            rectangles[(start, j-1)] = i
                        newRectangle = False
                    elif j == height-1 and newRectangle:
                        if not (start, j) in rectangles:
                            rectangles[(start, j)] = i
                        newRectangle = False

                if i == length - 1 and newRectangle:
                    for r in rectangles.keys():
                        result.append((r[0], r[1], rectangles[r], i))
            return result

        flags = sweep(flag_array)
        ret = self.new_flagset(fileh, tableh, rows, columns, flags, feed,
                               section, pola, name_prefix, title, algorithm,
                               params, flagresult)
        return ret

    def upd_flagset(self, flagh, rows, columns, flag_areas, flag_value = prefs.FLAG_TRUE):
        """
           flagh: reference to a HDF data table
           rows: number of rows of the flag table
           columns: number of channels
           flag_areas: list of rectangular areas to be set as flagged (xmin, xmax, ymin, ymax)
           flag_value: flag value to set to
        """
        pass

    def get_flagsets(self, fileh, tableh):
        """Return a dictionary of handlers to the flagging data

           fileh: FITS file handler
           tableh: reference to the flag table and operation
        """
        flagsets_dict = {}
        rif_dict = {}
        fs = self.get_feed_section(fileh, tableh)
        masks = fileh['FLAG TABLE'].data['section'] == str(fs[1])
        maskf = fileh['FLAG TABLE'].data['feed'] == str(fs[0])
        filt = fileh['FLAG TABLE'].data[maskf & masks]

        for a in set(filt['nop']):
            item = [fileh, fileh['flag table'], a]
            mask2 = fileh['FLAG TABLE'].data['nop'] == a
            pol = fileh['FLAG TABLE'].data[mask2]['pola'][0]
            alg = fileh['FLAG TABLE'].data[mask2]['algorithm']
            rif = (fs[0], fs[1], pol, alg)
            flagsets_dict['Flag_F'+str(fs[0])+'S'+str(fs[1])+':'+str(a)] = item
            rif_dict['Flag_F'+str(fs[0])+'S'+str(fs[1])+':'+str(a)] = rif
        return flagsets_dict, rif_dict

    def propag_flag_table(self, fileh, file_list):
        errorl = []
        try:
            flagt = fileh['flag table']
        except:
            raise KeyError('FLAG TABLE not found!')
        for f in file_list:
            try:
                newf = fits.open(f, mode='update')
                try:
                    ft = newf['flag table']
                    nrows = ft.data.shape[0]+flagt.data.shape[0]
                    nt = fits.BinTableHDU.from_columns(ft.columns, nrows=nrows)
                    for colname in ft.columns.names:
                        nt.data[colname][ft.data.shape[0]:] = flagt.data[colname]
                    newf['flag table'].data = nt.data
                    newf.flush()
                except:
                    newf.append(flagt)
                    newf.flush()
            except:
                errorl.append(f)
        return errorl

    def propag_to_feed(self, fileh, nop, feed):
        """
        make a copy of the flags of a given nop (number of operation)
        with another feed value
        """
        flagd = fileh['FLAG TABLE'].data
        flagmask = flagd['nop'] == nop
        flagnop = flagd[flagmask]
        ofeed = flagnop['feed'][0]

        flagareas = flagnop['flag_data']
        section = flagnop['section'][0]
        pola = flagnop['pola'][0]
        algorithm = flagnop['algorithm'][0]
        params = flagnop['params'][0]+'(copy of nop={}, feed={})'.format(nop, ofeed)
        flagresult = flagnop['flagresult'][0]

        self.new_flagset(fileh, None, 0, 0, flagareas, feed, section, pola,
                         'Flag', 'FLAG TABLE', algorithm, params, flagresult)

    def get_table_meta(self, tableh, meta_label):
        """Return table metadata

           tableh: reference to data table and operation
           meta_label: metadata name (string)
        """

        mask = tableh[1].data['nop'] == tableh[2]
        meta = tableh[1].data[mask][meta_label][0]
        return meta

    def del_table(self, fileh, tableh):
        """Delete a flag operation data from flag table

           fileh: FITS file handler
           tableh: reference to data table and operation
        """
        mask = fileh['FLAG TABLE'].data['nop'] != tableh[2]
        nnop = fileh['FLAG TABLE'].data[mask]['nop']
        for i in range(len(nnop)):
            if nnop[i] > tableh[2]:
                nnop[i] -= 1
        c1 = fits.Column(name='nop', format='J', array=nnop)
        c2 = fits.Column(name='algorithm', format='A150', array=fileh['FLAG TABLE'].data[mask]['algorithm'])
        c3 = fits.Column(name='params', format='A500', array=fileh['FLAG TABLE'].data[mask]['params'])
        c4 = fits.Column(name='flagresult', format='A150', array=fileh['FLAG TABLE'].data[mask]['flagresult'])
        c5 = fits.Column(name='flag_data', format='4J', array=fileh['FLAG TABLE'].data[mask]['flag_data'])
        c6 = fits.Column(name='feed', format='A10', array=fileh['FLAG TABLE'].data[mask]['feed'])
        c7 = fits.Column(name='section', format='A10', array=fileh['FLAG TABLE'].data[mask]['section'])
        c8 = fits.Column(name='pola', format='A10', array=fileh['FLAG TABLE'].data[mask]['pola'])

        flag_tab = fits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6, c7, c8])
        #if flag_tab.data.shape[0] == 0:
        #    fileh.__delitem__('FLAG TABLE')
        #else:
        fileh['FLAG TABLE'].data =  flag_tab.data
        fileh.flush()

    def del_sel_flags(self, fileh, feed, section, pola, rect):
        try:
            ftable = fileh['flag table'].data
        except:
            raise KeyError('FLAG TABLE not found!')
        rlist = []
        for i, row in enumerate(ftable):
            flag = row['flag_data']
            rfeed = row['feed']
            rsect = row['section']
            rpola = row['pola']
            dx = min(flag[3], rect[3]) - max(flag[2], rect[2])
            dy = min(flag[1], rect[1]) - max(flag[0], rect[0])
            if dx < 0 or dy < 0 or rfeed != str(feed) or rsect != str(section) or rpola != pola:
                rlist.append(i)
        newftable = ftable[rlist]
        fileh['flag table'].data = newftable
        fileh.flush()

    def rupd_columns(self, fileh, tableh,
                    start=None, stop=None, step=None, columns=None, names=None):
        """Modify a series of columns in the row slice [start:stop:step]
        """
        pass
