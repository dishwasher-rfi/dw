# This file is part of
#
# Dish Washer - RFI cleaning tool for single dish radiotelescopes data
#
# Copyright (C) 2014 - IRA-INAF
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
dw.gui.widgets
================

Implement widgets to visualize and manipulate the data

Functions
---------
* mu_range: Return the axis limits while changing measure unit
* flag_mu_toggle: Set the values of the flagging tools to proper measure units
* flag_image_mu_toggle: Set the values of the flagging image matrices to proper measure units
* nearest_coors: Return nearest channel and sample to the input coordinate
* rect_flag_shape: Set the properties of the rectangle flagging tool
* is_flag: Return 1 if the item is a flagging one
* is_flag_image: Return 1 if the item is a flagging matrix image
* get_ordered_rect: Return ordered item rect


Classes
-------
* MainWidget:
* ImageParam:
* TableListWithProperties:
"""

from os.path import basename, dirname
from numpy import array as np_array
from numpy import abs as np_abs
from numpy import round as np_round
from numpy import floor as np_floor
from numpy import ceil as np_ceil
from numpy import transpose as np_transpose
from numpy import median as np_median
from numpy import sqrt as np_sqrt
from numpy import mean as np_mean
from numpy import divide as np_divide

from guidata.qt.QtGui import QWidget, QMessageBox, QSplitter, QListWidget, QPushButton, QVBoxLayout, QGridLayout, QColor
from guidata.qt.QtCore import (QSize, QT_VERSION_STR, PYQT_VERSION_STR, Qt, QVariant)
from guidata.qt.compat import getopenfilename, getopenfilenames
from guidata.dataset.datatypes import DataSet, GetAttrProp
from guidata.dataset.dataitems import (IntItem, FloatArrayItem, StringItem, ChoiceItem)
from guidata.dataset.qtwidgets import DataSetEditGroupBox, DataSetShowGroupBox, DataSetEditLayout

from guidata.dataset.dataitems import MultipleChoiceItem, ChoiceItem, FloatItem, TextItem
from guidata.dataset.datatypes import FuncProp

from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.utils import update_dataset
from guidata.py3compat import to_text_string

from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, ValueProp
from guidata.dataset.dataitems import BoolItem, FloatItem

from guiqwt.config import _
from guiqwt.plot import ImageWidget
from guiqwt.plot import ImageDialog
from guiqwt.image import ImagePlot
from guiqwt.curve import PlotItemList, CurvePlot, GridItem
from guiqwt.histogram import ContrastAdjustment
from guiqwt.plot import PlotManager
from guiqwt.builder import make
#from guiqwt.signals import SIG_LUT_CHANGED
#from guiqwt.signals import SIG_ITEM_MOVED
#from guiqwt.signals import SIG_MARKER_CHANGED
#from guiqwt.signals import SIG_AXES_CHANGED
#from guiqwt.signals import SIG_RANGE_CHANGED
#from guiqwt.signals import SIG_ACTIVE_ITEM_CHANGED
#from guiqwt.signals import SIG_ITEM_SELECTION_CHANGED
#from guiqwt.signals import SIG_ANNOTATION_CHANGED
#from guiqwt.signals import SIG_ITEMS_CHANGED

from guiqwt.cross_section import CrossSectionItem

from guiqwt.image import XYImageItem

from guiqwt.shapes import XRangeSelection
from guiqwt.tools import AnnotatedRectangle, AnnotatedRectangleTool, ColormapTool
from guiqwt.tools import ItemListPanelTool, ReverseYAxisTool, AspectRatioTool
from guiqwt.tools import XCSPanelTool, YCSPanelTool, CrossSectionTool, AverageCrossSectionTool
from guiqwt.tools import AnnotatedPointTool, HRangeTool, ContrastPanelTool, VCursorTool, HCursorTool, BaseCursorTool, RectangleTool

import dw.gui.prefs as prefs
from dw.flag.rfi_dect_func import id_dict
import recurrence
import math

def mu_range(limits,kx,ky):
    """Return the axis limits while changing measure unit

    limits: tuple containing axis limits (xmin, xmax, ymin, ymax)
    kx: x axes conversion factor (float)
    ky: y axes conversion factor (float)
    """
    return (limits[0]*kx, limits[1]*kx, limits[2]*ky, limits[3]*ky)

def flag_mu_toggle(plot_items,to_phys, X, Y):
    """Set the values of the flagging tools to proper measure units

    plot_items: guiqwt.plot.items list element
    to_phys: True (switching to physical mu)
    X: Frequancy array
    Y: Time array
    """
    for item in plot_items:
        if type(item) is AnnotatedRectangle:
            t = get_ordered_rect(item)
            if to_phys:
                xmin = X[np_floor(t[0])]
                ymin = Y[np_floor(t[1])]
                xmax = X[np_ceil(t[2])]
                ymax = Y[np_ceil(t[3])]
            else:
                xmin = (np_abs(X-t[0])).argmin()
                ymin = (np_abs(Y-t[1])).argmin()
                xmax = (np_abs(X-t[2])).argmin()
                ymax = (np_abs(Y-t[3])).argmin()
            item.set_rect(xmin, ymin, xmax, ymax)

        if type(item) is XRangeSelection:
            t = item.get_range()
            if to_phys:
                (xmin, xmax) = X[[np_round(t[0]), np_round(t[1])]]
            else:
                xmin = (np_abs(X-t[0])).argmin()
                xmax = (np_abs(X-t[1])).argmin()

            item.set_range(xmin, xmax)
    return 0

def flag_image_mu_toggle(items, X, Y):
    """Set the values of the flagging image matrices to proper measure units

    items: guiqwt.plot.items list element
    """
    for item in items:
        item.set_xy(X,Y)

    return 0

def nearest_coord(x, y, x_array, y_array):
    """Return nearest channel and sample to the input coordinate

    x: x value
    y: y value
    x_array: array of the allowed x values
    y_array: array of the allowed y values
    """
    idx=(np_abs(x_array-x)).argmin()
    idy=(np_abs(y_array-y)).argmin()

    return (x_array[idx], y_array[idy])

def floor_coord(x, x_array):
    """Return nearest lower channel and sample to the input coordinate

    x: x value
    x_array: array of the allowed x values
    """
    dx = x_array-x
    idx = dx[dx<=0].argmax()

    return x_array[idx]

def ceil_coord(x, x_array):
    """Return nearest higher channel and sample to the input coordinate

    x: x value
    x_array: array of the allowed x values
    """
    if (x>x_array[-1]):
        return nearest_coord(x, x, x_array, x_array)[0]
    else:
        dx = x_array-x
        idx = dx.size-dx[dx>=0].size
        return x_array[idx]

def rect_flag_shape(sh):
    """Set the properties of the rectangle flagging tool

    sh: guiqwt.annotations.AnnotatedRectangle
    """
    param = sh.shape.shapeparam
    param.fill.color="#000000"
    param.fill.alpha=0.7
    param.sel_fill.color="#000000"
    param.sel_fill.alpha=0.5
    param.update_shape(sh.shape)
    sh.shape.plot()

def is_flag(item):
    """Return 1 if the item is a flagging one

    item: plot item
    """
    try:
        item.autoflag
        if item.autoflag == True:
            return 1
    except AttributeError:
        pass

    if type(item) == AnnotatedRectangle or type(item) == XRangeSelection:
        return 1
    else:
        return 0

def is_flag_image(item):
    """Return 1 if the item is a flagging matrix image

    item: plot item
    """
    try:
        item.dw_k_flagset
    except AttributeError:
        return 0

    return 1

def get_ordered_rect(item, ylimits=(0.0,0.0)):
    """Return ordered item rect"""
    if type(item) == AnnotatedRectangle:
        x1, y1, x2, y2 = item.get_rect()

        minx = min(x1, x2)
        miny = min(y1, y2)
        maxx = max(x1, x2)
        maxy = max(y1, y2)
    elif type(item) == XRangeSelection:
        x1, x2 = item.get_range()

        minx = min(x1, x2)
        maxx = max(x1, x2)
        maxy, miny = ylimits
    return (minx, miny, maxx, maxy)

class ImageParam(DataSet):

    """Implement the data structure for the metadata/properties panel"""

    _hide_data = False
    _hide_size = True
#    title = StringItem(_("Dataset"),
#                       default=_("Untitled"))

    bandwidth = FloatItem("Bw",
                          default=0,
#                          min=0,
#                          max=800,
                          unit="MHz",
                          help="Bandwidth")

    name = StringItem(_("Source"),
                      default=_("Untitled"),
                      help="Source name")

#    track = StringItem(_("Track"),
#                      default=_("No"),
#                      help="Source tracking").set_pos(col=1)

    ut = StringItem(_("UT"),
                  default=None,
                  help="Universal Time")

    ra = FloatItem(_("RA"),
                  default=0,
#                  min=0,
#                  max=8000,
                  unit="deg",
                  help="Rigth Ascension")

    dec = FloatItem(_("dec"),
                      default=0,
#                      min=0,
#                      max=8000,
                      unit="deg",
                      help="Declination")#.set_pos(col=1)

    azimuth = FloatItem(_("Az"),
                          default=0,
#                          min=0,
#                          max=8000,
                          unit="deg",
                          help="Azimuth")

    elevation = FloatItem(_("El"),
                          default=0,
#                          min=0,
#                          max=8000,
                          unit="deg",
                          help="Elevation")#.set_pos(col=1)

#    bool2 = BoolItem("", "Tracking")

#    data = FloatArrayItem(_("Data")).set_prop("display",
#                                              hide=GetAttrProp("_hide_data"))
#    width = IntItem(_("Width"), help=_("Image width (pixels)"), min=1,
#                    default=100).set_prop("display",
#                                          hide=GetAttrProp("_hide_size"))
#    height = IntItem(_("Height"), help=_("Image height (pixels)"), min=1,
#                     default=100).set_prop("display",
#                                           hide=GetAttrProp("_hide_size"))

    flag_meta = TextItem(_("Flag metadata"))

class TableListWithProperties(QSplitter):

    """Implement the side panel with data tables list and metadata/properties panel

    Methods
    -------
    __init__: instantiate the side panel
    """

    def __init__(self, parent):
        """Instantiate the side panel

        parent: QMainWindow
        """
        QSplitter.__init__(self, parent)
        self.setOrientation(Qt.Vertical)

        self.tablelist = QListWidget(self)
        self.addWidget(self.tablelist)

        self.properties = DataSetEditGroupBox(_("Metadata"), ImageParam, show_button = False)
        self.properties.setEnabled(False)
        self.addWidget(self.properties)

#        self.meta = QListWidget(self)
#        self.addWidget(self.meta
#        )
class FreqOffWidget(DataSet):
    """
    Frequency offset
    """
    freq_off = FloatItem("Frequency offset",
                         default=0, min=0).set_prop("display", active=ValueProp(True))

    def __init__(self):
        super(FreqOffWidget, self).__init__()

class FlagWidget(DataSet):
    """
    Flag Widget
    <b>Flag Widget:</b>
    """
    prop1 = ValueProp(False)
    prop2 = ValueProp(False)

    channel_range = BeginGroup("Spectral channel range (channel number)")
    enable_channel = BoolItem("Enable channel range",
                       help="If disabled, the following parameters will be ignored",
                       default=True).set_prop("display", store=prop1)
    channel_start = FloatItem("Channel start",
                         default=0, min=0).set_prop("display", active=prop1)
    channel_stop = FloatItem("Channel stop",
                         default=0).set_prop("display", active=prop1)
    _channel_range = EndGroup("Spectral channel range (channel number)")
    sample_range = BeginGroup("Time sample range (sample number)")
    enable_sample = BoolItem("Enable sample range",
                       help="If disabled, the following parameters will be ignored",
                       default=True).set_prop("display", store=prop2)
    sample_start = FloatItem("Sample start",
                         default=0, min=0).set_prop("display", active=prop2)
    sample_stop = FloatItem("Sample stop",
                         default=0).set_prop("display", active=prop2)
    _sample_range = EndGroup("Time sample range (sample number)")

    def __init__(self, sample_start, sample_stop, channel_start, channel_stop):
        super(FlagWidget, self).__init__()
        self.channel_start = channel_start
        self.channel_stop = channel_stop
        self.sample_start = sample_start
        self.sample_stop = sample_stop

    def get_widget_rect(self):
        """"""
        xmin = self.sample_start
        ymin = self.channel_start
        xmax = self.sample_stop
        ymax = self.channel_stop


        return xmin, ymin,xmax, ymax, self.enable_sample, self.enable_channel

class AlgSelectionWidget(DataSet):
    """
    RFI detection algorithm selection
    """
    _prop = GetAttrProp("choice")
    choice = ChoiceItem('Algorithm', [("-- Select Algorithm --", "-- Select Algorithm --")], default="-- Select Algorithm --").set_prop("display", store=_prop)

    def __init__(self, rfi_alg_dict):
        super(AlgSelectionWidget, self).__init__()

        choices = []
        for key in rfi_alg_dict.keys():
            choices.append((key, rfi_alg_dict[key]['name'], None))

        self._items[0].__dict__['_props']['data']['choices'] = choices

class AlgParamWidget(DataSet):
    """
    RFI algorithm parameter selection
    ________\tL\t\tR\t\tQ\t\tU
    mean\t:\t{:.2E}\t{:.2E}\t{:.2E}\t{:.2E}
    median\t:\t{:.2E}\t{:.2E}\t{:.2E}\t{:.2E}
    rms\t:\t{:.2E}\t{:.2E}\t{:.2E}\t{:.2E}
    """
    def __init__(self, dw_data, row):
        ret = self.info_values(dw_data, row)
        docstring = self.__doc__.format(ret[0][0], ret[1][0], ret[2][0], ret[3][0],
                                            ret[0][1], ret[1][1], ret[2][1], ret[3][1],
                                            ret[0][2], ret[1][2], ret[2][2], ret[3][2])
        setattr(self, '__doc__', docstring)
        super(AlgParamWidget, self).__init__()
        params = dw_data.auto_flag_get_params()
        self.dparams = dw_data.selected_dect_alg.get_def_params()

        del self._items[:]

        for param in params.keys():
            if type(params[param]) == int:
                self._items.append(IntItem(param, default = params[param], slider = False))

            if type(params[param]) == float:
                self._items.append(FloatItem(param, default = params[param], slider = False))

            if type(params[param]) == tuple:
                if type(params[param][0]) == int:
                    self._items.append(IntItem(param, default = params[param][0], min = params[param][1], max = params[param][2], slider = False))
                if type(params[param][0]) == float:
                    self._items.append(IntItem(param, default = params[param][0], min = params[param][1], max = params[param][2], slider = False))

            self._items[-1].set_name(param)

    def info_values(self, dw_data, row):
        datas = dw_data.dw_io.get_data(dw_data.datasets[row].th)
        integr = dw_data.dw_io.get_integration(dw_data.datasets[row].th)[0]
        ret = []
        for i in datas:
            M = np_divide(np_mean(i[i>10]), integr)
            m = np_divide(np_median(i[i>10]), integr)
            r = np_divide(np_sqrt(((i[i>10] - m)**2).mean()), integr)
            ret.append((M, m, r))
        return ret

    def get_params(self):
        par_dict = {}
        for item in self._items:
            dparam = self.dparams[item._name]
            if type(dparam) == tuple:
                par_dict[item._name] = (eval("self._"+item._name), dparam[1], dparam[2])
            else:
                par_dict[item._name] = eval("self._"+item._name)

        return par_dict

class AlgOutWidget(DataSet):
    """
    RFI algorithm output selection
    """
    def __init__(self, dw_data):
        super(AlgOutWidget, self).__init__()
        out_avail, out_dict = dw_data.auto_flag_get_out()
        del self._items[:]
        for out_option in out_avail:
            self._items.append(BoolItem(out_option, default = out_dict[out_option]))
            self._items[-1].set_name(out_option)

    def get_out(self):
        out_options = []
        for item in self._items:
            if eval("self._"+item._name):
                out_options.append(item._name)

        return out_options

class PropagWidget(DataSet):
    """
    Flag propagation widget
    """
    _prop = GetAttrProp("choice")
    choice = MultipleChoiceItem('Feeds', []).set_prop("display", store=_prop).horizontal(2)

    def __init__(self, dw_data, cf):
        super(PropagWidget, self).__init__()

        feeds = list(set([str(i.feed_section[0]) for i in dw_data.datasets]))
        self.nfeeds = len(feeds)
        choices = []
        for feed in feeds:
            if feed != str(cf):
                choices.append((feed, feed, None))

        self._items[0].__dict__['_props']['data']['choices'] = choices

class MainWidget(QSplitter):

    """Implement the main widget to visualize and manipulate the data

    Methods
    -------
    * __init__: instantiate and setup the main widget
    * set_data_ref: add a reference to data in MainWidget
    * register_tools: add tools to the toolbar
    * setup_lut_ranges: create a list of 'None' look up table ranges
    * open_setup: update proper attributes at file opening
    * refresh_list: refresh the list of datasets
    * log_toggle: toggle logaritmic scale on/off in the x cross section plot
    * mu_toggle: toggle physical measure units on/off on the main plot and cross section plots
    * grid_toggle: toggle grid on/off in the main plot
    * item_list: toggle item list panel on/off
    * contrast_panel_toggle(self): toggle contrast panel on/off
    * current_table_changed: update the plot as the selected dataset changes
    * lut_range_changed: select the look up table of the selected dataset
    * sig_marker_changed: call method on marker changed
    * upd_cs_marker: Update markers in the cross sections plots
    * upd_metadata: Update 'per sample' metadata in metadata panel
    * get_flag_items: Return all the flagging items
    * get_selected_flag_items: Return selcted flag items
    * get_checked_flag_items: Return checked flag items
    * get_flag_image_items: Return flagging matrix image items
    * get_checked_flag_image_items: Return checked flagging matrix image items
    * get_selected_flag_image_items: Return selected flagging matrix image items
    * upd_flag_items: Call method to lock selected flag items or new one to channels and samples
    * lock_rectangle: Lock rectangle flag shape item to the nearest channel and sample
    * lock_range: Lock range flag shape item to the nearest channel
    * lock_shape: Lock flag shape item to the nearest channel and sample
    * get_current_axes_scales: Return the values of axes scales in the current measure unit
    * show_data: plot the selected dataset
    * checked_items_to_flag: Create a new flag matrix from plot selected flag items
    * show_flagging_sets: Retrieve flagging sets data for the selected dataset
    * del_selected_flag_image_items: Delete flagging sets from data file
    * merge_selected_flag_image_items: Merge two or more flagging sets
    * deflag_selected_flag_image_items: Deflag previously flagged areas on axsisting flagsets
    * flag_widget: Run a FlagWidget instance to set a flag area
    * freq_off_action: Set the offset of the frequency scale
    """

    def __init__(self, parent, toolbar, icon_path):
        """Instantiate and setup the main widget

        parent: MainWindow
        toolbar: PyQt4.QtGui.QToolBar
        """
        QSplitter.__init__(self, parent)
        self.icon_path = icon_path
        self.data_ref = None
        self.mir_x = False
        self.flag_meta = None
        self.axes_phys_unit = prefs.AXES_PHYS_UNIT
        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(Qt.Horizontal)

        tablelistwithproperties = TableListWithProperties(self)
        self.addWidget(tablelistwithproperties)
        self.tablelist = tablelistwithproperties.tablelist
        self.tablelist.man_current = self.tablelist.currentRow()
        self.mem_dict = {}
        self.flag_button = QPushButton("Flag")
        self.image = ImageParam()
        self.tablelist.currentRowChanged.connect(self.current_table_changed)

        self.properties = tablelistwithproperties.properties

        self.imagewidget = ImageWidget(self, show_contrast=True,
                                       show_itemlist=True, show_xsection=True,
                                       show_ysection=True, xsection_pos=prefs.X_SECTION_POS,
                                       ysection_pos=prefs.Y_SECTION_POS, #xlabel=('MHz'), ylabel=('s')
                                       panels=[])
        self.imagewidget.plot.cross_marker.label_cb = self.imagewidget.plot.get_coordinates_str
        self.imagewidget.panels['x_cross_section'].cs_plot.curveparam.curvestyle = 'Steps'
        self.imagewidget.panels['y_cross_section'].cs_plot.curveparam.curvestyle = 'Steps'

        self.imagewidget.panels['x_cross_section'].cs_plot.toggle_apply_lut(False)
        self.imagewidget.panels['y_cross_section'].cs_plot.toggle_apply_lut(False)

        self.imagewidget.panels['x_cross_section'].cs_plot.toggle_autoscale(False)
        self.imagewidget.panels['y_cross_section'].cs_plot.toggle_autoscale(False)

#        self.imagewidget.panels['x_cross_section'].cs_plot.single_source = True
#        self.imagewidget.panels['y_cross_section'].cs_plot.single_source = True

        self.imagewidget.plot.SIG_LUT_CHANGED.connect(self.lut_range_changed)

        self.imagewidget.plot.SIG_MARKER_CHANGED.connect(self.sig_marker_changed)

        self.imagewidget.plot.SIG_ANNOTATION_CHANGED.connect(self.upd_flag_items)

        self.imagewidget.plot.SIG_ITEMS_CHANGED.connect(self.item_notsaved)

        self.imagewidget.plot.SIG_ITEM_SELECTION_CHANGED.connect(self.item_selection_changed)

        self.imagewidget.plot.SIG_ITEM_REMOVED.connect(self.item_notsaved)

#        self.imagewidget.plot.SIG_ACTIVE_ITEM_CHANGED.connect(self.active_item_changed)

#        self.imagewidget.plot.SIG_RANGE_CHANGED.connect(self.upd_flag_items)

        self.item = None # image item

        self.current_pola = 'L'

        self.imagewidget.add_toolbar(toolbar, "default")
        self.register_tools(toolbar)
        self.addWidget(self.imagewidget)

        self.imagewidget.panels['x_cross_section'].toolbar.hide()
        self.imagewidget.panels['y_cross_section'].toolbar.hide()

        self.lut_ranges = [] # List of LUT ranges

        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([1, 2])

    def set_data_ref(self, data_ref):
        """Add a reference to data in MainWidget

        data_ref: dw.core.data_def.DWData
        """
        self.data_ref = data_ref

    def register_tools(self, toolbar):
        """Add tools to the toolbar

        toolbar: PyQt4.QtGui.QToolBar
        """
#        self.imagewidget.register_all_image_tools()
        self.imagewidget.add_separator_tool()
        self.imagewidget.register_standard_tools()
        self.imagewidget.add_separator_tool()
        self.imagewidget.add_tool(ColormapTool)
        self.imagewidget.add_tool(ContrastPanelTool)
        self.imagewidget.add_tool(ItemListPanelTool)
        self.imagewidget.add_tool(ReverseYAxisTool)
        self.imagewidget.add_tool(AspectRatioTool)

        self.imagewidget.add_tool(XCSPanelTool)
        self.imagewidget.add_tool(YCSPanelTool)
        self.imagewidget.add_tool(CrossSectionTool)
        self.imagewidget.add_tool(AverageCrossSectionTool)
#        self.imagewidget.add_tool(ImageStatsTool)
        self.imagewidget.add_separator_tool()
#        self.imagewidget.add_tool(HCursorTool,
#                                  title="Sample Flagging")
#        self.imagewidget.add_tool(VCursorTool,
#                                  title="Channel Flagging")
        self.imagewidget.add_tool(HRangeTool,
                                  title="Channels Range Flagging")
        self.imagewidget.add_tool(AnnotatedRectangleTool,
                                  title="Flag",
                                  switch_to_default_tool=False,
                                  handle_final_shape_cb=rect_flag_shape)
#        self.imagewidget.add_tool(AnnotatedPointTool,
#                                  title="Point Flagging")
#        flag_selected =  create_action(self, _("Flag checked"),
#                                       tip=_("Flag checked items"),
#                                       triggered=self.checked_items_to_flag)
#        get_flag_sets =  create_action(self, _("Get flag sets"),
#                                       tip=_("Get flag set"),
#                                       triggered=self.show_flagging_sets)
#
#        add_actions(toolbar, [flag_selected])
        self.imagewidget.add_separator_tool()

        item_list = create_action(self, _("Item list..."),
                                  icon=get_icon('item_list.png'),
                                  tip=_("Item list manager"),
                                  triggered=self.item_list)
        contrast_toggle = create_action(self, _("Grid toggle..."),
                                        icon=get_icon('contrast.png'),
                                        tip=_("Toggles contrast panel on and off"),
                                        triggered=self.contrast_panel_toggle)
        grid_toggle = create_action(self, _("Grid toggle..."),
                                    icon=get_icon(self.icon_path+'grid_toggle.png'),
                                    tip=_("Toggles grid on and off"),
                                    triggered=self.grid_toggle)
        mu_toggle = create_action(self, _("Measure Units toggle..."),
                                  icon=get_icon(self.icon_path+'mesure.png'),
                                  tip=_("Toggles measure units"),
                                  triggered=self.mu_toggle)
        log_toggle = create_action(self, _("Y scale toggle..."),
                                   icon=get_icon(self.icon_path+'scale.png'),
                                   tip=_("Toggles y scale"),
                                   triggered=self.log_toggle)
        mir_x = create_action(self, _("Mirror X axis..."), # icon=get_icon('axes.png'),
                              tip=_("Mirror X"),
                              triggered=self.mir_x_toggle)

        add_actions(toolbar, [item_list, contrast_toggle, grid_toggle,
                              mu_toggle, log_toggle])#, mir_x])

    def setup_lut_ranges(self):
        """Create a list of 'None' look up table ranges"""
        self.lut_ranges = []
        for t in self.data_ref.datasets: #TODO: add getter in data_def to avoid direct access to data structure
            self.lut_ranges.append(None)

    def open_setup(self, data_ref):
        """Update proper attributes at file opening

        data_ref: dw.core.data_def.DWData
        """
        self.set_data_ref(data_ref)
        self.setup_lut_ranges()
        self.refresh_list()
        self.tablelist.setCurrentRow(0)

    def refresh_list(self):
        """Refresh the list of datasets"""
        self.tablelist.clear()
        if self.data_ref.correction == True:
            c = '*'
        else:
            c = ''
        self.tablelist.addItems([c+to_text_string(t.t) for t in self.data_ref.datasets])#TODO: add getter in data_def to avoid direct access to data structure

    def log_toggle(self):
        """Toggle logaritmic scale on/off in the x cross section plot"""
        xcs = self.imagewidget.panels['x_cross_section']
        if xcs.cs_plot.get_axis_scale(0) == 'lin':
            xcs.cs_plot.set_axis_scale(0, 'log')
        else:
            xcs.cs_plot.set_axis_scale(0, 'lin')
        xcs.cs_plot.replot()

    def mu_toggle(self):
        """Toggle physical measure units on/off on the main plot and cross section plots"""
        plot = self.imagewidget.plot
        self.axes_phys_unit = not self.axes_phys_unit
        to_phys_units = self.axes_phys_unit
        row = self.tablelist.currentRow()
        x = self.data_ref.get_freq_scale(row)
        y = self.data_ref.get_time_scale(row)
        limits = plot.get_plot_limits()
        if self.item is not None:
            if to_phys_units:
                self.item.set_xy(x,y)
                flag_image_mu_toggle(self.get_flag_image_items(), x, y)

                x_min = x[np_round(limits[0])]
                y_min = y[np_round(limits[2])]
                x_max = x[np_round(limits[1])]
                y_max = y[np_round(limits[3])]

                self.imagewidget.plot.set_titles(xlabel='MHz',
                                                 ylabel='Seconds')
                flag_mu_toggle(plot.items, True, x, y)
            else:
                self.item.set_xy(np_array(range(len(x))),np_array(range(len(y))))
                flag_image_mu_toggle(self.get_flag_image_items(),
                                     np_array(range(len(x))),
                                     np_array(range(len(y))))

                x_min = (np_abs(x-limits[0])).argmin()
                y_min = (np_abs(y-limits[2])).argmin()
                x_max = (np_abs(x-limits[1])).argmin()
                y_max = (np_abs(y-limits[3])).argmin()

                self.imagewidget.plot.set_titles(xlabel='Channels',
                                                 ylabel='Samples')
                flag_mu_toggle(plot.items, False, x, y)
            plot.set_plot_limits(x_min, x_max, y_min, y_max)
            plot.replot()
        else:
            pass

    def grid_toggle(self):
        """Toggle grid on/off in the main plot"""
        self.imagewidget.plot.grid.set_selectable(True)
        if self.imagewidget.plot.grid.isVisible():
           self.imagewidget.plot.grid.hide()
        else:
           self.imagewidget.plot.grid.show()
        self.imagewidget.plot.replot()

    def mir_x_toggle(self):
        self.mir_x = not self.mir_x

        row = self.tablelist.currentRow()
        self.current_table_changed(row)

    def item_list(self):
        """Toggle item list panel on/off"""
        if self.imagewidget.get_itemlist_panel().isVisible():
           self.imagewidget.get_itemlist_panel().hide()
        else:
           self.imagewidget.get_itemlist_panel().show()
           self.imagewidget.get_itemlist_panel().update()

    def contrast_panel_toggle(self):
        """Toggle contrast panel on/off"""
        if self.imagewidget.get_contrast_panel().isVisible():
           self.imagewidget.get_contrast_panel().hide()
        else:
           self.imagewidget.get_contrast_panel().show()
           self.imagewidget.get_contrast_panel().update()

    def get_items_status(self):
        """Get and save the selection status of the items in the last dataset"""
        il = []
        for n, i in enumerate(self.imagewidget.plot.get_items(z_sorted=True)):
            t = (n, i)
            il.append(t)
        self.mem_dict[self.tablelist.man_current] = il

    def set_items_status(self, row):
        """Set the previous state of items in the current dataset"""
        plot = self.imagewidget.plot
        for item_tup in reversed(self.mem_dict[row]):
            item = item_tup[1]
            plot.add_item(item)

    def current_table_changed(self, row):
        """Update the plot as the selected dataset changes"""
        self.imagewidget.plot.del_items(self.get_items_nogrid())
        self.image.title = self.tablelist.item(row).text()
        self.image.bandwidth = self.data_ref.get_bandwidth(row)
        self.image.data = self.data_ref.dataset2np_array(row)
        self.image.a_ut = self.data_ref.get_ut(row)[0]
        self.image.a_ascension = math.degrees(self.data_ref.get_ascension(row)[0])
        self.image.a_declination = math.degrees(self.data_ref.get_declination(row)[0])
        self.image.a_azimuth = math.degrees(self.data_ref.get_azimuth(row)[0])
        self.image.a_elevation = math.degrees(self.data_ref.get_elevation(row)[0])
        self.image.a_source = self.data_ref.get_source(row)[0]
        self.image.a_on_track = self.data_ref.get_on_track(row)[0]
        try:
            self.image.height, self.image.width = self.image.data[0].shape
        except:
            self.image.height, self.image.width = self.image.data.shape
        update_dataset(self.properties.dataset, self.image)
        self.properties.get()
        self.properties.setEnabled(True)
        if row in self.mem_dict:
            self.set_items_status(row)
        else:
            self.show_data(self.data_ref.get_freq_scale(row),
                           self.data_ref.get_time_scale(row),
                           self.image.data,
                           self.lut_ranges[row],
                        phys_units = self.axes_phys_unit)

            try:
                self.show_flagging_sets()
            except:
                pass
        self.tablelist.man_current = row
        self.imagewidget.itemlist.listwidget.items_changed(self.imagewidget.plot)
        self.item_notsaved()

    def get_items_nogrid(self):
        """Return all items except grid
        """
        items = []
        for item in self.imagewidget.plot.items:
            if type(item) != GridItem:
                items.append(item)

        return items

    def get_image_items(self):
        """Return flagging matrix image items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if type(item) == XYImageItem:
                items.append(item)

        return items

    def lut_range_changed(self):
        """Select the look up table of the selected dataset"""
        row = self.tablelist.currentRow()
        self.lut_ranges[row] = self.item.get_lut_range()

    def sig_marker_changed(self):
        """Call methods on marker changed"""
        self.upd_cs_marker()
        self.upd_metadata()

    def upd_cs_marker(self):
        """Update markers in the cross sections plots"""
        x,y = self.imagewidget.plot.cross_marker.get_pos()
        ysmin,ysmax = self.imagewidget.plot.get_axis_limits(0) #Y
