import sys
import numpy as np
import scipy.interpolate as inter
from os.path import exists, basename, dirname, normpath
#from os import walk

from guidata.qt.QtGui import (QMainWindow, QSplitter, QMessageBox, QFileDialog,
                              QListWidget, QListWidgetItem, QPushButton, QSizePolicy)
from guidata.qt.QtCore import (QSize, QT_VERSION_STR, PYQT_VERSION_STR, Qt, Signal)
from guidata.dataset.datatypes import DataSet, ValueProp, GetAttrProp, FuncProp, BeginGroup, EndGroup
from guidata.dataset.dataitems import (IntItem, StringItem, ChoiceItem, BoolItem, FloatItem)
from guidata.dataset.qtwidgets import DataSetEditGroupBox, DataSetShowGroupBox
from guidata.utils import update_dataset
from guidata.qt.compat import getexistingdirectory, getsavefilename, getopenfilename, getopenfilenames
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guiqwt.config import _

from guiqwt.builder import make
from guiqwt.plot import CurveWidget, BaseCurveWidget, PlotManager, CurvePlot, PlotItemList, configure_plot_splitter#, SIG_PLOT_AXIS_CHANGED
from guiqwt.baseplot import BasePlot
#from guiqwt.signals import SIG_PLOT_AXIS_CHANGED
from guiqwt.tools import RectZoomTool

import dw.core.data_def as dwdata

APP_NAME = _("Bandpass Correction")
APP_DESCRIPTION = ("Bandpass correction tool for Dish Washer")
LICENSE = """Released under the terms of GNU GPL v.3 <br>
             or (at your option) any later version"""

class ChoicesVariable(object):
    def __init__(self):
        self.choices = [("0", "0")]
        self.default = self.choices[0][0]

    def set(self, choices):
        normalized = []
        for idx, c in enumerate(choices):
            normalized.append(self._normalize_choice(idx, c))
        self.choices = normalized
        self.default = self.choices[0][0]

    def __call__(self, *args):
        return self.choices

    def _normalize_choice(self, idx, choice_tuple):
        img = None
        if isinstance(choice_tuple, tuple):
            if len(choice_tuple) == 2:
                key, value = choice_tuple
            else:
                key, value, img = choice_tuple
        else:
            key = idx
            value = choice_tuple
        if isinstance(value, str):
            value = str(value)
        return (key, value, img)

cfeeds = ChoicesVariable()
csections = ChoicesVariable()
cpolars = ChoicesVariable()

class FitParam(DataSet):
    _prop = GetAttrProp("fittype")
    fittype = ChoiceItem("Fit type", [("chebyshev", "Chebyshev"), ("spline", "Spline")], default="chebyshev").set_prop("display", store=_prop)
    k = IntItem(_("Spline degree"), help=_("Spline deg"),
                       min=1, max=5, default=3).set_prop("display", active=FuncProp(_prop, lambda x:x=='spline')).set_pos(col=1, colspan=2)
    s = IntItem(_("Spline Smooth"), help=_("Spline smooth"),
                min=0, default=30000).set_prop("display", active=FuncProp(_prop, lambda x:x=='spline')).set_pos(col=1, colspan=3)
    deg = IntItem(_("Chebyshev degree"), help=_("Chebyshev deg"),
                       min=0, default=90).set_prop("display", active=FuncProp(_prop, lambda x:x=='chebyshev')).set_pos(col=1, colspan=2)

class FitProperties(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)
        self.datas = DataSetEditGroupBox(_("Fit"), FitParam)
        self.addWidget(self.datas)

class DSParam(DataSet):
    feed = ChoiceItem("Feed", cfeeds, default=cfeeds.default)
    section = ChoiceItem("Section", csections, default=csections.default).set_pos(col=1, colspan=1)
    polar = ChoiceItem("Polarization", cpolars, default=cpolars.default).set_pos(col=2, colspan=1)

class DSProperties(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)
        DSParam.__init__
        self.datas = DataSetEditGroupBox(_("Dataset"), DSParam)
        self.addWidget(self.datas)

class InfoData(DataSet):
    feed = IntItem("Feed:", default=cfeeds.default)
    section = IntItem("Section:", default=csections.default).set_pos(col=1, colspan=1)
    polar = StringItem("Polarization:", default=cpolars.default).set_pos(col=2, colspan=1)
    freq = FloatItem("Frequency (MHz):", default="0.0").set_pos(col=3, colspan=1)
    band = FloatItem("Band (MHz):", default="0.0").set_pos(col=4, colspan=1)
    otype = StringItem("Type:", default="")
    flagname = StringItem("Flag file:", default="").set_pos(col=1, colspan=1)

