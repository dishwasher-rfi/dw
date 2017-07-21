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


#import numpy as np
#from scipy.ndimage import median_filter
from guiqwt.plot import ImageDialog
from guiqwt.tools import (AnnotatedRectangleTool)
from guiqwt.builder import make
from guiqwt.styles import style_generator

import guidata
_app = guidata.qapplication()

STYLE = style_generator()

def customize_shape(sh):
    param = sh.shape.shapeparam
#    param.line.color="#000000"
#    param.sel_line.color="#000000"
    param.fill.color="#000000"
    param.fill.alpha=0.7
    param.sel_fill.color="#000000"
    param.sel_fill.alpha=0.5

#    update_style_attr(style, param)

    param.update_shape(sh.shape)
    sh.shape.plot()


def data_view(data, ofa, data_title):
    win = ImageDialog(edit=True, toolbar=True, wintitle="DW viewer",
                      options=dict(show_contrast=False, xlabel='Channel',
                                   xunit='#', ylabel='time',show_xsection=True,
                                   show_ysection=True))
#    win.add_tool(AnnotatedRectangleTool)
#    win.add_tool(ReverseYAxisTool)


#    win.add_tool(AnnotatedRectangleTool, title="Flag",
#                 switch_to_default_tool=False,
#                 handle_final_shape_cb=customize_shape)
  #  win.add_tool(VCursorTool)
 #   sst=win.add_tool(SignalStatsTool)
#    SignalStatsTool.activate(sst)

    xcs=win.panels['x_cross_section']
    xcs.cs_plot.curveparam.curvestyle='Steps'
    xcs.cs_plot.perimage_mode=False
    ycs=win.panels['y_cross_section']
    ycs.cs_plot.curveparam.curvestyle='Steps'
    ycs.cs_plot.perimage_mode=False


    item_data = make.image(data, title = data_title)
    item_data.interpolate=(0,)

    item_ofa = make.image(ofa, title = 'Overflow')
    item_ofa.interpolate=(0,)
    item_ofa.imageparam.alpha_mask=True

    plot = win.get_plot()
    plot.add_item(item_data)
    plot.add_item(item_ofa)
#    plot.add_item(itemFlag)
    win.show()
    if win.exec_():
#        return plot.items
        return win