#        print(self.imagewidget.plot.get_axis_limits(1)) #Z
        xsmin,xsmax = self.imagewidget.plot.get_axis_limits(2) #X

        self.imagewidget.panels['x_cross_section'].cs_plot.cross_marker.set_pos(x=x)
        self.imagewidget.panels['x_cross_section'].cs_plot.setAxisScale(1,xsmin,xsmax)
        self.imagewidget.panels['x_cross_section'].cs_plot.cross_marker.update_label()

        self.imagewidget.panels['y_cross_section'].cs_plot.cross_marker.set_pos(y=y)
        self.imagewidget.panels['y_cross_section'].cs_plot.setAxisScale(1,ysmin,ysmax)
        self.imagewidget.panels['y_cross_section'].cs_plot.cross_marker.update_label()

        self.imagewidget.panels['x_cross_section'].cs_plot.cross_marker.show()
        self.imagewidget.panels['y_cross_section'].cs_plot.cross_marker.show()

#        for cross_section in ['x_cross_section', 'y_cross_section']:
#            for item in self.imagewidget.panels[cross_section].cs_plot.get_items():
#                if issubclass(type(item), CrossSectionItem):
#                    print(type(item))
#                    item.setVisible(item.get_source_image().isVisible())
#            self.imagewidget.panels[cross_section].cs_plot.replot()
#    def items_changed(self):
#        self.lock_shape(self.imagewidget.plot.items[-1])
#        self.imagewidget.plot.items[-1].plot()
#        self.imagewidget.plot.replot()

    def upd_metadata(self):
        """Update 'per sample' metadata in metadata panel"""
        x,y = self.imagewidget.plot.cross_marker.get_pos()

        row = self.tablelist.currentRow()
        Y = self.data_ref.get_time_scale(row)
        if self.axes_phys_unit:
            if y < Y[0]:
                y = Y[0]
            if y > Y[-1]:
                y = Y[-1]
            y = (np_abs(Y-y)).argmin()
        else:
            y = int(np_abs(y))
            if y < 0:
                y = 0
            if y > Y.shape[0]:
                y = Y[-1]

        self.image.ut = self.image.a_ut[y]
        self.image.azimuth = self.image.a_azimuth[y]
        self.image.elevation = self.image.a_elevation[y]
        self.image.ra = self.image.a_ascension[y]
        self.image.dec = self.image.a_declination[y]
        self.image.name = self.image.a_source[y]
        self.image.flag_meta = self.flag_meta
        update_dataset(self.properties.dataset, self.image)
        self.properties.get()
        self.properties.setEnabled(True)

    def get_flag_items(self):
        """Return flag items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag(item):
                items.append(item)

        return items

    def get_selected_flag_items(self):
        """Return selected flag items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag(item) and item.selected:
                items.append(item)
        return items

    def get_checked_flag_items(self):
        """Return checked flag items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag(item) and item.isVisible():
                items.append(item)

        return items

    def get_flag_image_items(self):
        """Return flagging matrix image items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag_image(item):
                items.append(item)
        return items

    def get_checked_flag_image_items(self):
        """Return checked flagging matrix image items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag_image(item) and item.isVisible():
                items.append(item)

        return items

    def get_selected_flag_image_items(self):
        """Return selected flagging matrix image items
        """
        items = []
        for item in self.imagewidget.plot.items:
            if is_flag_image(item) and item.selected:
                items.append(item)

        return items

    def upd_flag_items(self):
        """Call method to lock selected flag items or new one to channels and
        samples.
        """
        items = self.get_selected_flag_items()
        try:
            last = [i for i in self.imagewidget.plot.items if is_flag(i) or is_flag_image(i)][-1]
            items.append(last)
        except:
            pass

        for item in items:
            if item.title().text() == 'Flag':
                try:
                    title, rif = self.gen_flag_name_rif(item)
                    item.setTitle(title)
                    item.feed = rif[0]
                    item.secton = rif[1]
                    item.pola = rif[2]
                except:
                    pass
            self.lock_shape(item)

        self.item_selection_changed()

    def lock_rectangle(self, item):
        """Lock rectangle flag shape item to the nearest channel and sample

        item: guiqwt.plot.items element
        """
        (X, Y) = self.get_current_axes_scales()
        (xmin, ymin, xmax, ymax) = item.get_rect()
        #(xmin, ymin) = nearest_coord(xmin, ymin, X, Y)
        xmin = floor_coord(xmin, X) #Problems moving rectangle
        ymin = floor_coord(ymin, Y)
        #(xmax, ymax) = nearest_coord(xmax, ymax, X, Y)
        xmax = ceil_coord(xmax, X)
        ymax = ceil_coord(ymax, Y)
        item.set_rect(xmin, ymin, xmax, ymax)

    def lock_range(self, item):
        """Lock range flag shape item to the nearest channel

        item: guiqwt.plot.items element
        """
        row = self.tablelist.currentRow()
        X = self.data_ref.get_freq_scale(row)
        if not self.axes_phys_unit:
            X = np_array(range(len(X)))

        (xmin, xmax) = item.get_range()
        xmin = floor_coord(xmin, X)
        xmax = ceil_coord(xmax, X)
        #(xmin, xmax) = nearest_coord(xmin, xmax, X, X)
        item.set_range(xmin, xmax)

    def lock_shape(self, item):#TODO see https://pythonhosted.org/guiqwt/_modules/guiqwt/image.html align_rectangular_shape
        """Lock flag shape item to the nearest channel and sample

        item: guiqwt.plot.items element
        """
        if type(item) is AnnotatedRectangle:
            self.lock_rectangle(item)
        if type(item) is XRangeSelection:
            self.lock_range(item)

    def gen_flag_name_rif(self, item):
        """Generate a name and a (feed, section, polarization) tuple for a flag

        item: guiqwt.plot.items element
        """
        row = self.tablelist.currentRow()
        feed = self.data_ref.datasets[row].feed_section[0]
        section = self.data_ref.datasets[row].feed_section[1]
        alg = id_dict['Manual']
        if type(item) == AnnotatedRectangle:
            pola = []
            for item in self.get_items_nogrid():
                if not is_flag(item) and not is_flag_image(item) and item.isVisible():
                    pola.append(item.title().text())
            name = 'Flag.({})_F{}S{}:{}'.format(alg, feed, section, pola[0])
        elif type(item) == XRangeSelection:
            name = 'Flag.({})_F{}S{}:{}'.format(alg, feed, section, pola[0])
        #elif type(item) == XYImageItem:
        #    name = 'Flag_F{}S{}'.format(feed, section)

        return name, (feed, section, pola[0])

    def get_current_axes_scales(self):
        """Return the values of axes scales in the current measure unit"""
        row = self.tablelist.currentRow()

        X = self.data_ref.get_freq_scale(row)
        Y = self.data_ref.get_time_scale(row)
        if not self.axes_phys_unit:
            X = np_array(range(len(X)))
            Y = np_array(range(len(Y)))

        return (X,Y)

    def show_data(self, x, y, data, lut_range=None, phys_units=prefs.AXES_PHYS_UNIT):
        """Plot the selected dataset

        x: 1D numpy array for the x axes values
        y: 1D numpy array for the y axes values
        data: 2D numpy array (time-frequency matrix)
        lut_range:
        phys_units: boolean (default=True)
        """
        if isinstance(data, list):
            title = ["L", "R"]
            if self.mir_x == True:
                for dat in data:
                    dat = dat.transpose()[::-1].transpose()

            plot = self.imagewidget.plot
            ii = 0
            for dat in data:
                if phys_units:
                    self.axes_phys_unit = True
                    self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_PHYSICS, ylabel=prefs.Y_LABEL_PHYSICS)
                    self.item = make.xyimage(x,y,dat,title=title[ii])
                    self.imagewidget.plot.lock_aspect_ratio = False
                else:
                    self.axes_phys_unit = False
                    self.item = make.xyimage(np_array(range(len(x))),np_array(range(len(y))),dat,title=title[ii])
                    self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_ARBITRARY, ylabel=prefs.Y_LABEL_ARBITRARY)
                self.item.interpolate=(0,)
                plot.add_item(self.item, z=-ii-2)
                ii = ii +1
                if ii != 0:
                    self.item.hide()
            plot.replot()
        else:
            title = "Data"
            if self.mir_x == True:
                data = data.transpose()[::-1].transpose()

            plot = self.imagewidget.plot
            if self.item is not None:
                self.item.set_data(data)
                if phys_units:
                    self.item.set_xy(x,y)
                else:
                    self.item.set_xy(np_array(range(len(x))),np_array(range(len(y))))
                if lut_range is None:
                    lut_range = self.item.get_lut_range()
                self.imagewidget.set_contrast_range(*lut_range)
                self.imagewidget.update_cross_sections()
            else:
                if phys_units:
                    self.axes_phys_unit = True
                    self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_PHYSICS, ylabel=prefs.Y_LABEL_PHYSICS)
                    self.item = make.xyimage(x,y,data,title=title)
                    self.imagewidget.plot.lock_aspect_ratio = False
                else:
                    self.axes_phys_unit = False
                    self.item = make.xyimage(np_array(range(len(x))),np_array(range(len(y))),data,title=title)
                    self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_ARBITRARY, ylabel=prefs.Y_LABEL_ARBITRARY)
                self.item.interpolate=(0,)
                plot.add_item(self.item, z=-2)
            plot.replot()

    def checked_items_to_flag(self):
        """Create a new flag matrix from plot selected flag items
        """

        items = self.get_selected_flag_items()

        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("No flag items to process!")
            ret = msgBox.exec_()
            return -1

        flag_image_items = self.get_selected_flag_image_items()


        if prefs.FLAG_SELECTED_CONFIRM:
            msgBox = QMessageBox()
            if flag_image_items:
                msgBox.setText("You are going to append data to the selected flagging matrices")
                msgBox.setInformativeText("Flagging tool selected areas will be added")
            else:
                msgBox.setText("You are going to create a flag matrix on the data file")
                msgBox.setInformativeText("Flagging tool selected areas will be collapsed in the new matrix")

            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1


        row = self.tablelist.currentRow()
        #name = self.data_ref.datasets[row].th[2]
        feed = self.data_ref.datasets[row].feed_section[0]
        section = self.data_ref.datasets[row].feed_section[1]
        pola = []
        for item in self.get_items_nogrid():
            if not is_flag(item) and not is_flag_image(item) and item.isVisible():
                pola.append(item.title().text())

        try:
            for item in items:
                if item.autoflag == True:
                    print item.autosets[0], item.autosets[1]
                    self.data_ref.auto_flag_save(item.autosets[0], [item.autosets[1]])
        except:
            ylimits = (self.data_ref.get_time_scale(row)[-1], self.data_ref.get_time_scale(row)[0])
            flag_areas = []
            for item in items:
                if item.pola != pola[0]:
                    msgBox = QMessageBox()
                    msgBox.setText("You are saving for the current polarization a manual flag area created for another polarization. Are you sure?")
                    msgBox.addButton(QMessageBox.Cancel)
                    msgBox.addButton(QMessageBox.Ok)
                    msgBox.setDefaultButton(QMessageBox.Cancel)
                    ret = msgBox.exec_()
                    if ret != QMessageBox.Ok:
                        return -1
                xmin, ymin, xmax, ymax = get_ordered_rect(item, ylimits)
                if self.axes_phys_unit:
                    X = self.data_ref.get_freq_scale(row)
                    Y = self.data_ref.get_time_scale(row)
                    xmin = (np_abs(X-xmin)).argmin()
                    ymin = (np_abs(Y-ymin)).argmin()
                    xmax = (np_abs(X-xmax)).argmin()
                    ymax = (np_abs(Y-ymax)).argmin()

                flag_areas.append([ymin, ymax, xmin, xmax])

            if flag_image_items:
                for flag_image_item in flag_image_items:
                    self.data_ref.upd_flagset(row, flag_image_item.dw_k_flagset, flag_areas)
            else:
                self.data_ref.new_flagset(row, flag_areas, feed, section, pola[0])

        self.imagewidget.plot.del_items(items)
#        (l1, l2, l3, l4)= self.imagewidget.plot.get_plot_limits()
        self.show_flagging_sets()
#        self.imagewidget.plot.set_plot_limits(l1, l2, l3, l4)
#        self.imagewidget.plot.replot()

    def deflag_intersected(self):

        #items = self.get_checked_flag_items()
        items = self.get_selected_flag_items()

        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("No rectangular area selected!")
            ret = msgBox.exec_()
            return -1

        #flag_image_items = self.get_selected_flag_image_items()


        if prefs.FLAG_SELECTED_CONFIRM:
            msgBox = QMessageBox()
            msgBox.setText("You are going to remove the flag entries intersected by the selected areas")
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1


        row = self.tablelist.currentRow()
        #name = self.tablelist.currentItem().text()
        ylimits = (self.data_ref.get_time_scale(row)[-1], self.data_ref.get_time_scale(row)[0])
        flag_areas = []
        for item in items:
            xmin, ymin, xmax, ymax = get_ordered_rect(item, ylimits)
            if self.axes_phys_unit:
                X = self.data_ref.get_freq_scale(row)
                Y = self.data_ref.get_time_scale(row)
                xmin = (np_abs(X-xmin)).argmin()
                ymin = (np_abs(Y-ymin)).argmin()
                xmax = (np_abs(X-xmax)).argmin()
                ymax = (np_abs(Y-ymax)).argmin()

            flag_areas.append([ymin, ymax, xmin, xmax])

        for fa in flag_areas:
            self.data_ref.del_sel_flag(row, fa, self.current_pola)

        self.imagewidget.plot.del_items(items)

        self.show_flagging_sets()

    def show_flagging_sets(self):
        """Retrieve flagging sets data for the selected dataset
        """
        row = self.tablelist.currentRow()
        self.data_ref.get_flagsets(row)
        plot = self.imagewidget.plot
        (l1, l2, l3, l4)= plot.get_plot_limits()
        self.imagewidget.plot.del_items(self.get_flag_image_items())

        (X, Y) = self.get_current_axes_scales()

        ii = 0
        flagsets = self.data_ref.flagsets2np_array(row)
        for k_flagset, flagset in flagsets.iteritems():
            rif = self.data_ref.datasets[row].flagsets_rif[k_flagset]
            title = 'Flag.({})_F{}S{}:{}'.format(id_dict[rif[3][0]], rif[0], rif[1], rif[2]) #':'+str(k_flagset).split(':')[-1]
            item = make.xyimage(X,Y,flagset,alpha_mask=True,colormap='gray', title = title)
            item.feed = rif[0]
            item.section = rif[1]
            item.pola = rif[2]
            item.interpolate=(0,)
            item.dw_k_flagset = k_flagset
            item.set_lut_range([0,3])
            plot.add_item(item)
            ii = ii+1
        plot.set_plot_limits(l1, l2, l3, l4)
        plot.replot()
        self.item_notsaved()

    def del_selected_flag_image_item(self):
        """Delete flagging sets from data file
        """
        row = self.tablelist.currentRow()

        items = self.get_selected_flag_image_items()
        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("No flagging matrices selected")
            ret = msgBox.exec_()
            return -1

        msgBox = QMessageBox()
        msgBox.setText("You are going to permanently delete flagging matrices")
        msgBox.setInformativeText("Press OK to continue")
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.addButton(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret != QMessageBox.Ok:
            return -1

        for item in items:
            self.data_ref.del_flagset(row, item.dw_k_flagset)

        try:
            self.show_flagging_sets()
        except:
            pass

    def merge_selected_flag_image_items(self):
        """Merge two or more flagging sets
        """

        row = self.tablelist.currentRow()
        items = self.get_selected_flag_image_items()

        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("No flagging matrices selected")
            ret = msgBox.exec_()
            return -1

        msgBox = QMessageBox()
        msgBox.setText("You are going to permanently merge flagging matrices")
        msgBox.setInformativeText("Press OK to continue")
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.addButton(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret != QMessageBox.Ok:
            return -1

        items_idx = []
        for item in items:
            items_idx.append(item.dw_k_flagset)

        self.data_ref.merge_flagsets(row, items_idx)

        try:
            self.show_flagging_sets()
        except:
            pass

    def deflag_selected_flag_image_items(self):
        """Deflag previously flagged areas on axsisting flagsets
        """
        items = self.get_checked_flag_items()

        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("No flag items to process!")
            ret = msgBox.exec_()
            return -1

        flag_image_items = self.get_selected_flag_image_items()

        if not len(flag_image_items):
            msgBox = QMessageBox()
            msgBox.setText("No flag matrices to deflag!")
            ret = msgBox.exec_()
            return -1

        if prefs.FLAG_SELECTED_CONFIRM:
            msgBox = QMessageBox()
            msgBox.setText("You are going to deflag data to the selected flagging matrices")
            msgBox.setInformativeText("Flagging tool selected areas will be set as NOT flagged")
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1

        row = self.tablelist.currentRow()
        flag_areas = []
        for item in items:
            xmin, ymin, xmax, ymax = get_ordered_rect(item)

            if self.axes_phys_unit:
                X = self.data_ref.get_freq_scale(row)
                Y = self.data_ref.get_time_scale(row)
                xmin = (np_abs(X-xmin)).argmin()
                ymin = (np_abs(Y-ymin)).argmin()
                xmax = (np_abs(X-xmax)).argmin()
                ymax = (np_abs(Y-ymax)).argmin()

            flag_areas.append([ymin.astype(int),
                               ymax.astype(int),
                               xmin.astype(int),
                               xmax.astype(int)])

        for flag_image_item in flag_image_items:
            self.data_ref.deflag_flagset(row, flag_image_item.dw_k_flagset, flag_areas)

        self.imagewidget.plot.del_items(items)
        self.imagewidget.plot.replot()
        self.show_flagging_sets()

    def propag_flag_table(self):
        try:
            self.data_ref.fileh['flag table']
        except:
            msgBox = QMessageBox()
            msgBox.setText("The current file doesn't have a flag table")
            msgBox.exec_()
            return -1

        flret = getopenfilenames(self, _("Select file list"), dirname(self.data_ref.file_name))[0]
        if len(flret) == 0:
            return -1

        filelist = []
        for f in flret:
            filelist.append(str(f))

        msgBox = QMessageBox()
        msgBox.setText("Are you sure to append the current flag table to the selected files?")
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.addButton(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret != QMessageBox.Ok:
            return -1

        try:
            self.data_ref.propag_flagtable(filelist)
        except:
            msgBox = QMessageBox()
            msgBox.setText("Error in writing flag table")
            msgBox.exec_()
            return -1

        #if len(errors) > 0:
        #    ferr_str = "Errors for files: "
        #    for f in errors:
        #        ferr_str = ferr_str+f+', '
        #    msgBox = QMessageBox()
        #    msgBox.setText(ferr_str)
        #    msgBox.exec_()
        #    return -1

    def propag_feeds(self):
        """Propagate a flag from a feed to another
        """
        row = self.tablelist.currentRow()
        cf = self.data_ref.datasets[row].feed_section[0]
        cs = self.data_ref.datasets[row].feed_section[1]
        items = self.get_selected_flag_image_items()
        nfeeds = len(list(set([str(i.feed_section[0]) for i in self.data_ref.datasets])))

        if len(items) == 0:
            msgBox = QMessageBox()
            msgBox.setText("No flag selected!")
            msgBox.exec_()
            return -1

        if nfeeds == 1:
            msgBox = QMessageBox()
            msgBox.setText("There is only one feed!")
            msgBox.exec_()
            return -1

        propwidget = PropagWidget(self.data_ref, cf)
        propwidget.edit()

        tofeeds = propwidget.choice

        msgBox = QMessageBox()
        msgBox.setText("Are you sure to propagate the selected flags"
                       "to feeds:\n {} ?".format(', '.join(tofeeds)))
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.addButton(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret == QMessageBox.Cancel:
            return -1

        for item in items:
            self.data_ref.propag_tofeed(row, item.dw_k_flagset, tofeeds)

        for key in self.mem_dict.keys():
            f = self.data_ref.datasets[key].feed_section[0]
            s = self.data_ref.datasets[key].feed_section[1]
            if str(f) in tofeeds and s == cs:
                del self.mem_dict[key]

    def flag_widget(self):
        """Run a FlagWidget instance to set a flag area
        """
        new_item = 1
        items = self.get_selected_flag_items()
        if len(items) > 1:
            msgBox = QMessageBox()
            msgBox.setText("Too many items selected!")
            ret = msgBox.exec_()
            return -1

        if len(items) == 1:
            xmin, ymin, xmax, ymax = get_ordered_rect(items[0])
            new_item = 0
        else:
            xmin = ymin = xmax = ymax = 0

        (X, Y) = self.get_current_axes_scales()

        flag_widget = FlagWidget(ymin, ymax, xmin, xmax)
        flag_widget.edit()
        xmin, ymin, xmax, ymax, enable_sample, enable_channel = flag_widget.get_widget_rect()

        if not enable_sample:
            xmin = Y[0]
            xmax = Y[-1]

        if not enable_channel:
            ymin = X[0]
            ymax = X[-1]


        if new_item:
            pass
#            self.new_rect_flag_item(xmin, ymin, xmax, ymax)
        else:
            items[0].set_rect(ymin,xmin,ymax,xmax)
            self.imagewidget.plot.replot()

#            self.update_rect_flag_item(xmin, ymin, xmax, ymax)

        print(xmin, ymin, xmax, ymax)

    def rplot_widget_time(self):
        self.rplot_widget(axis = 0)

    def rplot_widget_freqs(self):
        self.rplot_widget(axis = 1)

    def rplot_widget(self, axis = 0):
        """Run a RecurrencePlot instance to show recurrence plot
        """

        items = self.get_selected_flag_items()

        if len(items) > 1:
            msgBox = QMessageBox()
            msgBox.setText("Recurrence plot tool")
            msgBox.setText("Too many items selected!")
            ret = msgBox.exec_()
            return -1

        if not len(items):
            msgBox = QMessageBox()
            msgBox.setText("Recurrence plot tool")
            msgBox.setText("No item selected. Proceed with the entire dataset?")

            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1
            else:
                xmin = ymin = 0
                ymax,xmax = self.image.data.shape
        else:
            xmin, ymin, xmax, ymax = get_ordered_rect(items[0])
            if self.axes_phys_unit:
                row = self.tablelist.currentRow()
                X = self.data_ref.get_freq_scale(row)
                Y = self.data_ref.get_time_scale(row)
                xmin = (np_abs(X-xmin)).argmin()
                ymin = (np_abs(Y-ymin)).argmin()
                xmax = (np_abs(X-xmax)).argmin()
                ymax = (np_abs(Y-ymax)).argmin()
            xmin = max(0,np_abs(xmin))
            ymin = max(0,np_abs(ymin))
            xmax = min(np_abs(xmax),self.image.data.shape[1])
            ymax = min(np_abs(ymax),self.image.data.shape[0])

        if axis:
            rplot_widg = RecurrenceDialog(np_transpose(self.image.data), (ymin,xmin,ymax,xmax))
        else:
            rplot_widg = RecurrenceDialog(self.image.data, (xmin,ymin,xmax,ymax))
        rplot_widg.show()

    def freq_off_action(self):
        """Set the offset of the frequency scale and update flagging items
        """
        freq_off_widget = FreqOffWidget()
        freq_off_widget.edit()

        row = self.tablelist.currentRow()

        items = self.get_flag_items()
        for item in items:
            xmin, ymin, xmax, ymax = get_ordered_rect(item)
            item.set_rect(xmin+freq_off_widget.freq_off-self.data_ref.get_freq_scale(row)[0],
                          ymin,
                          xmax+freq_off_widget.freq_off-self.data_ref.get_freq_scale(row)[0],
                          ymax)

        self.data_ref.upd_freq_scale_off(row, freq_off_widget.freq_off)
        self.current_table_changed(row)

    def rfi_dect_action(self):
        plot = self.imagewidget.plot
        (X, Y) = self.get_current_axes_scales()

        alg_selection = AlgSelectionWidget(self.data_ref.dect_alg)
        ret = alg_selection.edit()
        if ret:
            if self.data_ref.dect_alg.has_key(alg_selection.choice):
                row = self.tablelist.currentRow()
                self.data_ref.auto_flag_init(row, alg_selection.choice)
                param_selection = AlgParamWidget(self.data_ref, row)
                ret = param_selection.edit()
                if ret:
                    par_dict = param_selection.get_params()
                    self.data_ref.auto_flag_upd_params(**par_dict)
                    out_selection = AlgOutWidget(self.data_ref)
                    ret = out_selection.edit()
                    if ret:
                        #self.data_ref.auto_flag_compute(out_labels = out_selection.get_out())
                        try:
                            wds, f_res = self.data_ref.auto_flag_compute(out_labels = out_selection.get_out(), save=False)
                        except ValueError:
                            msgBox = QMessageBox()
                            msgBox.setText("Parameters error!")
                            msgBox.exec_()
                            return -1
                        for f in f_res:
                            flagset = f.flag_data
                            #feed = self.data_ref.datasets[row].feed_section[0]
                            #sect = self.data_ref.datasets[row].feed_section[1]
                            n_id = id_dict[self.data_ref.selected_dect_alg.name]
                            title = 'Flag.({})_F{}S{}:{}'.format(n_id, f.feed, f.section, f.pola)
                            item = make.xyimage(X,Y,flagset,alpha_mask=True,colormap='gray', title = title)
                            item.feed = f.feed
                            item.section = f.section
                            item.pola = f.pola
                            item.interpolate=(0,)
                            item.set_lut_range([0,3])
                            item.autoflag = True
                            item.algorithm = f.algorithm
                            item.params = f.params
                            item.flagresult = f.flagresult
                            item.autosets = (wds, f)
                            plot.add_item(item)
                            plot.replot()
                        self.item_selection_changed()
                        #self.show_flagging_sets()
                    else:
                        return -1
                else:
                    return -1
            else:
                return -1
        else:
            return -1

    def item_selection_changed(self):
        row = self.tablelist.currentRow()
        items = self.get_selected_flag_image_items()
        self.flag_meta = ''
        if len(items) == 1:
#            print(type(items[0].title()))
#            items[0].title().setTextEngine()
#            print(type(items[0].title().text().title()))
            for k in self.data_ref.get_flagset_meta(row, items[0].dw_k_flagset).keys():
                self.flag_meta = self.flag_meta+'\n'+str(k)+'='+str(self.data_ref.get_flagset_meta(row, items[0].dw_k_flagset)[k])
            #self.flag_meta = self.data_ref.get_flagset_meta(row, str(items[0].title().text()))
        elif len(items) == 0:
            items = self.get_selected_flag_items()
            if len(items) == 1:
                try:
                    items[0].autoflag
                    for k in ['flagresult','params','algorithm']:
                        if k == 'params':
                            value = ''
                            for i in getattr(items[0], k).keys():
                                value = value+str(i)+': '+str(getattr(items[0], k)[i])+' '
                        else:
                            value = str(getattr(items[0], k))
                        self.flag_meta = self.flag_meta+'\n'+str(k)+'='+value
                except AttributeError:
                    pass
        self.upd_metadata()

#    def active_item_changed(self):
        items = self.imagewidget.plot.get_items()
        aitem = self.imagewidget.plot.active_item
        if type(aitem)==XYImageItem and not is_flag(aitem) and not is_flag_image(aitem):
            for i in items:
                if type(i)==XYImageItem and not is_flag(i) and not is_flag_image(i):
                    if i.selected:
                        i.setVisible(True)
                        self.current_pola = i.title().text()
                    else:
                        i.setVisible(False)

            for f in items:
                if is_flag(f) or is_flag_image(f):
                    if f.pola == self.current_pola:
                        f.setVisible(True)
                    else:
                        f.setVisible(False)

        for cross_section in ['x_cross_section', 'y_cross_section']:
            self.imagewidget.panels[cross_section].cs_plot.known_items = {}
            for item in self.imagewidget.panels[cross_section].cs_plot.items[2:]:
                item.clear_data()
                self.imagewidget.panels[cross_section].cs_plot.del_item(item)

            for item in items:
                if issubclass(type(item), XYImageItem) and item.isVisible():
                    self.imagewidget.panels[cross_section].cs_plot.add_cross_section_item(source=item)
                    item.setVisible(item.isVisible())

            self.imagewidget.panels[cross_section].cs_plot.replot()
        self.imagewidget.itemlist.listwidget.items_changed(self.imagewidget.plot)
        self.item_notsaved()

    def open_corr_file(self):
        if self.data_ref.cfileh is not None:
            msgBox = QMessageBox()
            msgBox.setText("The correction file: "+ self.data_ref.cfile_name +" is alredy loaded. Change correction file?")
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1

        corr_file = getopenfilename(self, _("Select file list"), dirname(self.data_ref.file_name))[0]
        if corr_file == None:
            return -1

        try:
            self.data_ref.open_correction_file(str(corr_file))
        except:
            msgBox = QMessageBox()
            msgBox.setText("Not a correction file!")
            msgBox.exec_()
            return -1

    def toggle_corr(self):
        if self.data_ref.cfileh is None:
            msgBox = QMessageBox()
            msgBox.setText("No correction file open. Open it?")
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.addButton(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec_()
            if ret != QMessageBox.Ok:
                return -1

            self.open_corr_file()

        if self.data_ref.cfileh is not None:
            self.data_ref.toggle_correction()
            self.refresh_list()
        else:
            return -1

    def not_implemented(self):
        """Not implemented function dialog"""
        QMessageBox.about(self, "Sorry!", "Not yet implemented...")

    def data_uncheckable(self):
        plotlist = self.imagewidget.itemlist.listwidget
        items = plotlist.items
        for i in items:
            rawitem = plotlist.item(items.index(i))
            if str(rawitem.text()) in ["Data", "Grid", "L", "R", "Q", "U", "I", "V", "Phi", "P"]:
                rawitem.setData(Qt.CheckStateRole, QVariant())

    def item_notsaved(self):
        plotlist = self.imagewidget.itemlist.listwidget
        items = plotlist.items
        for i in items:
            if is_flag(i):
                rawitem = plotlist.item(items.index(i))
                rawitem.setForeground(QColor('red'))
            elif is_flag_image(i):
                rawitem = plotlist.item(items.index(i))
                rawitem.setForeground(QColor('blue'))
        self.imagewidget.refresh()
        #self.imagewidget.itemlist.listwidget.items_changed(self.imagewidget.plot)

class RecurrenceWidget(QWidget):
    """DEPRECATED"""
    def __init__(self, parent, r_range):
        QWidget.__init__(self)
        self.parent = parent
        self.r_range = r_range

        layout = QGridLayout()
        self.setLayout(layout)

        self.rplot = ImagePlot(self)
        layout.addWidget(self.rplot, 0, 0, 1, 0)
        self.rspect = CurvePlot(self)
        layout.addWidget(self.rspect,1, 0, 1, 0)

        self.contrast = ContrastAdjustment(self)
        layout.addWidget(self.contrast, 2, 0, 1, 0)
        self.itemlist = PlotItemList(self)
#        layout.addWidget(self.itemlist, 0, 1, 2, 0)

        self.manager = PlotManager(self)
        for plot in (self.rplot, self.rspect):
            self.manager.add_plot(plot)
        for panel in (self.itemlist, self.contrast):
            self.manager.add_panel(panel)

        self.compute_reference()

        r_image = make.image(self.r_data.rplot)
        self.rplot.add_item(r_image)

    def register_tools(self):
        self.manager.register_all_image_tools()

    def compute_reference(self):

#        print self.r_range
        self.r_data = recurrence.Recurrence()
        self.r_data.r_plot(self.parent.image.data[self.r_range[1]:self.r_range[3],self.r_range[0]:self.r_range[2]])

class RecurrenceDialog(ImageDialog):

    def __init__(self, data, r_range, wintitle=_("Recurrence plot"),
                 icon="guidata.svg", options=dict(show_contrast=False, yreverse=False),
                 edit=False):
#        rspect = CurvePlot(self)
        self.data = data
#        self.parent = parent
        self.r_range = r_range

        super(ImageDialog, self).__init__(wintitle=wintitle, icon=icon,
                                            toolbar=True, edit=edit,
                                            options=options)

        self.compute_reference()

        r_image = make.image(self.r_data.rplot)
        r_image.interpolate=(0,)
        self.get_plot().add_item(r_image)


    def compute_reference(self):

#        print self.r_range
        self.r_data = recurrence.Recurrence()
        self.r_data.r_plot(self.data[self.r_range[1]:self.r_range[3],self.r_range[0]:self.r_range[2]])

    def register_tools(self):
        self.register_standard_tools()
        self.add_tool(ColormapTool)
        self.add_tool(ContrastPanelTool)
        self.add_tool(ReverseYAxisTool)

class PolaViewerWidget(MainWidget):

    """Implement the main widget to visualize and manipulate the polarimeter data

    Methods
        -------
    * current_table_changed: update the plot as the selected dataset changes
    * show_data: plot the selected dataset
    * mu_toggle: toggle physical measure units on/off on the main plot and cross section plots
    """

    #def rfi_dect_action(self):
    #    print("-->")

    def current_table_changed(self, row):
        """Update the plot as the selected dataset changes"""
        self.get_items_status()
        #self.imagewidget.plot.del_items(self.get_image_items())
        self.imagewidget.plot.del_items(self.get_items_nogrid())
        self.image.title = self.tablelist.item(row).text()
        self.image.bandwidth = self.data_ref.get_bandwidth(row)
        self.image.data = self.data_ref.polaset2np_array(row)
        self.image.a_ut = self.data_ref.get_ut(row)
        self.image.a_ascension = math.degrees(self.data_ref.get_ascension(row)[0])
        self.image.a_declination = math.degrees(self.data_ref.get_declination(row)[0])
        self.image.a_azimuth = math.degrees(self.data_ref.get_azimuth(row)[0])
        self.image.a_elevation = math.degrees(self.data_ref.get_elevation(row)[0])
        self.image.a_source = self.data_ref.get_source(row)
        self.image.a_on_track = self.data_ref.get_on_track(row)
        self.image.height, self.image.width = self.image.data[0].shape
        update_dataset(self.properties.dataset, self.image)
        self.properties.get()
        self.properties.setEnabled(True)
        if row in self.mem_dict:
            self.set_items_status(row)
        else:
            self.show_data(self.data_ref.get_freq_scale(row),
                           self.data_ref.get_time_scale(row),
                           self.image.data,
                           self.lut_ranges[row],
                           phys_units = self.axes_phys_unit)

            try:
                self.show_flagging_sets()
            except:
                pass
        self.tablelist.man_current = row
        self.imagewidget.itemlist.listwidget.items_changed(self.imagewidget.plot)
        self.item_notsaved()

    def show_data(self, x, y, data_l, lut_range=None, phys_units=prefs.AXES_PHYS_UNIT):
        """Plot the selected dataset

        x: 1D numpy array for the x axes values
        y: 1D numpy array for the y axes values
        data: 2D numpy array (time-frequency matrix)
        lut_range:
        phys_units: boolean (default=True)
        """
        title = ["L", "R", "Q", "U"] #, "stk_i", "stk_v", "stk_phi", "stk_p"]
#        if self.mir_x == True:
#            data = data.transpose()[::-1].transpose()

        plot = self.imagewidget.plot
        ii = 0
        for data in data_l:
            if phys_units:
                self.axes_phys_unit = True
                self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_PHYSICS, ylabel=prefs.Y_LABEL_PHYSICS)
                self.item = make.xyimage(x,y,data,title=title[ii])
                self.imagewidget.plot.lock_aspect_ratio = False
            else:
                self.axes_phys_unit = False
                self.item = make.xyimage(np_array(range(len(x))),np_array(range(len(y))),data,title=title[ii])
                self.imagewidget.plot.set_titles(xlabel=prefs.X_LABEL_ARBITRARY, ylabel=prefs.Y_LABEL_ARBITRARY)
            self.item.interpolate=(0,)
            if title[ii] != 'L':
                self.item.hide()
            plot.add_item(self.item, z=-ii-2)
            ii = ii +1
        plot.replot()

    def mu_toggle(self):
        """Toggle physical measure units on/off on the main plot and cross section plots"""
        plot = self.imagewidget.plot
        self.axes_phys_unit = not self.axes_phys_unit
        to_phys_units = self.axes_phys_unit
        row = self.tablelist.currentRow()
        x = self.data_ref.get_freq_scale(row)
        y = self.data_ref.get_time_scale(row)
        limits = plot.get_plot_limits()
        if self.item is not None:
            if to_phys_units:
                #self.item.set_xy(x,y)
                flag_image_mu_toggle(self.get_image_items(), x, y)

                x_min = x[int(np_round(limits[0]))]
                y_min = y[int(np_round(limits[2]))]
                x_max = x[int(np_round(limits[1]))]
                y_max = y[int(np_round(limits[3]))]

                self.imagewidget.plot.set_titles(xlabel='MHz',
                                                 ylabel='Seconds')
                flag_mu_toggle(plot.items, True, x, y)
            else:
#                self.item.set_xy(np_array(range(len(x))),np_array(range(len(y))))
                flag_image_mu_toggle(self.get_image_items(),
                                     np_array(range(len(x))),
                                     np_array(range(len(y))))

                x_min = (np_abs(x-limits[0])).argmin()
                y_min = (np_abs(y-limits[2])).argmin()
                x_max = (np_abs(x-limits[1])).argmin()
                y_max = (np_abs(y-limits[3])).argmin()

                self.imagewidget.plot.set_titles(xlabel='Channels',
                                                 ylabel='Samples')
                flag_mu_toggle(plot.items, False, x, y)
            plot.set_plot_limits(x_min, x_max, y_min, y_max)
            plot.replot()
        else:
            pass