class DSInfo(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)
        self.datas = DataSetShowGroupBox(_("Current"), InfoData)
        self.addWidget(self.datas)

class ImageParam(DataSet):
    #_hide_data = False
    #_hide_size = True
    #title = StringItem(_("Title"), default=_("Untitled")).set_prop("display", hide=True)
    #data = FloatArrayItem(_("Settings")).set_prop("display",
    #                                          hide=GetAttrProp("_hide_data"))
    _prop = GetAttrProp("otype")
    otype = StringItem("Type of data", default="Unknown").set_prop("display", store=_prop)#, hide=True)
    title = StringItem(_("Title"), default=_("Untitled")).set_prop("display", hide=True)
    _bg = BeginGroup("Range setting")
    #feed = ChoiceItem("Feed", [(1, "1"), (2, "2"), (3, "3")]).set_prop("display", active=False)
    #section = ChoiceItem("Section", [("Ch0", "0"), ("Ch1", "1"), ("Ch2", "2"),
    #                                 ("Ch3", "3")]).set_pos(col=1, colspan=2)
    #polar = ChoiceItem("Polar", [(16, "first choice"), (32, "second choice"),
    #                     (64, "third choice")]).set_pos(col=2, colspan=2)
    #_prop = GetAttrProp("otype")
    #otype = ChoiceItem("Type of data", [("On/Off: off source", "On/Off: off source"), ("OTF", "OTF"), ("Unknown", "Unknown")], default="Unknown").set_prop("display", store=_prop, hide=True)
    #otype = StringItem("Type of data", default="Unknown").set_prop("display", store=_prop)#, hide=True)
    rangei = IntItem(_("num. samples begin"), help=_("Select a number of samples at the begin of the data to use for the computation"), min=0,
                     default=0).set_prop("display", active=FuncProp(_prop, lambda x: x=='OTF' or  x=='Unknown'))
    ranges = IntItem(_("num. samples end"), help=_("Select a number of sameples at the end of the data to use for the computation"), min=0,
                     default=0).set_prop("display", active=FuncProp(_prop, lambda x: x=='OTF' or  x=='Unknown')).set_pos(col=1, colspan=2)
    rall = BoolItem(_("All"), default=True).set_pos(col=2, colspan=2).set_prop("display", active=FuncProp(_prop, lambda x: x=='OTF' or x=='Unknown'), hide=True)
    excluded = IntItem(_("Excluded samples"), help=_("Select a number of samples to exclude from the computation at the begining and end of the data symmetrically"), min=0,
                       default=0).set_prop("display", active=FuncProp(_prop, lambda x: x=='OTF' or  x=='Unknown'))
    eall = BoolItem(_("All"), default=True).set_pos(col=1, colspan=2).set_prop("display", hide=True)
    _eg = EndGroup("Range setting")

    _bg2 = BeginGroup("Fit Range")
    frangei = IntItem(_("intitial freq sample"), help=_("Select the first freq sample to use for the fit computation"), min=0, default=0)
    franges = IntItem(_("last freq sample"), help=_("Select the last freq sample to use for the fit computation (if 0 take max)"), min=0, default=0).set_pos(col=1, colspan=1)
    _eg2 = EndGroup("Fit Range")
    #selected = BoolItem(_("Selected"), default=True)
    selected = ChoiceItem("Selected", [(True, "Yes"), (False, "No")], default=True).set_prop("display", hide=True)

class RectZoomToolsig(RectZoomTool):
    SIG_PLOT_AXIS_CHANGED = Signal()

    def validate(self, filter, event):
        self.SIG_VALIDATE_TOOL.emit(filter)
        self.SIG_PLOT_AXIS_CHANGED.emit()
        self.SIG_TOOL_JOB_FINISHED.emit()

