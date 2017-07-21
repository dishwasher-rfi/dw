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

Recurrence Plot and Recurrence Quantification Analysis

Functions
---------
* count_seq -

Classes
-------
* Recurrence -

"""
#from multiprocessing import Process, Array, Queue, Pool

import norms as rec_norm
from numpy import zeros as np_zeros
from numpy import fill_diagonal as np_fill_diagonal
from numpy import sum as np_sum
from numpy import diff as np_diff
from numpy import nonzero as np_nonzero
from numpy import hstack as np_hstack
from numpy import min as np_min
from numpy import max as np_max
from numpy import diagonal as np_diagonal
from numpy import array as np_array
from numpy import append as np_append
from numpy import sort as np_sort
from numpy import log as np_log

def count_seq(x):

    stop = np_nonzero(np_diff(np_hstack((x,0))) == -1)
    start = np_nonzero(np_diff(np_hstack((0,x))) == 1)

    ld = {}
    if len(start[0]):
        d = stop[0]-start[0]+1
        for ll in xrange (np_max((np_min(d),2)), np_max(d)+1):
            ld[str(ll)] = np_sum((d == ll).astype(int))

    return ld

class Recurrence(object):
    """ Compute recurrence plot and recurrence quantification analysis measures

    Methods
    -------
    * __init__ -
    * set_norm -
    * _plot -
    * r_plot -
    * cr_plot-
    * jr_plot -
    * rqa_rr -
    * rqa_l_freq_dist -
    * rqa_v_freq_dist -
    * _rqa_meas -
    * _rqa_lv_dist_min -
    * rqa_det -
    * rqa_lam -
    * rqa_ratio -
    * rqa_l -
    * rqa_tt -
    * _rqa_lv_max -
    * rqa_l_max -
    * rqa_v_max -
    * rqa_div -
    * rqa_entr -
    """
    def __init__(self, norm = rec_norm.L2NormBlas()):
        self.set_norm(norm)

    def set_norm(self, norm):
        self.norm = norm

    def _plot(self, x, y = None):

        cr = True
        if y == None:
            cr = False
            y = x

        length = x.shape[0]
        rplot = np_zeros((length,length))

        if cr:
            np_fill_diagonal(rplot,self.norm.compute(x,y))

        if self.norm.is_simmetric:
            for lag in xrange(1,length):
                d = self.norm.compute(x[0:-lag],y[lag:])
                np_fill_diagonal(rplot[lag:,0:-lag],d)
                np_fill_diagonal(rplot[0:-lag,lag:],d)

#            rplot = np_rot90(rplot)

        else:
            pass

        return rplot

#    def _plot_mp(self, x, y = None):
#
#        print "mp->"
#
#        if y == None:
#            cr = False
#            y = x
#
#        length = x.shape[0]
#        rplot = np_zeros((length,length))
#
#        if cr:
#            np_fill_diagonal(rplot,self.norm.compute(x,y))
#
#        if self.norm.is_simmetric:
#            p = Pool(processes=4)
#            p.map(rec_norm.TestNorm, x)
##            q = Queue()
##            workers = [Process(target=rp_par, args = (q, x, y, lag))
##                for lag in range(length)]
##
##            for p in workers:
##                p.start()
##            for p in workers:
##                p.join()
##            while not q.empty():
##                print q.get(),


    def r_plot(self, x):
        self.rplot = self._plot(x)
        self.rr = {}
        self.p_l = {}
        self.p_v = {}
        self.det = {}
        self.lam = {}
        self.ratio = {}
        self.l = {}
        self.tt = {}
        self.l_max = {}
        self.v_max = {}
        self.entr = {}
        return self.rplot

    def cr_plot(self, x, y):
        crplot = 0
        self.crplot = self._plot(x,y)
        return crplot

    def jr_plot(self, x, y):
        jrplot = 0
        return jrplot

    def rqa_rr(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return self.rr[str(th)]
        except KeyError:
            self.rr[str(th)] = np_sum(self.rplot < th).astype(float)/self.rplot.size
            return self.rr[str(th)]

    def rqa_l_freq_dist(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return self.p_l[str(th)]
        except KeyError:
            self.p_l[str(th)] = {}
            if self.norm.is_simmetric:
                range_start = 1
                self.p_l[str(th)][str(self.rplot.shape[0])] = 1
                k = 2
            else:
                range_start =  -self.rplot.shape[0]
                k = 1

            for dd in xrange (range_start, self.rplot.shape[0]):
                dl =  count_seq(np_diagonal((self.rplot < th).astype(int), dd))
                for item in dl.iteritems():
                    try:
                        self.p_l[str(th)][str(item[0])]
                    except KeyError:
                        self.p_l[str(th)][str(item[0])] = 0

                    self.p_l[str(th)][str(item[0])] = self.p_l[str(th)][str(item[0])] + k*item[1]

            return self.p_l[str(th)]


    def rqa_v_freq_dist(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return self.p_v[str(th)]
        except KeyError:
            self.p_v[str(th)] = {}

            for dd in xrange (0, self.rplot.shape[0]):
                dl =  count_seq((self.rplot < th).astype(int)[:,dd])
                for item in dl.iteritems():
                    try:
                        self.p_v[str(th)][str(item[0])]
                    except KeyError:
                        self.p_v[str(th)][str(item[0])] = 0

                    self.p_v[str(th)][str(item[0])] = self.p_v[str(th)][str(item[0])] + item[1]

            return self.p_v[str(th)]

    def _rqa_meas(self, th, m_min, freq_dist, den, measure_dict):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return measure_dict[str(th)][str(m_min)]
        except KeyError:
            l,p = self._rqa_lv_dist_min(th, m_min, freq_dist, ret_sum = 0)

            try:
                measure_dict[str(th)]
            except KeyError:
                measure_dict[str(th)] = {}

            measure_dict[str(th)][str(m_min)] = l.astype(float).dot(p)/den

            return measure_dict[str(th)][str(m_min)]

    def _rqa_lv_dist_min(self, th, m_min, freq_dist, ret_sum = 0):
        l = np_array([])
        p = np_array([])
        for item in freq_dist(th).items():
            if float(item[0]) >= m_min:
                if item[1]:
                    l = np_append(l, item[0])
                    p = np_append(p, item[1])

        if ret_sum:
            return p.sum()
        else:
            return (l,p)

    def rqa_det(self, th, l_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        return  self._rqa_meas(th, l_min, self.rqa_l_freq_dist,
                               self.rqa_rr(th)*self.rplot.shape[0]*self.rplot.shape[0],
                               self.det)

    def rqa_lam(self, th, v_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        return  self._rqa_meas(th, v_min, self.rqa_v_freq_dist,
                               self.rqa_rr(th)*self.rplot.shape[0]*self.rplot.shape[0],
                               self.lam)

    def rqa_ratio(self, th, l_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return self.ratio[str(th)][str(l_min)]
        except KeyError:
            try:
                self.ratio[str(th)]
            except KeyError:
                self.ratio[str(th)] = {}

            self.ratio[str(th)][str(l_min)] = self.rqa_det(th, l_min)/self.rqa_rr(th)

            return self.ratio[str(th)][str(l_min)]

    def rqa_l(self, th, l_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        return  self._rqa_meas(th, l_min, self.rqa_l_freq_dist,
                               self._rqa_lv_dist_min(th, l_min, self.rqa_l_freq_dist, ret_sum = 1),
                               self.l)

    def rqa_tt(self, th, v_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        return  self._rqa_meas(th, v_min, self.rqa_v_freq_dist,
                               self._rqa_lv_dist_min(th, v_min, self.rqa_v_freq_dist, ret_sum = 1),
                               self.tt)

    def _rqa_lv_max(self, th, freq_dist, measure_dict, offset):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return measure_dict[str(th)]
        except KeyError:
            d = freq_dist(th)
            n = np_hstack((1,np_array(d.values())))
            l = np_hstack((0,np_array(map(int, d.keys()))))
            measure_dict[str(th)] = np_sort(l*(n>0).astype(int))[-offset] #[-2] to avoid considering diagonal line

            return measure_dict[str(th)]

    def rqa_l_max(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        return self._rqa_lv_max(th, self.rqa_l_freq_dist, self.l_max, 2)

    def rqa_v_max(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        return self._rqa_lv_max(th, self.rqa_v_freq_dist, self.v_max, 1)

    def rqa_div(self, th):
        try:
            self.rplot
        except AttributeError:
            return -1

        return 1.0/float(self.rqa_l_max(th))

    def rqa_entr(self, th, l_min):
        try:
            self.rplot
        except AttributeError:
            return -1

        try:
            return self.entr[str(th)][str(l_min)]
        except KeyError:
            try:
                self.entr[str(th)]
            except KeyError:
                self.entr[str(th)] = {}

            l,p = self._rqa_lv_dist_min(th, l_min, self.rqa_l_freq_dist, ret_sum = 0)
            pp = p/np_sum(p)
            self.entr[str(th)][str(l_min)] = -pp.dot(np_log(pp))

            return self.entr[str(th)][str(l_min)]


