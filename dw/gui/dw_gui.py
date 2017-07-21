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
dw.gui.dw_gui
================

Implement the GUI main window and menu

Classes
-------
* MainWindow - Implement the GUI main window and menu
"""

import sys
from os.path import exists
from os import system
from os.path import splitext

#import numpy as np
from guidata.qt.QtGui import QMainWindow, QMessageBox, QPushButton
from guidata.qt.QtCore import QSize
from guidata.qt.compat import getopenfilename
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guiqwt.config import _

import dw.core.data_def as dwdata
import dw.gui.widgets as dwwidg


APP_NAME = _("Dish Washer")
APP_DESCRIPTION = ("RFI cleaning tool for single dish radiotelescopes data")
LICENSE = """Released under the terms of GNU GPL v.3 <br>
             or (at your option) any later version"""




class MainWindow(QMainWindow):

    """Implement the GUI main window and menu

    Methods
    -------
    * __init__: instantiate the main window and setup some parameter
    * setup_central_widget: instantiate and setup the central widget
    * set_menu: build the menu
    * set_flag_toolbar: build the flagging toolbar
    * about: about dialog
    * not_implemented: not implemented functionality dialog
    * open_file: open data file
    * close_file: lose data file
    * checked_items_to_flag
    * del_selected_flag_image_item
    * merge_selected_flag_image_items
    * deflag_selected_flag_image_items
    """

    def __init__(self):
        """Instantiate the main window and setup some parameter"""
        QMainWindow.__init__(self)
        for p in sys.path:
            if exists(p+'/data/'):
                self.icon_path = p+'/data/'
                break
            if exists(p+'/dw/data/'):
                self.icon_path = p+'/dw/data/'
                break
        self.setWindowIcon(get_icon(self.icon_path+'DW.png'))
        self.setWindowTitle(APP_NAME)
        self.resize(QSize(1024, 768))

        # Welcome message in statusbar:
        status = self.statusBar()
        status.showMessage(_("Welcome to Dish Washer! Open a file to start."), 7000)

        # File menu & Main toolbar
        self.set_menu()

        # Set central widget:
        self.toolbar = self.addToolBar("Image")

        # Set central widget:
#        self.setup_central_widget(self.toolbar)

#        self.set_flag_toolbar()

    def setup_central_widget(self, widget, toolbar):
        """Instantiate and setup the central widget

        toolbar: PyQt4.QtGui.QToolBar
        """
        self.mainwidget = widget(self, toolbar, self.icon_path)
        self.setCentralWidget(self.mainwidget)

    def set_menu(self):
        """Build the menu"""

        file_menu = self.menuBar().addMenu(_("File"))
        open_action = create_action(self, _("Open file..."),
                                    shortcut="Ctrl+O",
                                    icon=get_icon('fileopen.png'),
                                    tip=_("Open a data file"),
                                    triggered=self.open_file)
        close_action = create_action(self, _("Close..."),
                                    shortcut="Ctrl+C",
                                    icon=get_icon('fileclose.png'),
                                    tip=_("Close a data file"),
                                    triggered=self.close_file)
        quit_action = create_action(self, _("Quit"),
                                    shortcut="Ctrl+Q",
                                    icon=get_std_icon("DialogCloseButton"),
                                    tip=_("Quit application"),
                                    triggered=self.close_dw)
        add_actions(file_menu, ( open_action, None, close_action, None, quit_action))

        #Tools menu
        Tool_menu = self.menuBar().addMenu(_("Tools"))
#        RFI1_action = create_action(self, _("RFI flag algorithm 1"),
#                                    shortcut="Ctrl+1",
#                                    icon=get_icon(''),
#                                    tip=_("Detect RFI - alg 1"),
#                                    triggered=self.not_implemented)
        Ipython_action = create_action(self, _("Ipython console"),
                                    shortcut="Ctrl+I",
                                    icon=get_icon('python.png'),
                                    tip=_("Launch Ipython console"),
                                    triggered=self.embed_ipython)
        bpc_action = create_action(self, _("Band pass correction tool"),
                                   shortcut="Ctrl+B",
                                   icon=get_icon('sticks.png'),
                                   tip=("Launch the tool for the band pass correction"),
                                   triggered=self.bpcexec)
        bpc_open_file = create_action(self, _("Open a correction file"),
                                      shortcut="Ctrl+N",
                                      icon=get_icon('fileopen.png'),
                                      tip=("Open a file generated by the bandpass correction tool"),
                                      triggered=self.open_corr_file)
        bpc_toggle = create_action(self, _("Apply/Unapply correction"),
                                   shortcut="Ctrl+M",
                                   icon=get_icon('fileimport.png'),
                                   tip=("Toggle use of correction on data"),
                                   triggered=self.toggle_corr)
        freq_off_action = create_action(self, _("Set freq scale offset"),
                                    shortcut="Ctrl+0",
                                    icon=get_icon('vcursor.png'),
                                    tip=_("Set freq scale offset"),
                                    triggered=self.freq_off)
        mir_x_action = create_action(self, _("Mirror x axis"),
                                    shortcut="Ctrl+X",
                                    icon=get_icon('axes.png'),
                                    tip=_("Mirror x axis"),
                                    triggered=self.mir_x)
        #rplot_time_action = create_action(self, _("Recurrence plot (time)"),
        #                            icon=get_icon(''),
        #                            tip=_("Recurrence plot widget"),
        #                            triggered=self.rplot_widget_time)
        #rplot_freqs_action = create_action(self, _("Recurrence plot (frequencies)"),
        #                            icon=get_icon(''),
        #                            tip=_("Recurrence plot widget"),
        #                            triggered=self.rplot_widget_freqs)

        add_actions(Tool_menu, ( None, Ipython_action, None, bpc_action, bpc_open_file, bpc_toggle))#, None, freq_off_action, mir_x_action))#, None, rplot_time_action, rplot_freqs_action))

        #RFI flag menu
        flag_menu = self.menuBar().addMenu(_("Flagging"))
        self.flag_action = create_action(self, _("Flag..."),
                                    shortcut="Ctrl+F",
                                    icon=get_icon(self.icon_path+'flag_ok.png'),
                                    tip=_("Flag..."),
                                    triggered=self.checked_items_to_flag)

        self.deflag_isect_action = create_action(self, _("Deflag intersected"),
                                                 shortcut="Ctrl+G",
                                                 icon=get_icon(self.icon_path+'flag_sel_del.png'),
                                                 tip=_("Remove flags intersected by element"),
                                                 triggered=self.deflag_intersected)

        deflag_action = create_action(self, _("Deflag..."),
                                    shortcut="Ctrl+Shift+F",
#                                    icon=get_icon('fileopen.png'),
                                    tip=_("Deflag..."),
                                    triggered=self.deflag_selected_flag_image_items)

        merge_flag_action = create_action(self, _("Merge selected"),
#                                    shortcut="Ctrl+F",
#                                    icon=get_icon('fileopen.png'),
                                    tip=_("Flag..."),
                                    triggered=self.merge_selected_flag_image_items)

        del_flag_action = create_action(self, _("Delete selected"),
#                                    shortcut="Ctrl+F",
                                    icon=get_icon(self.icon_path+'flag_del.png'),
                                    tip=_("Delete selected flagging matrices"),
                                    triggered=self.del_selected_flag_image_item)

        flag_widget_action = create_action(self, _("Manual Flag Widget"),
                                           icon=get_icon(self.icon_path+'flag.png'),
                                           tip=_("Open a flagging widget"),
                                           triggered=self.flag_widget)

        propag_flag_action = create_action(self, _("Propagate flag table to files"),
                                           icon=get_icon(self.icon_path+'flag_copy.png'),
                                           tip=("Propagate the file table to other files"),
                                           triggered=self.propag_flag_table)

        propag_feeds_action = create_action(self, _("Propagate flag feed -> feed"),
                                            icon=get_icon(self.icon_path+'flag_copy.png'),
                                            tip=("Propagate a flag feed to feed"),
                                            triggered=self.propag_feeds)

        auto_flag_action = create_action(self, _("Auto RFI detection"),
                                           tip=_("Run auto RFI detection"),
                                           triggered=self.rfi_dect_action)


        add_actions(flag_menu, ( self.flag_action, self.deflag_isect_action,
#                                deflag_action, merge_flag_action,
                                del_flag_action, flag_widget_action, None, propag_flag_action,
                                propag_feeds_action,
                                None, auto_flag_action))

        # Help menu
        help_menu = self.menuBar().addMenu("?")
        about_action = create_action(self, _("About..."),
                                     icon=get_std_icon('MessageBoxInformation'),
                                     triggered=self.about)
        add_actions(help_menu, (about_action,))

        main_toolbar = self.addToolBar("Main")

        add_actions(main_toolbar, ( open_action, ))


    def set_flag_toolbar(self):
        """Build the flagging toolbar"""

        self.flag_toolbar = self.addToolBar("Flag")
        add_actions(self.flag_toolbar, ( self.flag_action, self.deflag_isect_action))

    def about(self):
        """About dialog"""
        QMessageBox.about(self, APP_NAME,
              """<b>%s</b><br>
              v%s<p>
              Copyright &copy; 2014 IRA-INAF<br><br>
              %s
              """ % \
              (APP_DESCRIPTION, dwdata.dw_version(), LICENSE))

    def embed_ipython(self):
        from IPython import embed
        embed()

#        try:
#            get_ipython
#        except NameError:
#            from IPython.terminal.embed import InteractiveShellEmbed
#            ipshell = InteractiveShellEmbed()
#            # Now ipshell() will open IPython anywhere in the code
#            ipshell()
#        else:
#            # Define a dummy ipshell() so the same code doesn't crash inside an
#            # interactive IPython
#            def ipshell(): pass

    def not_implemented(self):
        """Not implemented function dialog"""
        QMessageBox.about(self, "Sorry!", "Not yet implemented...")

#------I/O
    def _open_file(self):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdout = None
        filename, _filter = getopenfilename(self, _("Open"), "")
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err

        if filename:
            extension = splitext(str(filename))[1]
            if extension not in ['.fits', '.hdf5', '.hdf', '.h5']:
                msgBox = QMessageBox()
                msgBox.setText("Wrong file type!")
                msgBox.exec_()
                return -1

            if extension == '.fits':
                file_type = "fits"
            elif extension == (".hdf5" or ".h5" or ".hdf"):
                msgBox = QMessageBox()
                msgBox.setText("Are data spectrometric or spectropolarimetric?")
                msgBox.addButton(QPushButton('Spect'), QMessageBox.NoRole)
                msgBox.addButton(QPushButton('Polar'), QMessageBox.YesRole)
                ret = msgBox.exec_()
                if ret == False:
                    widg_type = 0
                    file_type = 'hdf'
                elif ret == True:
                    widg_type = 1
                    file_type = 'hdf_pola'

            self.data = dwdata.DWData()
            self.data.open_data(filename, file_type)
            if file_type == 'fits':
                if self.data.data_type_dict[0][0] == 'simple':
                    widg_type = 0
                elif self.data.data_type_dict[0][0] == 'stokes':
                    widg_type = 1

            if widg_type == 0:
                self.setup_central_widget(dwwidg.MainWidget, self.toolbar)
            elif widg_type == 1:
                self.setup_central_widget(dwwidg.PolaViewerWidget, self.toolbar)
            self.set_flag_toolbar()

            self.mainwidget.open_setup(self.data)
            self.setWindowTitle(APP_NAME+" - "+filename)
#            self.mainwidget.lut_setup()
#            self.mainwidget.refresh_list()

    def open_file(self):
        """Open data file"""
        try:
            for i in self.mainwidget.imagewidget.plot.items:
                if dwwidg.is_flag(i):
                    msgBox = QMessageBox()
                    msgBox.setText("There are not saved flags! Are you sure to discard them?")
                    msgBox.addButton(QMessageBox.Cancel)
                    msgBox.addButton(QMessageBox.Ok)
                    msgBox.setDefaultButton(QMessageBox.Cancel)
                    ret = msgBox.exec_()
                    if ret == QMessageBox.Cancel:
                        return -1
                    elif ret == QMessageBox.Ok:
                        break
        except:
            pass

        self.toolbar.clear()
        try:
            self.flag_toolbar.close()
        except:
            pass
        try:
            self._open_file()
        except:
            msgBox = QMessageBox()
            msgBox.setText("File structure not recognized!")
            msgBox.exec_()
            return -1

    def close_file(self):
        """Close data file"""
        for i in self.mainwidget.imagewidget.plot.items:
            if dwwidg.is_flag(i):
                msgBox = QMessageBox()
                msgBox.setText("There are not saved flags! Are you sure to discard them?")
                msgBox.addButton(QMessageBox.Cancel)
                msgBox.addButton(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                ret = msgBox.exec_()
                if ret == QMessageBox.Cancel:
                    return -1
                elif ret == QMessageBox.Ok:
                    break

        self.mainwidget.close()
        self.toolbar.clear()
        self.flag_toolbar.close()
        self.data.close()
        del self.data
        del self.mainwidget
        self.setWindowTitle(APP_NAME)

    def close_dw(self):
        """Close DW"""
        try:
            for i in self.mainwidget.imagewidget.plot.items:
                if dwwidg.is_flag(i):
                    msgBox = QMessageBox()
                    msgBox.setText("There are not saved flags! Are you sure to discard them?")
                    msgBox.addButton(QMessageBox.Cancel)
                    msgBox.addButton(QMessageBox.Ok)
                    msgBox.setDefaultButton(QMessageBox.Cancel)
                    ret = msgBox.exec_()
                    if ret == QMessageBox.Cancel:
                        return -1
                    elif ret == QMessageBox.Ok:
                        break
            self.close()
        except:
            self.close()

    def checked_items_to_flag(self):
        self.mainwidget.checked_items_to_flag()

    def deflag_intersected(self):
        self.mainwidget.deflag_intersected()

    def del_selected_flag_image_item(self):
        self.mainwidget.del_selected_flag_image_item()

    def merge_selected_flag_image_items(self):
        self.mainwidget.merge_selected_flag_image_items()

    def deflag_selected_flag_image_items(self):
        self.mainwidget.deflag_selected_flag_image_items()

    def flag_widget(self):
        """"""
        self.mainwidget.flag_widget()

    def propag_flag_table(self):
        """"""
        self.mainwidget.propag_flag_table()

    def propag_feeds(self):
        """"""
        self.mainwidget.propag_feeds()

    def freq_off(self):
        self.mainwidget.freq_off_action()

    def mir_x(self):
        self.mainwidget.mir_x_toggle()

    def rplot_widget_time(self):
        self.mainwidget.rplot_widget_time()

    def rplot_widget_freqs(self):
        self.mainwidget.rplot_widget_freqs()

    def rfi_dect_action(self):
        self.mainwidget.rfi_dect_action()

    def bpcexec(self):
        system("bpcgui &")

    def open_corr_file(self):
        self.mainwidget.open_corr_file()

    def toggle_corr(self):
        self.mainwidget.toggle_corr()

if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    window = MainWindow()
    window.show()
    app.exec_()

