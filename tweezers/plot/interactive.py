import sys
import ipywidgets as widgets
from IPython.display import display
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import (
            FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar,
            QtWidgets, QtCore, QtGui)
from matplotlib.widgets import RectangleSelector
from collections import OrderedDict

from tweezers import TweezersData, TweezersDataCollection
from tweezers.io import TxtBiotecSource, TxtMpiSource, TdmsCTrapSource


class CollectionPlot:
    """
    Interactive plot for looking at all datasets in a :class:`tweezers.TweezersCollection` for use in a Jupyter
    notebook.
    """
    
    def __init__(self, data, fcn, **kwargs):
        self.tc = data.copy().flatten()
        self.fcn = fcn
        self.i = 0
        self.n = len(self.tc)
        self.ids = list(self.tc.keys())

        # initialize widgets
        currentLabelDescription = widgets.Label(value='Current ID: ')
        self.currentLabel = widgets.HTML()

        buttonLayout = widgets.Layout(width='40px')
        self.previousButton = widgets.Button(description='<', layout=buttonLayout)
        self.previousButton.on_click(self.previous)
        self.nextButton = widgets.Button(description='>', layout=buttonLayout)
        self.nextButton.on_click(self.next)

        self.datasetDropdown = widgets.Dropdown(options=self.ids, value=self.ids[0])
        self.datasetDropdown.observe(self.datasetDropdownChanged, names='value')

        statusMsgLabel = widgets.Label(value='Status:')
        self.statusMsg = widgets.Label(value='-')
        self.statusMsg.layout.width = '100px'

        display(widgets.VBox([
            widgets.HBox([currentLabelDescription, self.currentLabel]),
            widgets.HBox([self.previousButton, self.datasetDropdown, self.nextButton]),
            widgets.HBox([statusMsgLabel, self.statusMsg])
        ]))

        # make figure
        self.fig, self.ax = plt.subplots(**kwargs)

        self.update()

    def update(self):
        self.statusMsg.value = 'Loading...'
        self.ax.cla()
        self.currentLabel.value = '<b>{}</b>'.format(self.ids[self.i])
        self.fcn(self.tc[self.i], self.ax)
        self.fig.tight_layout()
        self.statusMsg.value = '-'

    def next(self, b):
        if self.i < self.n - 1:
            self.i += 1
            self.datasetDropdown.value = self.ids[self.i]

    def previous(self, b):
        if self.i > 0:
            self.i -= 1
            self.datasetDropdown.value = self.ids[self.i]

    def datasetDropdownChanged(self, change):
        self.i = self.ids.index(change['new'])
        self.update()


class CustomComboBox(QtWidgets.QComboBox):
    """
    Custom combo box that allows addition of a separator by simply passing `None`. This also works when passing lists.
    """

    n = 0

    def addItems(self, items):
        """
        Add a all the items in the given list. Add a separator if an element is `None`.

        Args:
            items (`list` of `str`): strings to add, `None` will become a separator
        """

        for item in items:
            self.addItem(item)

    def addItem(self, item):
        """
        Add a single item to the combo box. If `item` is `None`, a separator will be added.

        Args:
            item (str): string to add or `None` for separator
        """

        if item:
            super().addItem(item)
        else:
            self.insertSeparator(self.n)
        self.n += 1

    def setCurrentItem(self, item):
        """
        Set the current item by its name.

        Args:
            item (str): name of the item to select
        """

        index = self.findText(item)
        if index >= 0:
            self.setCurrentIndex(index)


