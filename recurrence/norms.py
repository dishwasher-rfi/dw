#!/usr/bin/env python

# Copyright (C) 2015 - IRA-INAF
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
recurrence.py
================

Vectorial norms definition for
Recurrence Plot and Recurrence Quantification Analysis

Classes
-------
*

"""

from multiprocessing import Pool, cpu_count

from numpy.linalg import norm as np_norm
from numpy import zeros as np_zeros
from scipy.linalg import norm as sp_norm

class RecurrenceNorm(object):

    is_simmetric = None
    is_multiprocess = None

    @staticmethod
    def compute(x, y):
        raise NotImplemented

    @classmethod
    def get_implementations(cls):
        return cls.__subclasses__()

class L2Norm(RecurrenceNorm):

    is_simmetric = True
    is_multiprocess = False

    @staticmethod
    def compute(x, y):
        return np_norm(x-y,axis=1)

class L2NormBlas(RecurrenceNorm):

    is_simmetric = True
    is_multiprocess = False

    @staticmethod
    def compute(x, y):
        nv = np_zeros(x.shape[0])
        for ii in xrange(x.shape[0]):
            nv[ii] = sp_norm(x[ii,:]-y[ii,:])

        return nv

class L2NormBlasMp(RecurrenceNorm):

    is_simmetric = True
    is_multiprocess = True

    nproc = cpu_count()

    @staticmethod
    def compute(x, y):
        p = Pool(L2NormBlasMp.nproc)
        nv = p.map(sp_norm, x-y, x.shape[0]/L2NormBlasMp.nproc)
        p.close()
        p.terminate()
        return nv




