from PyQt5 import QtWidgets, QtCore, uic
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
            FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar)
from matplotlib.widgets import RectangleSelector
from collections import OrderedDict

import tweezers
from tweezers.plot.SegmentSelectorUi import Ui_MainWindow


class SpanSelector(RectangleSelector):
    """
    Customized :class:`RectangleSelector` to allow span selection that is adjustable with handles.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # patching handles for the selection
        self._corner_handles.artist.remove()
        self._edge_handles.artist.remove()

        self._edge_order = ['W', 'E']
        self.artists = [self.to_draw,
                        self._center_handle.artist,
                        self._edge_handles.artist]
        # self.artists = [self.to_draw]

    @property
    def edge_centers(self):
        xe, ye = super().edge_centers
        return (xe[0], xe[2]), (ye[0], ye[2])

    @property
    def extents(self):
        return super().extents

    @extents.setter
    def extents(self, extents):
        extents = (*extents[0:2], *self.ax.get_ylim())
        super(SpanSelector, self.__class__).extents.fset(self, extents)


class DataManager:
    tLim = None
    tc = None
    t = None
    segCounter = dict()

    def __init__(self, path, sourceType=tweezers.io.TxtBiotecSource):
        self.path = path
        self.sourceType = sourceType

    @staticmethod
    def getSourceTypes():
        return OrderedDict([
            ('TxtBiotecSource', tweezers.io.TxtBiotecSource),
            ('TdmsCTrapSource', tweezers.io.TdmsCTrapSource),
            ('TxtMpiSource', tweezers.io.TxtMpiSource)
        ])

    def loadCollection(self, callback):
        self.callback = callback

        # create thread
        self.thread = QtCore.QThread()
        self.dataLoader = DataLoader(path=self.path, sourceType=self.sourceType)

        # connect signal
        self.dataLoader.completed.connect(self.onCollectionLoaded)
        # move data loader to thread
        self.dataLoader.moveToThread(self.thread)
        self.dataLoader.finished.connect(self.thread.quit)
        self.thread.started.connect(self.dataLoader.loadCollection)
        self.thread.start()

    def onCollectionLoaded(self, tc):
        self.tc = tc.flatten()
        self.setT(0)
        self.callback()

    def setT(self, idx):
        self.t = self.tc[idx]
        self.tLim = None

    def getIds(self):
        return self.tc.keys()

    def getForceColumns(self):
        res = [item for item in self.t.data.columns if item.lower().endswith('force')]
        return res

    def getDistColumns(self):
        res = [item for item in self.t.data.columns if (item.lower().endswith('dist')
                                                        or item.lower().endswith('ext')
                                                        or item in ['dist1', 'dist2'])]     # c-trap compatibility
        return res

    def getAxesLabel(self, name):
        if name in self.getForceColumns():
            return 'Force [pN]'
        elif name in self.getDistColumns():
            return 'Distance [nm]'
        else:
            return None

    def plotTime(self, ax, yAxis):
        ax.clear()
        # plot data
        d = self.t.avData
        ax.plot(d.time, d[yAxis], '.', markersize=3)
        ax.set_xlabel('Time [s]', fontsize=12)
        ax.set_ylabel(self.getAxesLabel(yAxis), fontsize=12)

        # plot segments
        for seg in self.t.segments.values():
            ax.axvspan(seg['tmin'], seg['tmax'], facecolor='red', alpha=0.2)

    def plotDistance(self, ax, xAxis, yAxis):
        ax.clear()
        # plot data
        d = self.t.avData
        # is there a selection?
        if self.tLim:
            d = d.query('{} <= time <= {}'.format(*self.tLim))
        # plot
        ax.plot(d[xAxis], d[yAxis], '.', markersize=3)
        ax.set_xlabel(self.getAxesLabel(xAxis), fontsize=12)
        ax.set_ylabel(self.getAxesLabel(yAxis), fontsize=12)

    def _getBeadId(self, t):
        try:
            return t.meta.beadId
        except KeyError():
            return t.meta.id

    def saveSegment(self, name=None):
        tmin, tmax = self.tLim[:2]
        if not name:
            idx = self._getBeadId(self.t)
            if idx not in self.segCounter.keys():
                self.segCounter[idx] = 0
            name = '{}'.format(self.segCounter[idx])
            self.segCounter[idx] += 1
        # check if segment already exists
        if name in self.t.segments.keys():
            # update existing segment
            self.t.segments[name].tmin = tmin
            self.t.segments[name].tmax = tmax
        else:
            # create new segment
            self.t.addSegment(tmin=tmin, tmax=tmax, name=name)
        return name

    def clearSegments(self):
        self.t.segments.clear()

    def removeSegment(self, segId):
        self.t.segments.pop(segId)

    def getSegmentNames(self):
        return self.t.segments.keys()

    def getSegmentLimits(self, segId):
        seg = self.t.segments[segId]
        return [seg.tmin, seg.tmax]

    def export(self, callback, path, groupExport=True):
        self.callback = callback

        # create thread
        self.thread = QtCore.QThread()
        self.dataLoader = DataLoader(path=path, tc=self.tc, groupExport=groupExport)

        # connect signal
        self.dataLoader.completed.connect(callback)
        # move data loader to thread
        self.dataLoader.moveToThread(self.thread)
        self.dataLoader.finished.connect(self.thread.quit)
        self.thread.started.connect(self.dataLoader.export)
        self.thread.start()


class DataLoader(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    completed = QtCore.pyqtSignal(object)

    def __init__(self, path=None, sourceType=tweezers.io.TxtBiotecSource, tc=None, groupExport=True):
        super().__init__()
        self.path = path
        self.sourceType = sourceType
        self.groupExport = groupExport
        self.tc = tc

    @QtCore.pyqtSlot()
    def loadCollection(self):
        tc = tweezers.TweezersDataCollection.load(self.path, source=self.sourceType)
        self.completed.emit(tc)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def export(self):
        error = None
        try:
            ac = self.tc.getAnalysis(path=self.path, groupByBead=self.groupExport, onlySegments=True)
            ac.save()
        except Exception as err:
            error = err
        self.completed.emit(error)
        self.finished.emit()


class PlotNavigationToolbar(NavigationToolbar):
    """
    Customized :class:`NavigationToolbar2QT`. Only shows certain buttons.
    """

    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Back', 'Forward', 'Pan', 'Zoom', 'Save', None)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QtCore.QSize(18, 18))
        self.setFixedHeight(18)
        self.setStyleSheet("QToolBar { border: 0px }")


class SegmentSelector(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi('/Users/christophehrlich/Documents/Python/tweezers/tweezers/plot/SegmentSelectorUi.ui', self)
        self.setupUi(self)

        # access settings object: organization: Grill Lab; application: Tweezers
        self.settings = QtCore.QSettings('Grill Lab', 'Tweezers')
        self.settings.beginGroup('segmentSelector')

        self._setupGeneralUi()
        self._setupFigureUi()
        self._setupSettingsUi()
        self._setupSegmentUi()

        self.setDataLoaded(False)

        self.show()

    def _setupGeneralUi(self):
        """
        Setup general UI stuff
        """

        # set window size and position
        storedGeometry = self.settings.value('windowGeometry', False)
        if storedGeometry:
            self.restoreGeometry(storedGeometry)
        else:
            self.setGeometry(100, 50, 1000, 730)

        self.setWindowTitle('Segment Selector')

    def _setupFigureUi(self):
        """
        Setup the figure UI
        """

        # setup collection controls
        self.collectionNextBtn.clicked.connect(self.onCollectionNext)
        self.collectionPrevBtn.clicked.connect(self.onCollectionPrev)
        self.collectionCmb.currentIndexChanged[int].connect(self.onSelectData)

        # set mpl options
        mpl.pyplot.style.use('fivethirtyeight')
        params = {'lines.linewidth': 2}
        mpl.rcParams.update(params)

        # create time figure with selector
        self.timeCanvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.axTime = self.timeCanvas.figure.add_subplot(1, 1, 1)
        self.axTime.tick_params(labelsize=12)
        self.timeCanvas.figure.tight_layout()
        # create time toolbar
        self.timeToolbar = PlotNavigationToolbar(self.timeCanvas, self)
        # add span selector for segments
        self.selector = SpanSelector(self.axTime, self.onSegmentSpan, drawtype='box',
                                     interactive=True, useblit=True,
                                     rectprops={'alpha': 0.5, 'facecolor': 'red'})

        # create force-distance figure
        self.distCanvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.axDist = self.distCanvas.figure.add_subplot(1, 1, 1)
        self.axDist.tick_params(labelsize=12)
        self.axDist.figure.tight_layout()
        # create dist toolbar
        self.distToolbar = PlotNavigationToolbar(self.distCanvas, self)

        self.figureBx.addWidget(self.timeToolbar)
        self.figureBx.addWidget(self.timeCanvas)
        self.figureBx.addWidget(self.distToolbar)
        self.figureBx.addWidget(self.distCanvas)

    def _setupSettingsUi(self):
        """
        Setup "Settings" tab UI
        """

        sourceTypes = list(DataManager.getSourceTypes().keys())
        self.sourceTypeCmb.addItems(sourceTypes)

        # source type combo box
        selectedType = self.settings.value('dataSourceType', sourceTypes[0])
        idx = 0
        if selectedType in sourceTypes:
            idx = sourceTypes.index(selectedType)
        self.sourceTypeCmb.setCurrentIndex(idx)

        # group by bead checkbox
        self.groupExportBeadCbx.setChecked(self.settings.value('groupExport', True))

        # axis selction combo boxes
        self.timeYAxisCmb.currentIndexChanged[int].connect(self.onSelectTimeYAxis)
        self.distXAxisCmb.currentIndexChanged[int].connect(self.onSelectDistXAxis)
        self.distYAxisCmb.currentIndexChanged[int].connect(self.onSelectDistYAxis)

    def _setupSegmentUi(self):
        """
        Setup "Segments" tab UI
        """

        self.quitBtn.clicked.connect(self.onExit)
        self.loadDirectoryBtn.clicked.connect(self.onLoadDirectory)

        self.clearSegmentBtn.clicked.connect(self.onClearSegments)
        self.saveSegmentBtn.clicked.connect(self.onSaveSegment)
        self.exportSegmentBtn.clicked.connect(self.onExport)
        self.segmentLst.selectionModel().selectionChanged.connect(self.onSegmentSelect)
        self.removeSegmentBtn.clicked.connect(self.onRemoveSegment)

    def setDataLoaded(self, loaded):
        """
        Set UI state for no loaded data.

        Args:
            loaded: bool
        """

        disabled = not loaded
        self.dataBx.setDisabled(disabled)
        self.plotOptionsGrp.setDisabled(disabled)
        self.clearSegmentBtn.setDisabled(disabled)
        self.segmentIdTxt.setDisabled(disabled)
        self.saveSegmentBtn.setDisabled(disabled)
        self.segmentLst.setDisabled(disabled)
        self.exportSegmentBtn.setDisabled(disabled)

    def onExit(self):
        """
        Event handler for the "Quit" button. Use in general to quit the application
        """

        self.close()

    def onLoadDirectory(self):
        """
        Event handler for the load directory button.
        """

        lastImportDir = self.settings.value('importDir', '')
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", lastImportDir)
        # sourceType = self.sourceTypeCmb.currentText()
        sourceType = tweezers.io.TxtBiotecSource
        if path:
            self.settings.setValue('importDir', path)
            self.statusbar.showMessage('Loading directory ...')
            self.setDataLoaded(False)
            self.data = DataManager(path, sourceType=sourceType)
            self.data.loadCollection(self.onDirectoryLoaded)

    def onDirectoryLoaded(self):
        """
        Event handler for when new directory was loaded.
        """

        # populate settings
        # time y axis selection combo
        items = [*self.data.getForceColumns(), *self.data.getDistColumns()]
        self._populateCmbAndSelect(self.timeYAxisCmb, items, self.settings.value('timeYAxis', items[0]))

        # dist x axis selection combo
        items = self.data.getDistColumns()
        self._populateCmbAndSelect(self.distXAxisCmb, items, self.settings.value('distXAxis', items[0]))

        # dist y axis selection combo
        items = self.data.getForceColumns()
        self._populateCmbAndSelect(self.distYAxisCmb, items, self.settings.value('distYAxis', items[0]))

        # get all ids and add them to the collectionCmb
        # this will also trigger the onSelectData event handler
        for idx in self.data.getIds():
            self.collectionCmb.addItem(idx)
        self.statusbar.showMessage('Directory loaded')

    def _populateCmbAndSelect(self, cmb, items, selectedItem):
        """
        Helper function to populate the combo boxes for the settings.

        Args:
            cmb: Combo box to populate
            items: List of items to put into combo box
            selectedItem: Item to select, if it is not in `items`, the first item in `items` is selected
        """

        cmb.blockSignals(True)
        cmb.clear()
        # using a loop allows for None entries to becoma a separator
        for item in items:
            cmb.addItem(item)
        idx = 0
        if selectedItem in items:
            idx = items.index(selectedItem)
        cmb.setCurrentIndex(idx)
        cmb.blockSignals(False)

    def onSelectData(self, idx):
        """
        Event handler for new selected data set.

        Args:
            idx: Index of the data set selected.
        """

        # set current dataset
        self.data.setT(idx)
        # update data display
        self.showData()
        # enable GUI
        self.setDataLoaded(True)
        self.statusbar.showMessage('Trial "{}" loaded'.format(self.collectionCmb.currentText()))

    def showData(self):
        """
        Update all the plots and the segment list.
        """

        self.plotTime()
        self.plotDist()
        self.updateSegmentList()

    def plotTime(self):
        """
        Populate the time plot.
        """

        self.data.plotTime(self.axTime, self.timeYAxisCmb.currentText())
        self.timeCanvas.figure.tight_layout()
        # update toolbar home, forward etc buttons
        self.timeToolbar.update()
        self.timeCanvas.draw()

    def plotDist(self):
        """
        Populate the distance plot.
        """

        self.data.plotDistance(self.axDist, self.distXAxisCmb.currentText(), self.distYAxisCmb.currentText())
        self.distCanvas.figure.tight_layout()
        self.distToolbar.update()
        self.distCanvas.draw()

    def onSegmentSpan(self, eclick, erelease):
        """
        Event handler for the span selector that actually selects the segments in the time-plot.

        Args:
            eclick: event data for click event
            erelease: event data for the release event
        """

        # get click limits
        self.data.tLim = sorted([eclick.xdata, erelease.xdata])
        # update plot
        self.plotDist()
        self.statusbar.showMessage('Segment: {:.1f} s - {:.1f} s'.format(*self.data.tLim))

    def updateSegmentList(self):
        """
        Update the list of segments.
        """

        self.segmentLst.blockSignals(True)
        self.segmentLst.clear()
        self.segmentLst.addItems(self.data.getSegmentNames())
        self.segmentLst.blockSignals(False)

    def onClearSegments(self):
        """
        Event handler for the "Clear Segments" button. Clears all the segments for the current :class:`.TweezersData`.
        """

        # delete all segments and update the plot
        self.data.clearSegments()
        self.showData()
        self.statusbar.showMessage('Segments cleared')

    def onSaveSegment(self):
        """
        Event handler for the "Save Segment" button. Saves the currently selected segment.
        """

        # ToDo: add warning for empty segment
        # make safe segment id from input
        # inspired by https://gist.github.com/seanh/93666
        segId = self.segmentIdTxt.text().strip()
        keepcharacters = ('_', '-')
        segId = "".join(c for c in segId if c.isalnum() or c in keepcharacters)
        self.segmentIdTxt.setText('')
        # save segment
        segId = self.data.saveSegment(name=segId)
        # update the GUI
        self.showData()
        self.statusbar.showMessage('Segment "{}" added'.format(segId))

    def onSegmentSelect(self, selected, deselected):
        """
        Event handler for selection of a segment from the segment list.

        Args:
            selected: Newly selected item
            deselected: Deselected item
        """

        # get selected item text
        selItem = None
        if selected.indexes():
            selItem = selected.indexes()[0].data()

        if selItem:
            # enter edit mode
            self.removeSegmentBtn.setDisabled(False)
            self.segmentIdTxt.setText(selItem)
            self.selector.extents = self.data.getSegmentLimits(selItem)
        else:
            # leave edit mode
            self.removeSegmentBtn.setDisabled(True)
            self.segmentIdTxt.setText('')

        pass

    def onRemoveSegment(self):
        """
        Event handler for removing a segment from the segment list.
        """

        segId = self.segmentLst.currentItem().text()
        self.data.removeSegment(segId)
        self.segmentIdTxt.setText('')
        self.showData()
        self.statusbar.showMessage('Segment "{}" removed'.format(segId))

    def onCollectionNext(self):
        """
        Event handler for the "Next Element" button.
        """

        idx = self.collectionCmb.currentIndex() + 1
        if idx < self.collectionCmb.count():
            self.collectionCmb.setCurrentIndex(idx)

    def onCollectionPrev(self):
        """
        Event handler for the "Previous Element" button.
        """

        idx = self.collectionCmb.currentIndex() - 1
        if idx >= 0:
            self.collectionCmb.setCurrentIndex(idx)

    def onSelectTimeYAxis(self, idx):
        """
        Event Handler for y-axis selection combo box for the time plot.
        """

        self.plotTime()

    def onSelectDistXAxis(self, idx):
        """
        Event Handler for x-axis selection combo box for the distance plot.
        """

        self.plotDist()

    def onSelectDistYAxis(self, idx):
        """
        Event Handler for y-axis selection combo box for the distance plot.
        """

        self.plotDist()

    def onExport(self):
        """
        Event handler for the "Export" button. Triggers exporting / saving of the analysis files.
        """

        lastExportDir = self.settings.value('exportDir', '')
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", lastExportDir)
        if path:
            self.settings.setValue('exportDir', path)
            groupExport = self.groupExportBeadCbx.isChecked()
            self.settings.setValue('groupExport', groupExport)
            self.statusbar.showMessage('Saving analysis files...')
            self.data.export(self.onExported, path, groupExport=groupExport)

    def onExported(self, error):
        """
        Event handler for when data was exported.
        """

        if error:
            self.displayError('Could not save analysis files!', error)
        self.statusbar.showMessage('Segments exported')

    def closeEvent(self, event):
        """
        Event handler for closing the window. Used to store some settings before exiting.
        """

        self.settings.setValue('windowGeometry', self.saveGeometry())
        self.settings.setValue('dataSourceType', self.sourceTypeCmb.currentText())
        self.settings.setValue('groupExport', self.groupExportBeadCbx.isChecked())
        self.settings.setValue('timeYAxis', self.timeYAxisCmb.currentText())
        self.settings.setValue('distXAxis', self.distXAxisCmb.currentText())
        self.settings.setValue('distYAxis', self.distYAxisCmb.currentText())

    def displayError(self, message, error):
        """
        Display a dialog box with an error message to the user.

        Args:
            message (str): message to display
            error (error): error returned by the exception, its message will also be displayed
        """

        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Error')
        msg.setText(message)
        if error:
            msg.setInformativeText('{0}'.format(error))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


def runSegmentSelector():
    """
    Function to run the :class:`.SegmentSelector`. It starts the required QtApplication and loads the
    :class:`.SegmentSelector` widget.
    """

    # might require setting backend properly
    if not QtWidgets.QApplication.instance():
        qapp = QtWidgets.QApplication([])
    else:
        qapp = QtWidgets.QApplication.instance()
    app = SegmentSelector()
    app.show()
    qapp.setActiveWindow(app)
    qapp.exec_()
    qapp.quit()