class TrialComboBox(QtWidgets.QComboBox):
    """
    Combo box to allow selection of the trials in a :class:`.TweezersDataCollection`.
    """

    tToInd = {}
    indToT = {}

    def __init__(self, tc=None):
        """
        Args:
            tc (:class:`.TweezersDataCollection`, optional): data to load in the combo box
        """
        super().__init__()
        if tc:
            self.setTweezersCollection(tc)

    def setTweezersCollection(self, tc):
        """
        Set the current dataset to the given one, allows updating the GUI.

        Args:
            tc (:class:`.TweezersDataCollection`): data set to populate the combo box with
        """

        self.clear()
        cInd, tInd = self._addGroup(tc, 0, 0)
        self.tc = tc.flatten()

    def _addGroup(self, group, cInd, tInd):
        """
        Add all :class:`.TweezersData` objects in a :class:`.TweezersDataCollection` or call this function recursively
        on all nested collections.

        Args:
            group (:class:`.TweezersDataCollection`): collection to add
            cInd: mapping of combo box indices to TweezersData indices
            tInd: mapping of TweezersData indices to combo box indices

        Returns:
            * cInd (:class:`dict`) -- updated mapping
            * tInd (:class:`dict`) -- updated mapping
        """

        for key, value in group.items():
            if isinstance(value, TweezersData):
                self.tToInd[tInd] = cInd
                self.indToT[cInd] = tInd
                self.addItem(key)
                cInd += 1
                tInd += 1
            else:
                cInd, tInd = self._addGroup(value, cInd, tInd)
                self.insertSeparator(cInd)
                cInd += 1

        return cInd, tInd

    def getTIndFromInd(self, index):
        """
        Convert combo box index to :class:`.TweezersData` index.

        Args:
            index (int): index to convert

        Returns:
            int
        """

        return self.indToT[index]

    def next(self):
        """
        Select the next item in the combo box.
        """

        tInd = self.indToT[self.currentIndex()]
        try:
            self.setCurrentIndex(self.tToInd[tInd + 1])
        except KeyError:
            pass

    def previous(self):
        """
        Select the previous item in the combo box.
        """

        tInd = self.indToT[self.currentIndex()]
        try:
            self.setCurrentIndex(self.tToInd[tInd - 1])
        except KeyError:
            pass


class PlotNavigationToolbar(NavigationToolbar):
    """
    Customized :class:`NavigationToolbar2QT`. Only shows certain buttons.
    """

    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Back', 'Forward', 'Pan', 'Zoom', 'Save', None)]


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
    """
    Class to manage the actual :class:`.TweezersDataCollection` and :class:`.TweezersData`. This is an attempt to
    decouple the GUI and the application logic.
    """

    def __init__(self, tc):
        self.tc = tc.flatten()
        self.segCounter = self._setSegmentCounter()
        self.n = 0
        self.setT(0)
        self.timeYAxis = self.getForceColumns()[0]
        self.distXAxis = self.getDistColumns()[0]
        self.distYAxis = self.timeYAxis

    @classmethod
    def load(cls, path, sourceType='TxtBiotecSource'):
        """
        Load data from the given path.

        Args:
            path (`str` or :class:`pathlib.Path`): path to load
            sourceType (str): name of tweezers data source to use for loading the data

        Returns:
            :class:`.DataManager`
        """

        sourceType = cls.getSourceTypes()[sourceType]
        tc = TweezersDataCollection.load(path, source=sourceType)
        return cls(tc)

    def _setSegmentCounter(self):
        counter = dict()
        for key, t in self.tc.items():
            counter[self._getBeadId(t)] = 0
        return counter

    def _getBeadId(self, t):
        try:
            return t.meta.beadId
        except KeyError():
            return t.meta.id

    def setT(self, index):
        self.t = self.tc[index]
        self.tLim = None

    def saveSegment(self, name=None):
        tmin, tmax = self.tLim[:2]
        if not name:
            ide = self._getBeadId(self.t)
            name = '{}'.format(self.segCounter[ide])
            self.segCounter[ide] += 1
        # check if segment already exists
        if name in self.t.segments.keys():
            # update existing segment
            self.t.segments[name].tmin = tmin
            self.t.segments[name].tmax = tmax
        else:
            # create new segment
            self.t.addSegment(tmin=tmin, tmax=tmax, name=name)

    def clearSegments(self):
        self.t.segments.clear()

    @property
    def data(self):
        return self.t.avData

    @property
    def selectedData(self):
        if self.tLim:
            return self.t.avData.query('{} <= time <= {}'.format(*self.tLim))
        else:
            return self.t.avData

    def getForceColumns(self):
        res = [item for item in self.t.data.columns if item.lower().endswith('force')]
        return res

    def getDistColumns(self):
        res = [item for item in self.t.data.columns if (item.lower().endswith('dist')
                                                        or item.lower().endswith('ext'))]
        return res

    def getAxesLabel(self, name):
        if name in self.getForceColumns():
            return 'Force [pN]'
        elif name in self.getDistColumns():
            return 'Distance [nm]'
        else:
            return None

    @staticmethod
    def getSourceTypes():
        return OrderedDict([
            ('TxtBiotecSource', TxtBiotecSource),
            ('TdmsCTrapSource', TdmsCTrapSource),
            ('TxtMpiSource', TxtMpiSource)
        ])

    def plotTime(self, ax):
        t = self.t
        ax.plot(t.avData.time, t.avData[self.timeYAxis], '-', linewidth=0.5, markersize=3)
        # plot segments
        (ymin, ymax) = ax.get_ylim()
        for seg in t.segments.values():
            rect = Rectangle((seg['tmin'], ymin), seg['tmax'] - seg['tmin'], ymax - ymin,
                             facecolor='red', alpha=0.2)
            ax.add_patch(rect)
        # redraw canvas to show changes
        ax.set_xlabel('Time [s]', fontsize=14)
        ax.set_ylabel(self.getAxesLabel(self.timeYAxis), fontsize=14)

    def plotDistance(self, ax):
        data = self.selectedData
        ax.plot(data[self.distXAxis], data[self.distYAxis], '.')
        ax.set_xlabel('Distance [nm]', fontsize=14)
        ax.set_ylabel(self.getAxesLabel(self.distYAxis), fontsize=14)

    def export(self, path, groupExport=True):
        ac = self.tc.getAnalysis(path=path, groupByBead=groupExport)
        ac.save()