class BaseCurveWidget2(QSplitter):
    """
    Construct a BaseCurveWidget object, which includes:
        * A plot (:py:class:`guiqwt.curve.CurvePlot`)
        * An `item list` panel (:py:class:`guiqwt.curve.PlotItemList`)

    This object does nothing in itself because plot and panels are not
    connected to each other.
    See children class :py:class:`guiqwt.plot.CurveWidget`
    """
    def __init__(self, parent=None, title=None,
                 xlabel=None, ylabel=None, xunit=None, yunit=None,
                 section="plot", show_itemlist=False, gridparam=None,
                 rtitle=None, rxlabel=None, rylabel=None, rxunit=None,
                 ryunit=None, rsection="rplot", rgridparam=None,
                 curve_antialiasing=None):
        QSplitter.__init__(self, Qt.Vertical, parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plot = CurvePlot(parent=self, title=title, xlabel=xlabel,
                              ylabel=ylabel, xunit=xunit, yunit=yunit,
                              section=section, gridparam=gridparam)

        self.rplot = CurvePlot(parent=self, title=rtitle, xlabel=rxlabel,
                               ylabel=rylabel, xunit=rxunit, yunit=ryunit,
                               section=section, gridparam=rgridparam)

        if curve_antialiasing is not None:
            self.plot.set_antialiasing(curve_antialiasing)
            self.rplot.set_antialiasing(curve_antialiasing)
        self.addWidget(self.plot)
        self.addWidget(self.rplot)
        self.itemlist = PlotItemList(self)
        self.itemlist.setVisible(show_itemlist)
        self.addWidget(self.itemlist)
        configure_plot_splitter(self)

class CurveWidget2(BaseCurveWidget2, PlotManager):
    """
    Construct a CurveWidget object: plotting widget with integrated
    plot manager
        * parent: parent widget
        * title: plot title
        * xlabel: (bottom axis title, top axis title) or bottom axis title only
        * ylabel: (left axis title, right axis title) or left axis title only
        * xunit: (bottom axis unit, top axis unit) or bottom axis unit only
        * yunit: (left axis unit, right axis unit) or left axis unit only
        * panels (optional): additionnal panels (list, tuple)
    """
    def __init__(self, parent=None, title=None, rtitle=None,
                 xlabel=None, ylabel=None, rxlabel=None, rylabel=None,
                 xunit=None, yunit=None, rxunit=None, ryunit=None,
                 section="plot", rsection="rplot", show_itemlist=False,
                 gridparam=None, rgridparam=None,
                 panels=None):
        BaseCurveWidget2.__init__(self, parent, title,
                                 xlabel, ylabel, xunit, yunit,
                                 section, show_itemlist, gridparam,
                                 rtitle, rxlabel, rylabel, rxunit, ryunit,
                                 rsection, rgridparam)
        PlotManager.__init__(self, main=self)

        # Configuring plot manager
        self.add_plot(self.plot)
        self.add_plot(self.rplot)
        self.synchronize_axis("bottom", [self.plot, self.rplot])
        self.add_panel(self.itemlist)
        if panels is not None:
            for panel in panels:
                self.add_panel(panel)

class ImageListWithProperties(QSplitter):
    def __init__(self, parent):
        QSplitter.__init__(self, parent)
        self.imagelist = QListWidget(self)
        self.addWidget(self.imagelist)
        self.properties = DataSetEditGroupBox(_("Selection"), ImageParam)
        self.properties.setEnabled(False)
        self.addWidget(self.properties)

class FitWidget(QSplitter):
    def __init__(self, parent, toolbar):
        QSplitter.__init__(self, parent)
        self.data_ref = None
        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(Qt.Vertical)

        fitproperties = FitProperties(self)
        self.addWidget(fitproperties)
        self.fit_t = fitproperties.datas
        self.fit_t.SIG_APPLY_BUTTON_CLICKED.connect(self.properties_changed)

        self.imagewidget = CurveWidget2(self)
        #self.reswidget = CurveWidget(self)
        print self.imagewidget.synchronized_plots
        self.item = None
        self.fitem = None
        self.ritem = None
        self.flagitem = None

        self.imagewidget.add_toolbar(toolbar, "default")
        self.imagewidget.register_standard_tools()
        self.imagewidget.add_tool(RectZoomToolsig)

        self.imagewidget.plot.SIG_PLOT_AXIS_CHANGED.connect(self.sync_zoom)

        fitfile = create_action(self, _("Update fit file..."),
                                icon=get_icon('fileopen.png'), tip=_("Update fit file"),
                                triggered=self.fitfile)
        add_actions(toolbar, [fitfile])

        self.addWidget(self.imagewidget)
        #self.addWidget(self.reswidget)

        self.fitc = None
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([100, 600, 100])

    def set_data_ref(self, data_ref, begin, end):
        self.data_ref = data_ref
        self.median = data_ref.gmed
        self.feed = data_ref.dssel[0]
        self.section = data_ref.dssel[1]
        self.polar = data_ref.dssel[2]
        self.begin = begin
        self.end = end
        self.flag = data_ref.flag

    def open_setup(self, data_ref, begin, end):
        self.fsel = FitParam()
        self.set_data_ref(data_ref, begin, end)
        self.show_data(self.median[0], self.median[1], self.flag)
#        self.set_images(data_ref)
#        self.set_ds_selector(data_ref)
#        self.refresh_list()

#    def refresh_list(self):
#        self.imagelist.clear()
#        self.imagelist.addItems([image.title for image in self.images])

    def sync_zoom(self):
        print "signal"
        lim = self.imagewidget.plot.get_axis_limits(1)
        self.imagewidget.rplot.set_axis_limits(1, lim[0], lim[1])
        self.imagewidget.rplot.replot()

    def show_data(self, x, y, flag=None, fx=None, fy=None, res=None):#, lut_range=None):
        plot = self.imagewidget.plot
        #rplot = self.reswidget.plot
        rplot = self.imagewidget.rplot
        rplot.set_axis_limits(1, x[0], x[-1])
        if self.item is not None:
            self.item.set_data(x, y)
        else:
            self.item = make.curve(x, y, color='blue')
            plot.add_item(self.item, z=0)
        if flag is not None:
            if self.flagitem is not None:
                self.flagitem.set_data(x, flag*y)
            else:
                self.flagitem = make.curve(x, flag*y, color='green')
                plot.add_item(self.flagitem, z=0)
        if fx is not None:
            if flag is not None:
                res = flag[fx[0]:fx[-1]+1]*res
            if self.fitem is not None:
                self.fitem.set_data(fx, fy)
            else:
                self.fitem = make.curve(fx, fy, color='red')
                plot.add_item(self.fitem, z=0)
            if self.ritem is not None:
                self.ritem.set_data(fx, res)
            else:
                self.ritem = make.curve(fx, res, color='red')
                rplot.add_item(self.ritem, z=0)
        plot.replot()
        rplot.replot()

    def properties_changed(self):
        update_dataset(self.fsel, self.fit_t.dataset)
        self.fitc = self.data_ref.get_fit(self.fsel.fittype, self.median, self.fsel.k, self.fsel.s, self.fsel.deg, self.begin, self.end, self.flag)
        self.show_data(self.median[0], self.median[1], self.flag, self.fitc[0], self.fitc[1], self.fitc[3])

    def fitfile(self):
        if self.fitc == None:
            msgBox = QMessageBox()
            msgBox.setText("Fit not yet executed!")
            msgBox.exec_()
            return -1

        msgBox = QMessageBox()
        msgBox.setText("Save correction file?")
        #msgBox.setInformativeText("A correction file will be saved in the root directory of the observation.")
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.addButton(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret != QMessageBox.Ok:
            return -1

        name = getsavefilename(self, _("Save File"),
                               self.data_ref.dir_name+"/"+basename(normpath(self.data_ref.dir_name)+"_fit."+self.data_ref.files_type),
                               options=QFileDialog.DontConfirmOverwrite)
        if str(name[0]):
            if exists(str(name[0])):
                msgBox = QMessageBox()
                msgBox.setText("File exists!")
                msgBox.setInformativeText("Do you want to update it?")
                msgBox.addButton(QMessageBox.Cancel)
                msgBox.addButton(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                ret = msgBox.exec_()
                if ret != QMessageBox.Ok:
                    return -1

            self.data_ref.fitfile(str(name[0]), self.fitc)

class MainWidget(QSplitter):
    def __init__(self, parent, toolbar):
        QSplitter.__init__(self, parent)
        self.data_ref = None
        self.setContentsMargins(10, 10, 10, 10)
        self.setOrientation(Qt.Vertical)

        dsinfo = DSInfo(self)
        self.addWidget(dsinfo)
        dsproperties = DSProperties(self)
        self.addWidget(dsproperties)
        imagelistwithproperties = ImageListWithProperties(self)
        self.addWidget(imagelistwithproperties)
        self.imagelist = imagelistwithproperties.imagelist
        self.imagelist.currentRowChanged.connect(self.current_item_changed)
        self.imagelist.itemSelectionChanged.connect(self.selection_changed)
        self.ds = dsproperties.datas
        self.info = dsinfo.datas
        self.ds.SIG_APPLY_BUTTON_CLICKED.connect(self.properties_changed)
        self.properties = imagelistwithproperties.properties
        self.properties.SIG_APPLY_BUTTON_CLICKED.connect(self.properties_changed)

        self.imagewidget = CurveWidget(self)
        self.item = None
        self.flagitem = None
        self.flagname = ""

        self.imagewidget.add_toolbar(toolbar, "default")
        self.imagewidget.register_standard_tools()

        flag = create_action(self, _("Get preflag from file..."),
                             icon=get_icon('eraser.png'), tip=_("Get a preflag from file"),
                             triggered=self.preflag)
        fit = create_action(self, _("Open fit window..."),
                                  icon=get_icon('polyline.png'), tip=_("Open fit window"),
                                  triggered=self.fit_win)
        #apply = create_action(self, _("Apply fit file..."),
        #                      icon=get_icon('export.png'), tip=_("Apply fit file"),
        #                      triggered=self.apply_fit)
        add_actions(toolbar, [None, flag, fit])
        self.addWidget(self.imagewidget)

        self.images = []
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setHandleWidth(10)
        self.setSizes([50, 100, 200, 600])

    def set_data_ref(self, data_ref):
        self.data_ref = data_ref
        self.data_ref.flag = None

    def set_images(self, data_ref):
        for dataset in data_ref.dir_datasets:
            image = ImageParam()
            image.title = dataset.title
            image.otype = dataset.otype
            image.selected = dataset.selected
            self.images.append(image)

    def set_ds_selector(self):
        #c_polar = [("l", "l"), ("r", "r")]
        #choices.set(c_polar)
        #print choices.__call__()
        self.dssel = DSParam()

    def open_setup(self, data_ref):
        self.set_data_ref(data_ref)
        self.set_images(data_ref)
        self.set_ds_selector()
        self.refresh_list()
        self.update_info()

#    def refresh_list(self):
#        self.imagelist.clear()
#        self.imagelist.addItems([image.title for image in self.images])
    def refresh_list(self):
        self.imagelist.clear()
        for image in self.images:
            item = QListWidgetItem(image.title)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(2 if image.selected else 0)
            self.imagelist.addItem(item)

    def selection_changed(self):
        row = self.imagelist.currentRow()
        self.properties.setDisabled(row == -1)

    def current_item_changed(self, row):
        self.image = self.images[row]
        med = self.data_ref.get_median_data([row], self.dssel.section, self.dssel.polar, [self.image.rangei], [self.image.ranges], [self.image.excluded])
        self.image.x = med[0]
        self.image.y = med[1]
        self.show_data(self.image.x, self.image.y, self.data_ref.flag)
        update_dataset(self.properties.dataset, self.image)
        self.properties.get()
        self.update_info()

    def show_data(self, x, y, flag=None):
        plot = self.imagewidget.plot
        if self.item is not None:
            self.item.set_data(x, y)
        else:
            self.item = make.curve(x, y, color='blue')
            plot.add_item(self.item, z=0)
        if flag is not None:
            if self.flagitem is not None:
                self.flagitem.set_data(x, flag*y)
            else:
                self.flagitem = make.curve(x, flag*y, color='green')
                plot.add_item(self.flagitem, z=0)
        plot.replot()

    def update_info(self):
        row = self.imagelist.currentRow()
        ds = self.data_ref.dir_datasets[row]
        self.info.dataset.feed = self.dssel.feed
        self.info.dataset.section = self.dssel.section
        d = {"0":"L", "1":"R", "2":"Q", "3":"U"}
        self.info.dataset.polar = d[self.dssel.polar]
        self.info.dataset.freq = self.data_ref.dw_io.get_frequency(ds.th)
        self.info.dataset.band = self.data_ref.dw_io.get_bandwidth(ds.th,
                                        self.dssel.section, d[self.dssel.polar])
        self.info.dataset.otype = ds.otype
        self.info.dataset.flagname = self.flagname
        self.info.get()

    def properties_changed(self):
        row = self.imagelist.currentRow()
        image = self.images[row]
        try:
            image.x
        except:
            pass
        else:
            if ((self.properties.dataset.franges != 0 and
                self.properties.dataset.franges < len(image.x) and
                self.properties.dataset.frangei < self.properties.dataset.franges) or
                (self.properties.dataset.franges == 0 and
                self.properties.dataset.frangei < len(image.x))):
                pass
            else:
                msgBox = QMessageBox()
                msgBox.setText("Fit range void or out of bound! Range max 0:%s" % (len(image.x)-1))
                msgBox.exec_()
                return -1
        update_dataset(image, self.properties.dataset)
        #self.dssel.section = self.data_ref.list2choices(self.data_ref.sections[int(self.ds.dataset.feed)])
        csections.set(self.data_ref.list2choices(self.data_ref.sections[int(self.ds.dataset.feed)]))
        update_dataset(self.dssel, self.ds.dataset)
        self.update_info()
        if self.flagname:
            self.data_ref.flag = self.data_ref.get_flag_curve(self.flagname, self.dssel.section)
        #for i in self.images:
        #    i.otype = image.otype
        if image.rall == True:
            for i in self.images:
                i.rangei = image.rangei
                i.ranges = image.ranges
        if image.eall == True:
            for i in self.images:
                i.excluded = image.excluded
        for i in self.images:
            i.frangei = image.frangei
            i.franges = image.franges
        try:
            self.show_data(image.x, image.y, self.data_ref.flag)
        except:
            pass

    def preflag(self):
        filename = getopenfilename(self, _("Open"), "")
        if not str(filename[0]):
            return -1
        else:
            #try:
            self.flagname = str(filename[0])
            self.data_ref.flag = self.data_ref.get_flag_curve(self.flagname, self.dssel.section)
            self.properties_changed()
            #except:
            #    msgBox = QMessageBox()
            #    msgBox.setText("Wrong file!")
            #    msgBox.exec_()
            #    return -1

    def get_gmedian(self):
        ldata = []
        liran = []
        lsran = []
        lexcl = []
        for i in enumerate(self.images):
            if self.imagelist.item(i[0]).checkState() == 2:
                ldata.append(i[0])
                liran.append(i[1].rangei)
                lsran.append(i[1].ranges)
                lexcl.append(i[1].excluded)
        if len(ldata) != 0:
            self.data_ref.dssel = [self.dssel.feed, self.dssel.section, self.dssel.polar]
            self.data_ref.gmed = self.data_ref.get_median_data(ldata, self.dssel.section, self.dssel.polar, liran, lsran, lexcl)
        else:
            return -1

    def fit_win(self):
        self.fwindow = FitWindow()
        #try:
        self.get_gmedian()
        self.fwindow.get_data(self.data_ref, self.images[0].frangei, self.images[0].franges)
        self.fwindow.show()
        #except:
        #    msgBox = QMessageBox()
        #    msgBox.setText("Selection empty!")
        #    msgBox.exec_()
        #    return -1

    def apply_fit(self):
        msgBox = QMessageBox()
        msgBox.setText("Apply corrections?")
        msgBox.setInformativeText("Select to which files will be applied the correction.")
        CancelButton = msgBox.addButton("Cancel", msgBox.RejectRole)
        SelectButton = msgBox.addButton("Select", msgBox.NoRole)
        AllButton = msgBox.addButton("All", msgBox.YesRole)
        #msgBox.setDefaultButton(QMessageBox.Cancel)
        msgBox.exec_()
        if msgBox.clickedButton() == CancelButton:
            return -1
        elif msgBox.clickedButton() == AllButton:
            filelist = None
        elif msgBox.clickedButton() == SelectButton:
            flret = getopenfilenames(self, _("Select file list"), self.data_ref.dir_name)[0]
            filelist = []
            for f in flret:
                filelist.append((basename(str(f)), dirname(str(f))))
            msgBox = QMessageBox()
            msgBox.setText("Select the correction file")
            msgBox.addButton(QMessageBox.Ok)
            msgBox.exec_()

        filename = getopenfilename(self, _("Correction file"), self.data_ref.dir_name+"/"+basename(normpath(self.data_ref.dir_name)+"_fit."+self.data_ref.files_type))
        try:
            self.data_ref.applycorr(str(filename[0]), filelist)
        except:
            msgBox = QMessageBox()
            msgBox.setText("Not a correction file!")
            msgBox.exec_()
            return -1

class FitWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        for p in sys.path:
            if exists(p+'/data/DW.png'):
                icon_path = p+'/data/DW.png'
                break
            if exists(p+'/dw/data/DW.png'):
                icon_path = p+'/dw/data/DW.png'
                break
        self.setWindowIcon(get_icon(icon_path))
        self.setWindowTitle(APP_NAME)
        self.resize(QSize(1024, 768))
        self.data = None

    def get_data(self, data, begin, end):
        self.data = data
        self.begin = begin
        self.end = end
        self.setup()

    def setup_central_widget(self, widget, toolbar):
        self.mainwidget = widget(self, toolbar)
        self.setCentralWidget(self.mainwidget)

    def setup(self):
        help_menu = self.menuBar().addMenu("?")
        about_action = create_action(self, _("About..."),
                                     icon=get_std_icon('MessageBoxInformation'),
                                     triggered=self.about)
        add_actions(help_menu, (about_action,))

        self.toolbar = self.addToolBar("Image")
        self.setup_central_widget(FitWidget, self.toolbar)
        self.mainwidget.open_setup(self.data, self.begin, self.end)

    def about(self):
        QMessageBox.about( self, _("About ")+APP_NAME,
                          """<b>%s</b><br>
                          v%s<p>
                          Copyright &copy; 2014 IRA-INAF<br><br>
                          %s
                          """ % \
                          (APP_DESCRIPTION, dwdata.dw_version(), LICENSE))

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        for p in sys.path:
            if exists(p+'/data/DW.png'):
                icon_path = p+'/data/DW.png'
                break
            if exists(p+'/dw/data/DW.png'):
                icon_path = p+'/dw/data/DW.png'
                break
        self.setWindowIcon(get_icon(icon_path))
        self.setWindowTitle(APP_NAME)
        self.resize(QSize(1024, 768))
        self.status = self.statusBar()
        self.setup()

    def setup_central_widget(self, widget, toolbar):
        self.mainwidget = widget(self, toolbar)
        self.setCentralWidget(self.mainwidget)

    def setup(self):
        file_menu = self.menuBar().addMenu(_("File"))
        open_action = create_action(self, _("Open..."),
                                    shortcut="Ctrl+O",
                                    icon=get_icon('fileopen.png'),
                                    tip=_("Open an acquisition directory"),
                                    triggered=self.open)
        #apply_action = create_action(self, _("Apply"),
        #                             shortcut="Ctrl+A",
        #                             icon=get_icon('fileopen.png'),
        #                             tip=_("Open an acquisition directory"),
        #                             triggered=self.apply)
        quit_action = create_action(self, _("Quit"),
                                    shortcut="Ctrl+Q",
                                    icon=get_std_icon("DialogCloseButton"),
                                    tip=_("Quit application"),
                                    triggered=self.close)
        add_actions(file_menu, (open_action, None, quit_action))
        help_menu = self.menuBar().addMenu("?")
        about_action = create_action(self, _("About..."),
                                     icon=get_std_icon('MessageBoxInformation'),
                                     triggered=self.about)
        add_actions(help_menu, (about_action,))

        main_toolbar = self.addToolBar("Main")
        add_actions(main_toolbar, (open_action, ))

        self.toolbar = self.addToolBar("Image")

    def about(self):
        QMessageBox.about( self, _("About ")+APP_NAME,
                          """<b>%s</b><br>
                          v%s<p>
                          Copyright &copy; 2014 IRA-INAF<br><br>
                          %s
                          """ % \
                          (APP_DESCRIPTION, dwdata.dw_version(), LICENSE))

    def _open(self):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        dirname = getexistingdirectory(self, _("Open"), "",
                                       options=QFileDialog.ShowDirsOnly)
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
        if dirname:
            self.data = dwdata.DWObs()
            self.data.open_dir(dirname)
            cfeeds.set(self.data.list2choices(self.data.sections.keys()))
            csections.set(self.data.list2choices(self.data.sections.values()[0]))
            cpolars.set(self.data.list2choices(self.data.polars))
            self.setup_central_widget(MainWidget, self.toolbar)
            #try:
            #    self.data.dw_io.new_file(dirname, self.data.flist, 4, 8192)
            #except:
            #    print "file exists"
            self.mainwidget.open_setup(self.data)
            self.setWindowTitle(APP_NAME+" - "+dirname)

    def open(self):
        try:
            self._open()
        except:
            msgBox = QMessageBox()
            msgBox.setText("Wrong type of directory!")
            msgBox.exec_()
            return -1

if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    window = MainWindow()
    window.show()
    app.exec_()
