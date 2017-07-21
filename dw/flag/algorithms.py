# Copyright (C) 2014 - IRA-INAF
#
# Author: Federico Cantini <cantini@ira.inaf.it>
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

from sys import path
# Set to absolute path for development
path.append("/home/federico/Documents/IRA-INAF/dw/pyLibdw")

class FlagAlgorithm(object):
    def __init__(self, data_matrix, flag_matrix):
        self.set_data(data_matrix)
        self.set_flag(flag_matrix)
        
    def set_data(self,data_matrix):
        self._data = data_matrix
        
    def set_flag(self,data_flag):
        self._flag = data_flag
    
    @classmethod
    def get_implementations(cls):
        return cls.__subclasses__()
    
    def compute(self):
        pass

    
###############################################################################
###############################################################################
class MeanOutFlagAlg(FlagAlgorithm):#Flags data>threshold times the MEAN value
    def __init__(self, data_matrix, flag_matrix, threshold):
        super(MeanOutFlagAlg, self).__init__(data_matrix, flag_matrix)
        self.setThreshold(threshold)
        
    def set_threshold(self,threshold):
        self._th = threshold
       
    def compute(self):
        a = MeanOutFlagAlgC(self._data, self._flag, self._th)
        a.compute()
 
       
###############################################################################
class MeanOutFlagAlgC(MeanOutFlagAlg): # C implementation
    def __init__(self, data_matrix, flag_matrix, threshold):
        super(MeanOutFlagAlgC, self).__init__(data_matrix, flag_matrix, 
                                              threshold)
        
    def compute(self):
        print("mean C")
        print self._data
        self._data[0] = 0
        print self._data
        pass #call to C function via pyLibdw wrapper

        
###############################################################################
class MeanOutFlagAlgPy(MeanOutFlagAlg): # Python implementation
    def __init__(self, data_matrix, flag_matrix, threshold):
        super(MeanOutFlagAlgC, self).__init__(self, data_matrix, flag_matrix, 
                                              threshold)
        
    def compute(self):
        print("mean python")
        pass #Pyhton implementation        
###############################################################################
###############################################################################




