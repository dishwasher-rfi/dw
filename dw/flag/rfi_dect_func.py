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
dw.flag.rfi_dect_func
=====================

Implement automatic detection of RFI

Classes
-------
* AutoFlagSet - Define a data structure for automatically generated flagging sets
* FlagAlgorithm - Base class for RFI detection algorithms implementation
* FullChan - Return flag matrix (intended for continuously interfered channels)
* FullDWT - Return 3D flag matrix (2D data + 1D DWT decomposition)
* FlagLibDw - Class for RFI detection using libdw
* SingleChLibdw - (TEST CLASS) flag a single channel using libdw
* EvenOddLibdw - (TEST CLASS) flag even and odd channels writing output in separate flaging matrices using libdw

Functions
---------
* bootstrap_resample - Return a bootstrap resampled array_like
"""

import ctypes as ct

from matplotlib.mlab import prctile
import scipy.ndimage as sp_dip
from scipy.stats import normaltest as sp_normaltest
from scipy.stats import threshold as sp_threshold

from numpy import array as np_array
from numpy import median as np_median
from numpy import min as np_min
from numpy import zeros as np_zeros
from numpy import sqrt as np_sqrt
from numpy import std as np_std
#from numpy import ceil as np_ceil
#from numpy import log2 as np_log2
from numpy import floor as np_floor
from numpy.random import rand as np_rand
from numpy import uint8 as np_uint8
from numpy import nan

import pywt

import dw.flag.conf as conf

try:
    libdw=ct.CDLL(conf.libdw_loc_dir)
except:
    libdw=ct.CDLL(conf.libdw_dir)

id_dict = {"Manual":"MN", "SimpleThreshold":"ST", "Full_channel":"FC",
           "Channel_DWT":"WT", "_libdw":"LD", "Single_channel_libdw":"SC",
           "Even_odd_libdw":"EO"}

class AutoFlagSet():

    """Define a data structure for automatically generated flagging sets

    * flag_data: 2D array with flagging data
    * algorithm: used algorithm's name
    * flagresult: identifier of the flagging matrix (string)
    * params: dict of algorithm's used parameters
    """

    def __init__(self):
        self.flag_data = None
        self.algorithm = None
        self.flagresult = None
        self.params = None
        self.feed = None
        self.section = None
        self.pola = None


class FlagAlgorithm(object):
    """Base class for RFI detection algorithms implementation

    *Class variables*
    * name - name of the implementes algorithm (empty string here)
    * descritpion - descritpion of the implementes algorithm (empty string here)
    * def_params - dictionary of algorithm's parameters (empty dict here)

    *Methods*
    * __init__ - initialize data and parameters
    * get_implementations - return the subclasses (i.e. available RFI dect algorithms)
    * get_def_params - return the dictionary of the default parameters
    * get_def_params_names - return a list of default parameters names
    * get_def_params_values - return a list of default parameters values
    * get_params - return the dictionary of the current parameters
    * get_params_names - return a list of the current parameters names
    * get_params_values - return a list of the current parameters values
    * upd_param_values - update the value of a parameter
    * _set_avail_output - set the algorithm's available output options
    * get_avail_output - return a list of the algorithm's available output options
    * _set_def_output - set the algorithm's default output options
    * get_def_output - return a list of the algorithm's default output options
    * set_output - populate the output data structure
    * get_output - return the output data structure
    * get_output_labels - return a list of selected output options
    * is_out_selected - check if a output option is selected
    * is_out_avail - check if a output option is available
    * is_out_default - check if a output option is default
    * _autoset_params - automatically set params ont he base of input and parameters (TO BE OVERRIDDEN)
    * _define_output - define the available and default output options labels (TO BE OVERRIDDEN)
    * compute - detect RFI (TO BE OVERRIDDEN)
    """
    name = ""
    description = ""
    def_params = {}
    is_exec = False

    def __init__(self, data, **kwargs):
        """Initialize data and parameters

        * data - data matrix to detect RFI on
        * kwargs - algorithm's parameters (dictionary)
        """
        self.data = data
        self.params = dict(self.def_params)
        self.upd_params_values(**kwargs)
        self._autoset_params()
        self._define_output()

    @classmethod
    def get_implementations(cls):
        """Return the subclasses (i.e. available RFI dect algorithms)
        """
        implementations = cls.__subclasses__() + [g for s in cls.__subclasses__() for g in s.get_implementations()]
        exec_impl = []
        for implementation in implementations:
            if implementation.is_exec:
                exec_impl.append(implementation)

        return exec_impl

    @classmethod
    def get_def_params(cls):
        """Return the dictionary of the default parameters
        """
        return cls.def_params

    @classmethod
    def get_def_params_names(cls):
        """Return a list of default parameters names
        """
        return cls.get_def_params().keys()

    @classmethod
    def get_def_params_values(cls):
        """Return a list of default parameters values
        """
        return cls.get_def_params().values()

    def get_params(self):
        """Return the dictionary of the current parameters
        """
        return self.params

    def get_params_names(self):
        """Return a list of the current parameters names
        """
        return self.get_params().keys()

    def get_params_values(self):
        """Return a list of the current parameters values
        """
        return self.get_params().values()

    def upd_param_value(self, param, value):
        """Update the value of a parameter

        param - parameter name (string)
        value - parameter value
        """
        self.params.update({param: value})
        self.__dict__.update(self.params)

    def upd_params_values(self, **par_dict):
        """Update the parameters

        par_dict - dictionary of param: value
        """
        self.params.update(par_dict)
        self.__dict__.update(self.params)

    def _set_avail_output(self, labels):
        """Set the algorithm's available output options

        labels - list of output options labels
        """
        self.avail_outputs = labels

    def get_avail_output(self):
        """Return a list of the algorithm's available output options
        """
        return self.avail_outputs

    def _set_def_output(self, labels):
        """Set the algorithm's default output options

        labels - list of output options labels
        """
        self.def_outputs = labels

        self.set_output(labels = self.def_outputs)

    def get_def_output(self):
        """Return a list of the algorithm's default output options
        """
        return self.def_outputs

    def set_output(self, labels = None):
        """Populate the output data structure

        labels - list of output options labels to select
        """
        if labels == None:
            labels = self.get_def_output()

        self.flag_results = {}

        for label in labels:
            if self.is_out_avail(label):
                flag = AutoFlagSet()
                flag.flag_data = np_zeros(self.data[0].shape).astype(np_uint8)
                flag.algorithm = self.name
                flag.flagresult = label
                flag.params = self.get_params()

                self.flag_results[label] = flag

    def get_output(self):
        """Return the output data structure
        """
        return self.flag_results

    def get_output_labels(self):
        """Return a list of selected output options
        """
        return self.get_output().keys()

    def is_out_selected(self, label):
        """Check if a output option is selected

        label - output option label
        """
        return self.get_output().has_key(label)

    def is_out_avail(self, label):
        """Check if a output option is avalilable

        label - output option label
        """
        return dict(zip(self.get_avail_output(),self.get_avail_output())).has_key(label)

    def is_out_default(self, label):
        """Check if a output option is default

        label - output option label
        """
        return dict(zip(self.get_def_output(),self.get_def_output())).has_key(label)

    def _autoset_params(self):
        """Atomatically set params on the base of input and parameters
        TO BE OVERRIDDEN in actual algorithm implementation class
        """
        pass

    def _define_output(self):
        """Define the available and default output options labels
        TO BE OVERRIDDEN in actual algorithm implementation class
        """
        pass

    def compute(self):
        """Detect RFI
        TO BE OVERRIDDEN in actual algorithm implementation class
        """
        pass


class SimpleThreshold(FlagAlgorithm):
    """Detect RFI

    *Class variables*
    * name - name of the implementes algorithm
    * descritpion - descritpion of the implementes algorithm
    * def_params - dictionary of algorithm's parameters

    *Methods*
    * _define_output - define the available and default output options labels
    * compute - detect RFI

    *Algorithm's parameters*
    * median_size_time:
    * median_size_freq:
    * th_k:
    * p_th:

    *Algorithm's output flagging matrices*
    * normal:
    * not_normal:

    """
    name = "SimpleThreshold"
    description = "Detection using a threshold on the median of the entire matrix"
    def_params = {'num_of_rms_above_median':(2., 0., nan)}
    is_exec = True

    def _define_output(self):
        """Define the available and default output options labels
        """
        self._set_avail_output(['L', 'R', 'Q', 'U'])
        self._set_def_output(['L', 'R'])

    def compute(self):
        """Detect RFI
        """
        m_ind = {'L':0, 'R':1, 'Q':2, 'U':3}
        if self.num_of_rms_above_median[0] <= self.num_of_rms_above_median[1] or self.num_of_rms_above_median[0] >= self.num_of_rms_above_median[2]:
            raise ValueError
            return 0
        for lab in self.flag_results.keys():
            med = np_median(self.data[m_ind[lab]][self.data[m_ind[lab]]>10])
            rms = np_sqrt(((self.data[m_ind[lab]][self.data[m_ind[lab]]>10] - med)**2).mean())
            res = sp_threshold(self.data[m_ind[lab]]-med, threshmin=self.num_of_rms_above_median[0]*rms, newval=0)
            res[res > 0] = 1
            self.flag_results[lab].pola = lab
            self.flag_results[lab].flag_data = res
        return self.flag_results


class FullChan(FlagAlgorithm):
    """Detect RFI

    *Class variables*
    * name - name of the implementes algorithm
    * descritpion - descritpion of the implementes algorithm
    * def_params - dictionary of algorithm's parameters

    *Methods*
    * _define_output - define the available and default output options labels
    * compute - detect RFI

    *Algorithm's parameters*
    * median_size_time:
    * median_size_freq:
    * th_k:
    * p_th:

    *Algorithm's output flagging matrices*
    * normal:
    * not_normal:

    """
    name = "Full_channel"
    description = "Detection of completely interfered channels"
    def_params = {'median_size_time': 1,
                  'median_size_freq': 5,
                  'th_k': 10.,
                  'p_th': .01}
    is_exec = False

    def _define_output(self):
        """Define the available and default output options labels
        """
        self._set_avail_output(['Normal', 'Not_normal'])
        self._set_def_output(['Not_normal'])

    def compute(self):
        """Detect RFI
        """
        median_size = (self.median_size_time, self.median_size_freq)

        data = self.data-sp_dip.median_filter(self.data, size=median_size)
    #    data1 = np.abs(np.sum(data,0))
    #    data1 = np.abs(np.median(data,0))
        data1 = (np_median(data,0))
    #    th = np.percentile(data1, th_prctile)
        thl = []
        for ii in xrange(data1.shape[0]-9):
            thl.append(prctile(data1[ii:ii+10],p=90))
     #       thl.append(max(data1[ii:ii+10]))

        th = self.th_k*np_median(thl)
        for ii in xrange(data1.shape[0]):
            if data1[ii] > th:
                z,p_value = sp_normaltest(data[:,ii])
                if p_value < self.p_th:
                    if self.is_out_selected('Not_normal'):
                        self.flag_results['Not_normal'].flag_data[:,ii] = 1
                else:
                    if self.is_out_selected('Normal'):
                        self.flag_results['Normal'].flag_data[:,ii] = 1
        return self.flag_results


class FullDWT(FlagAlgorithm):
    """Return 3D flag matrix (2D data + 1D DWT decomposition)

    *Methods*
    * chan_dwt - Return 1 channel flagging array
    * baseline_dwt - Return the estimation of the data baseline based on DWT
    * noise_dwt - Return the estimation of the DWT components noise level
    * waverec - Return 1D DWT reconstructed data using details up to levels
    * waverec_levels - Return 1D DWT reconstructed data using selected details levels
    * wavecomp - Return DWT reconstructed component

    *Algorithm's parameters*
    * level:
    * th_k:

    *Algorithm's output flagging matrices*
    * #:

    """

    name = "Channel_DWT"
    description = "Detection of intermittent RFI on sigle channel using DWT"
    def_params = {'level': 0,
                  'th_k': 1.}
    is_exec = False

    def _autoset_params(self):
        """Atomatically set level from data size (number of time samples)
        """

        if self.level == 0:
            self.w = pywt.Wavelet('haar')
#           self.upd_param_value('level',int(np_ceil(np_log2(self.data.shape[0])).astype(int)))
            self.upd_param_value('level',int(pywt.dwt_max_level(self.data.shape[0], self.w)))

    def _define_output(self):
        """Define the available and default output options labels
        """

        self._set_avail_output(map(str,range(self.level)))
        self._set_def_output(map(str,range(self.level/2, min(self.level, self.level/2+3))))

    def compute(self):
        """
        """

        flag = np_zeros((self.data.shape[0], self.data.shape[1], self.level))
#        w = pywt.Wavelet('haar')

        for ii in xrange(self.data.shape[1]):
            coeff = pywt.wavedec(self.data[:,ii], wavelet=self.w, mode='cpd', level = self.level)
            th = self.noise_dwt(coeff,self.w)*self.th_k
            flag[:,ii,:] = self.chan_dwt(coeff,self.w, th = th)


        for label in self.get_output_labels():
            self.flag_results[label].flag_data = flag[:,:,int(label)]


        return self.flag_results

    @classmethod
    def chan_dwt(cls, coeff,w, th = None):
        """Return 1 channel flagging array

        coeff: DWT coefficients
        w: pywt wavelet object
        th: thresholds array
        """
        if th == None:
            th = cls.noise_dwt(coeff,w)
        ch_flag = np_zeros((len(coeff[-1])*2, len(coeff)-1))
        offset = cls.baseline_dwt(coeff, w)
        for ll in xrange(len(coeff)-1):
            ch_flag[:,ll] = ((cls.waverec(coeff,w,ll,offset=False)-offset)>th[ll]).astype(float)

        return ch_flag

    @classmethod
    def baseline_dwt(cls, coeff, w):
        """Return the estimation of the data baseline based on DWT

        coeff: DWT coefficients
        w: pywt wavelet object
        """
        return np_min(cls.waverec(coeff, w, len(coeff)/2))

    @classmethod
    def noise_dwt(cls, coeff, w):
        """Return the estimation of the DWT components noise level

        coeff: DWT coefficients
        w: pywt wavelet object
        """
        n_boot = 1000
        k_th = 10
        k_std = 1./np_sqrt(2)
        std_l = []
        std_a = np_zeros(n_boot)
        wcomp = cls.wavecomp(coeff, w, len(coeff)-1)

        for ii in xrange(n_boot):
            std_a[ii] = np_std(bootstrap_resample(wcomp, 10))

        stdv = np_median(std_a)
        std_l.append(stdv)
        for ll in xrange(len(coeff)-2,0,-1):
            stdv = stdv*k_std
            std_l.append(stdv)
        std_l.append(0)

        std_l.reverse()
        return np_array(std_l)*k_th

    @classmethod
    def waverec(cls, coeff, w, level, offset = False):
        """Return 1D DWT reconstructed data using details up to levels

        coeff: DWT coefficients
        w: pywt wavelet object
        level: DWT details component
        offset: if TRUE, subtract offset from data
        """

        if offset:
            offset = np_min(cls.waverec(coeff, w, len(coeff)/2))
        else:
            offset = 0

        loc_coeff = coeff[:]
        for ll in xrange(level+1, len(coeff)):
            loc_coeff[ll] = np_zeros(coeff[ll].shape)

        return pywt.waverec(loc_coeff,w) - offset

    @classmethod
    def waverec_levels(cls, coeff, w, levels, offset = False):
        """Return 1D DWT reconstructed data using selected details levels

        coeff: DWT coefficients
        w: pywt wavelet object
        level: DWT details component
        offset: if TRUE, subtract offset from data
        """

        if offset:
            offset = np_min(cls.waverec(coeff, w, 0))
        else:
            offset = 0

        loc_coeff = []
        for ll in xrange(len(coeff)):
            loc_coeff.append(np_zeros(coeff[ll].shape))

        for ll in levels:
            loc_coeff[ll] = coeff[ll]

        return pywt.waverec(loc_coeff,w) - offset

    @classmethod
    def wavecomp(cls, coeff, w, level):
        """Return 1D DWT reconstructed component

        coeff: DWT coefficients
        w: pywt wavelet object
        level: DWT details component
        """

        loc_coeff = []
        for ll in xrange(len(coeff)):
            loc_coeff.append(np_zeros(coeff[ll].shape))

        loc_coeff[level] = coeff[level]

        return pywt.waverec(loc_coeff,w)

class FlagLibDw(FlagAlgorithm):
    """Class for RFI detection using libdw

    *Methods*
    * __init__ - initialize data and parameters
    * set_output -
    """

    name = "_libdw"
    is_exec = False
    c_init = libdw.init_dw
    c_alloc_out = libdw.dw_alloc_flag_out
    c_set_out = libdw.dw_set_flag_out
    c_set_out_prod = libdw.dw_set_flag_prod
    c_compute = None

    def __init__(self, data, **kwargs):
        """Initialize data and parameters
        Override the super class method to set datastructure to use with libdw

        * data - data matrix to detect RFI on
        * kwargs - algorithm's parameters (dictionary)
        """

        class DwStruct(ct.Structure):
            """Define a data structure to pass to C library libdw
            """
            _fields_=[("data", ct.POINTER(ct.c_double * data.shape[1] * data.shape[0])),
                      ("rows", ct.c_int),
                      ("cols", ct.c_int),
                      ("flag_data", ct.POINTER(ct.POINTER(ct.c_byte))),
                      ("flag_data_ind", ct.POINTER(ct.c_int)),
                      ("l_flag", ct.c_int),
                      ("flag_product", ct.POINTER(ct.c_int)),
                      ("l_flag_prod", ct.c_int)]

        self.dw_struct = DwStruct()

        super(FlagLibDw, self).__init__(data, **kwargs)
#        self.n_rows = ct.c_int(data.shape[0])
#        self.n_cols = ct.c_int(data.shape[1])
#        self.c_data = data.ctypes.data_as(ct.POINTER(ct.c_double * self.data.shape[0] * self.data.shape[1]))
        self.c_init(ct.pointer(self.dw_struct),
                    data.ctypes.data_as(ct.POINTER(ct.c_double * self.data.shape[1] * self.data.shape[0])), #data
                    ct.c_int(data.shape[0]), #rows
                    ct.c_int(data.shape[1])) #cols

    def set_output(self, labels = None):
        """Populate the output data structure
        Override the super class method to setup a proper C structure
        to get libdw out

        labels - list of output options labels to select
        """

        super(FlagLibDw, self).set_output(labels)

        l_flag_product = len(self.get_avail_output())
        l_flag = len(self.get_output())
        flag_product = (ct.c_int * l_flag_product)()
        flag_data_ind = (ct.c_int * l_flag)()
        self.c_alloc_out(ct.pointer(self.dw_struct), ct.c_int(l_flag))

        ii = 0; #flag data counter
        jj = 0; #flag_product array counter
        for label in self.get_avail_output():
            flag_product[jj] = ct.c_int(-1)
            if self.is_out_selected(label):
                flag_product[jj] = ct.c_int(ii)
                flag_data_ind[ii] = ct.c_int(jj)
                self.c_set_out(ct.pointer(self.dw_struct),
                               self.flag_results[label].flag_data.ctypes.data_as(ct.POINTER(ct.c_byte * self.data.shape[1] * self.data.shape[0])),
                               ct.c_int(ii))
                ii = ii + 1
            jj = jj + 1

        self.c_set_out_prod(ct.pointer(self.dw_struct),
                            ct.pointer(flag_product),
                            ct.c_int(l_flag_product),
                            ct.pointer(flag_data_ind))

    def compute(self):
        """Call a RFI detection algorithm C imlementation in libdw

        The method has NOT to be overridden in subclasses calling libdw algorithms
        """
        params = self.get_params()
        params_string = ""
        for param in self.c_params_order:
            params_string = params_string + str(params[param])

        self.c_compute(ct.pointer(self.dw_struct), eval(params_string))

        return self.flag_results

class SingleChLibdw(FlagLibDw):
    """TEST CLASS
    flag a single channel using libdw

    *Methods*
    * _define_output - Define the available and default output options labels
    """
    name = "Single_channel_libdw"
    def_params = {'channel': 0}
    c_params_order = ['channel']
    is_exec = False
    c_compute = libdw.dw_single_channel

    def _define_output(self):
        """Define the available and default output options labels
        """
        self._set_avail_output(['Test'])
        self._set_def_output(['Test'])

class EvenOddLibdw(FlagLibDw):
    """TEST CLASS
    flag even and odd channels writing output in separate flaging matrices
    using libdw

    *Methods*
    * _define_output - Define the available and default output options labels
    """
    name = "Even_odd_libdw"
    def_params = {'channel_start': 0}
    c_params_order = ['channel_start']
    is_exec = False
    c_compute = libdw.dw_even_odd

    def _define_output(self):
        """Define the available and default output options labels
        """
        self._set_avail_output(['Even', 'Odd'])
        self._set_def_output(['Even', 'Odd'])

def bootstrap_resample(X, n=None):
    """ Return a bootstrap resampled array_like

    X : array_like data to resample
    n : int, optional length of resampled array, equal to len(X) if n==None
    """
    if n == None:
        n = len(X)

    resample_i = np_floor(np_rand(n)*len(X)).astype(int)
    X_resample = X[resample_i]
    return X_resample