class SegmentSelector(QtWidgets.QMainWindow):
    """
    GUI tool to select segments from datasets and export them as analysis files.

    Run it using the `runSegmentSelector` function or the compiled
    executable.
    """

    selector = None
    data = None

    def __init__(self, tc=None):
        super().__init__()
        # access settings object: organization: Grill Lab; application: Tweezers
        self.settings = QtCore.QSettings('Grill Lab', 'Tweezers')
        self.settings.beginGroup('segmentSelector')
        # qt starting point
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        # set window size and position
        storedGeometry = self.settings.value('windowGeometry', False)
        if storedGeometry:
            self.restoreGeometry(storedGeometry)
        else:
            self.setGeometry(100, 50, 1000, 730)
        # self.showFullScreen()
        self.setWindowTitle('Segment Selector')
        # status bar
        self.statusBar().showMessage('Starting...')

        # mpl options
        mpl.pyplot.style.use('fivethirtyeight')
        params = {'lines.linewidth': 2}
        mpl.rcParams.update(params)


        # box for plotting fgigures
        figBox = QtWidgets.QVBoxLayout()
        # create time figure with selector
        self.timeCanvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.axTime = self.timeCanvas.figure.add_subplot(1, 1, 1)
        self.timeCanvas.figure.tight_layout()
        self.selector = SpanSelector(self.axTime, self.onSegmentSelect, drawtype='box',
                                     interactive=True, useblit=True,
                                     rectprops={'alpha': 0.5, 'facecolor': 'red'})
        # create MPL toolbar
        self.mplToolbar = PlotNavigationToolbar(self.timeCanvas, self._main)
        # create force-distance figure
        self.fdCanvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.axDist = self.fdCanvas.figure.add_subplot(1, 1, 1)
        self.axDist.figure.tight_layout()
        figBox.addWidget(self.mplToolbar)
        figBox.addWidget(self.timeCanvas)
        figBox.addWidget(self.fdCanvas)

        # tweezers data "browser"
        # combo box for trial selection
        collectionBox = QtWidgets.QHBoxLayout()
        self.collectionCombo = TrialComboBox()
        self.collectionCombo.currentIndexChanged[int].connect(self.onSelectTrial)
        # previous button
        self.collectionPrevBtn = QtWidgets.QPushButton('<')
        self.collectionPrevBtn.setFixedWidth(50)
        self.collectionPrevBtn.setDisabled(True)
        self.collectionPrevBtn.clicked.connect(self.onPrevTrial)
        self.collectionNextBtn = QtWidgets.QPushButton('>')
        self.collectionNextBtn.setFixedWidth(50)
        self.collectionNextBtn.clicked.connect(self.onNextTrial)
        collectionBox.addWidget(self.collectionPrevBtn)
        collectionBox.addWidget(self.collectionCombo)
        collectionBox.addWidget(self.collectionNextBtn)

        # control pane
        # time plot y-axis selection
        buttonBox = QtWidgets.QVBoxLayout()
        timeYAxisLbl = QtWidgets.QLabel('Time Plot Y-Axis:')
        self.timeYAxisCmb = CustomComboBox()
        self.timeYAxisCmb.currentIndexChanged[str].connect(self.onSelectTimeYAxis)

        # dist plot x-axis selection
        distXAxisLbl = QtWidgets.QLabel('Distance Plot X-Axis:')
        self.distXAxisCmb = CustomComboBox()
        self.distXAxisCmb.currentIndexChanged[str].connect(self.onSelectDistXAxis)

        # dist plot y-axis selection
        distYAxisLbl = QtWidgets.QLabel('Distance Plot Y-Axis:')
        self.distYAxisCmb = CustomComboBox()
        self.distYAxisCmb.currentIndexChanged[str].connect(self.onSelectDistYAxis)

        # clear segments button
        self.clearSegmentsBtn = QtWidgets.QPushButton('Clear Segments')
        self.clearSegmentsBtn.clicked.connect(self.onClearSegments)

        # save segment text field and button
        self.saveSegmentIdTxt = QtWidgets.QLineEdit()
        self.saveSegmentIdTxt.setFixedWidth(150)
        self.saveSegmentIdTxt.setPlaceholderText('Segment ID (optional)')
        self.saveSegmentIdTxt.returnPressed.connect(self.onSaveSegment)
        self.saveSegmentBtn = QtWidgets.QPushButton('Save Segment')
        self.saveSegmentBtn.clicked.connect(self.onSaveSegment)

        # segment list
        segmentListLbl = QtWidgets.QLabel('Segments:')
        self.segmentList = QtWidgets.QListWidget()
        self.segmentList.setFixedWidth(150)

        # export grouped checkbox
        self.groupExportByIdChkbx = QtWidgets.QCheckBox('Group Export by Bead')
        self.groupExportByIdChkbx.setToolTip('<nobr>If set, creates only one Tweezers Analysis file</nobr> per Bead ID '
                                             'and '
                                             'stores '
                                             'all segments in this single file. Otherwise, one file is created per '
                                             'trial file.')
        self.groupExportByIdChkbx.setChecked(self.settings.value('groupExport', True))
        self.groupExportByIdChkbx.clicked.connect(self.onGroupExportClicked)

        # export button
        self.exportBtn = QtWidgets.QPushButton('Export')
        self.exportBtn.clicked.connect(self.onExport)

        # source type combo box
        self.sourceTypeCmb = CustomComboBox()
        self.sourceTypeCmb.addItems(DataManager.getSourceTypes().keys())
        # load data button
        loadDataBtn = QtWidgets.QPushButton('Load Directory')
        loadDataBtn.clicked.connect(self.onLoadDirectory)

        # quit button
        quitBtn = QtWidgets.QPushButton('Quit')
        quitBtn.clicked.connect(self.onExit)

        # add everything to the layout
        buttonBox.addWidget(timeYAxisLbl)
        buttonBox.addWidget(self.timeYAxisCmb)
        buttonBox.addWidget(distXAxisLbl)
        buttonBox.addWidget(self.distXAxisCmb)
        buttonBox.addWidget(distYAxisLbl)
        buttonBox.addWidget(self.distYAxisCmb)
        buttonBox.addWidget(self.clearSegmentsBtn)
        buttonBox.addWidget(self.saveSegmentIdTxt)
        buttonBox.addWidget(self.saveSegmentBtn)
        buttonBox.addWidget(segmentListLbl)
        buttonBox.addWidget(self.segmentList)
        buttonBox.addWidget(self.groupExportByIdChkbx)
        buttonBox.addWidget(self.exportBtn)
        buttonBox.addStretch(1)
        buttonBox.addWidget(self.sourceTypeCmb)
        buttonBox.addWidget(loadDataBtn)
        buttonBox.addWidget(quitBtn)

        hbox = QtWidgets.QHBoxLayout(self._main)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(collectionBox)
        vbox.addLayout(figBox)
        hbox.addLayout(vbox)
        hbox.addLayout(buttonBox)

        self.disableGui(True)
        self.setStatus('Ready')

        if tc:
            # store reference to the tweezers data collection
            self.data = DataManager(tc)
            self.loadData()

    def disableGui(self, disabled):
        """
        Diable all the GUI elements.

        Args:
            disabled (bool): `True` to disable everyting, `False` to enable everything
        """
        self.mplToolbar.setDisabled(disabled)
        self.selector.active = not disabled
        self.collectionCombo.setDisabled(disabled)
        self.collectionCombo.blockSignals(disabled)
        self.collectionPrevBtn.setDisabled(disabled)
        self.collectionNextBtn.setDisabled(disabled)
        self.timeYAxisCmb.setDisabled(disabled)
        self.timeYAxisCmb.blockSignals(disabled)
        self.distXAxisCmb.setDisabled(disabled)
        self.distXAxisCmb.blockSignals(disabled)
        self.distYAxisCmb.setDisabled(disabled)
        self.distYAxisCmb.blockSignals(disabled)
        self.clearSegmentsBtn.setDisabled(disabled)
        self.saveSegmentBtn.setDisabled(disabled)
        self.groupExportByIdChkbx.setDisabled(disabled)
        self.exportBtn.setDisabled(disabled)

    def loadData(self):
        """
        Do the acutal loading of the data stored in the :class:`.DataManager` and do some adjustments to the GUI.
        """

        # make sure nothing emits events
        self.disableGui(True)

        # set time y axis
        self.timeYAxisCmb.clear()
        items = [*self.data.getForceColumns(), None, *self.data.getDistColumns()]
        self.timeYAxisCmb.addItems(items)
        selectedItem = self.settings.value('timeYAxis', items[0])
        if selectedItem not in items:
            selectedItem = items[0]
        self.data.timeYAxis = selectedItem
        # this also triggers onSelectTimeYAxis
        self.timeYAxisCmb.setCurrentItem(selectedItem)

        # set dist x axis
        self.distXAxisCmb.clear()
        items = self.data.getDistColumns()
        self.distXAxisCmb.addItems(items)
        selectedItem = self.settings.value('distXAxis', items[0])
        if selectedItem not in items:
            selectedItem = items[0]
        self.data.distXAxis = selectedItem
        self.distXAxisCmb.setCurrentItem(selectedItem)

        # set dist y axis
        self.distYAxisCmb.clear()
        items = self.data.getForceColumns()
        self.distYAxisCmb.addItems(items)
        selectedItem = self.settings.value('distYAxis', items[0])
        if selectedItem not in items:
            selectedItem = items[0]
        self.data.distYAxis = selectedItem
        self.distYAxisCmb.setCurrentItem(selectedItem)

        self.collectionCombo.setTweezersCollection(self.data.tc)
        # self.collectionCombo.setCurrentIndex(0)

        self.disableGui(False)

        # plot the first dataset
        self.onSelectTrial(0)

    def onLoadDirectory(self):
        """
        Event handler for the "Load Directory" button. Get the path to the folder to load, create the references and
        trigger the loading and initialization of the GUI.
        """

        lastImportDir = self.settings.value('importDir', '')
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", lastImportDir)
        if path:
            self.settings.setValue('importDir', path)
            self.setStatus('Loading files ...')
            self.disableGui(True)
            self.data = DataManager.load(path, sourceType=self.sourceTypeCmb.currentText())
            self.loadData()
            self.setStatus('Ready')

    def setStatus(self, message):
        """
        Set the text in the status bar.

        Args:
            message (str): set to display in the status bar
        """

        self.statusBar().showMessage(message)
        self.repaint()

    def displayData(self):
        """
        Update all the plots and the segment list.
        """

        self.setStatus('Loading data...')
        self.plotTime()
        self.plotDistance()
        self.updateSegmentList()
        self.setStatus('Ready')

    def plotTime(self):
        """
        Update the plot in the time-figure. To select the data, manipulate the :class:`.DataManager` object.
        """

        # remove previous data from plot
        self.axTime.clear()
        # plot timeseries
        self.data.plotTime(self.axTime)
        self.timeCanvas.figure.tight_layout()
        # update toolbar home, forward etc buttons
        self.mplToolbar.update()
        self.timeCanvas.draw()

    def plotDistance(self):
        """
        Update the plot in the distance-figure. To select the data, manipulate the :class:`.DataManager` object.
        """

        # remove previous data from plot
        self.axDist.clear()
        # plot distance curve
        self.data.plotDistance(self.axDist)
        self.fdCanvas.figure.tight_layout()
        # redraw canvas to show changes
        self.fdCanvas.draw()

    def updateSegmentList(self):
        """
        Update the list of segments.
        """

        self.segmentList.clear()
        self.segmentList.addItems(self.data.t.segments.keys())

    def onSegmentSelect(self, eclick, erelease):
        """
        Event handler for the span selector that actually selects the segments in the time-plot.

        Args:
            eclick: event data for click event
            erelease: event data for the release event
        """

        # get click limits
        self.data.tLim = sorted([eclick.xdata, erelease.xdata])
        # update plot
        self.plotDistance()

    def onClearSegments(self):
        """
        Event handler for the "Clear Segments" button. Clears all the segments for the current :class:`.TweezersData`.
        """

        # delete all segments and update the plot
        self.data.clearSegments()
        self.displayData()
        self.setStatus('Segments cleared')

    def onSaveSegment(self):
        """
        Event handler for the "Save Segment" button. Saves the currently selected segment.
        """

        # ToDo: add warning for empty segment
        # make safe segment id from input
        # inspired by https://gist.github.com/seanh/93666
        segId = self.saveSegmentIdTxt.text().strip()
        keepcharacters = ('_', '-')
        segId = "".join(c for c in segId if c.isalnum() or c in keepcharacters)
        self.saveSegmentIdTxt.setText('')
        # save segment
        self.data.saveSegment(name=segId)
        # update the GUI
        self.plotTime()
        self.updateSegmentList()
        self.setStatus('Segment added')

    def onSelectTrial(self, index):
        """
        Event handler for the trial selection combo box. Selects the new trial in the :class:`.DataManager` object
        and updates the plots.
        """

        # update current dataset and plot new data
        index = self.collectionCombo.getTIndFromInd(index)
        self.data.setT(index)
        self.displayData()

    def onPrevTrial(self):
        """
        Event handler for the "Previous Trial" button.
        """

        try:
            self.collectionCombo.previous()
        except KeyError:
            self.setStatus('First trial reached')

    def onNextTrial(self):
        """
        Event Handler for the "Next Trial" Button.
        """

        try:
            self.collectionCombo.next()
        except KeyError:
            self.setStatus('Last trial reached')

    def onSelectTimeYAxis(self, axis):
        """
        Event Handler for y-axis selection combo box for the time plot.

        Args:
            axis (str): name of the selected axis
        """

        self.settings.setValue('timeYAxis', axis)
        self.data.timeYAxis = axis
        self.plotTime()

    def onSelectDistXAxis(self, axis):
        """
        Event Handler for x-axis selection combo box for the distance plot.

        Args:
            axis (str): name of the selected axis
        """

        self.settings.setValue('distXAxis', axis)
        self.data.distXAxis = axis
        self.plotDistance()

    def onSelectDistYAxis(self, axis):
        """
        Event Handler for y-axis selection combo box for the distance plot.

        Args:
            axis (str): name of the selected axis
        """

        self.settings.setValue('distYAxis', axis)
        self.data.distYAxis = axis
        self.plotDistance()

    def onGroupExportClicked(self):
        """
        Event handler for the "Group by Bead ID" checkbox. Updates the value in the settings object.
        """

        state = self.groupExportByIdChkbx.isChecked()
        self.settings.setValue('groupExport', state)

    def onExport(self):
        """
        Event handler for the "Export" button. Triggers exporting / saving of the analysis files.
        """

        lastExportDir = self.settings.value('exportDir', '')
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", lastExportDir)
        if path:
            self.settings.setValue('exportDir', path)
            self.setStatus('Saving analysis files...')
            try:
                group = self.settings.value('groupExport')
                self.data.export(path, groupExport=group)
            except KeyError as err:
                self.displayError('Could not save all analysis files', err)
            self.setStatus('Ready')

    def onExit(self):
        """
        Event handler for the "Quit" button. Use in general to quit the application
        """
        QtWidgets.QApplication.instance().quit()

    def closeEvent(self, event):
        """
        Event handler for closing the window. Used to store some display settings before exiting.
        """

        self.settings.setValue('windowGeometry', self.saveGeometry())

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
        msg.setInformativeText('{0}'.format(error))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


def runSegmentSelector(tc=None):
    """
    Function to run the :class:`.SegmentSelector`. It starts the required QtApplication and loads the
    :class:`.SegmentSelector` widget.

    If this function is called with the `tc` parameter, this :class:`.TweezersDataCollection` will be loaded upon
    startup. If the function is called from an interactive shell (e.g. a Jupyter notebook), one can just keep working
    with `tc` after exiting the GUI since the references will still be valid. In other words, the
    :class:`.TweezersData` objects in `tc` will hold all the segments that were selected via the GUI.

    Args:
        tc (:class:`.TweezersDataCollection`): data to load on startup
    """

    # might require setting backend properly
    if not QtWidgets.QApplication.instance():
        qapp = QtWidgets.QApplication([])
    else:
        qapp = QtWidgets.QApplication.instance()
    app = SegmentSelector(tc)
    app.show()
    qapp.setActiveWindow(app)
    qapp.exec_()
    qapp.quit()


