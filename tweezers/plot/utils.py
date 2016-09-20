import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.patches import Rectangle
import ipywidgets as widgets
from IPython.display import display

from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.collections import TweezersCollection

def peekPlot(td, *cols):
    # ToDo: docstring

    if not cols:
        # if no columns were given, plot all force columns
        cols = []
        for col in td.avData.columns:
            if col.lower().endswith('force'):
                cols.append(col)
    # shortcut to data
    avd = td.avData

    # plot data
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in cols:
        ax.plot(avd['time'], avd[col], '.', label=col)
    # plot segments
    try:
        segments = td.analysis['segments']
    except KeyError:
        segments = {}
    t0 = avd.timeAbs[0]
    for seg in segments.values():
        plotSegment(ax, seg['tmin'] - t0, seg['tmax'] - t0)
    # labels
    ax.set_ylabel(td.units[cols[0]])
    ax.set_xlabel(td.units['time'])
    ax.legend()
    fig.suptitle(td.meta['id'])
    return fig, ax


def plotSegment(ax, xmin, xmax, facecolor='red', alpha=0.2):
    # todo: docstring
    (ymin, ymax) = ax.get_ylim()
    ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor=facecolor, alpha=alpha))


class SegmentSelector:
    # todo: docstring
    color = 'red'
    alpha = 0.2

    def __init__(self, td, *cols, fig=None, ax=None, autosave=False):
        self.td = td
        self.autosave = autosave
        try:
            self.segments = td.analysis['segments']
        except KeyError:
            td.analysis['segments'] = IndexedOrderedDict()

        # create plot
        if not fig or not ax:
            self.fig, self.ax = plt.subplots(figsize=(12, 6))
        else:
            self.fig = fig
            self.ax = ax

        self.plot(*cols)
        self.selector = SpanSelector(self.ax, self.onselect, 'horizontal', rectprops={'alpha': 0.5, 'facecolor': self.color})

    def onselect(self, xmin, xmax):
        # store new segment
        self.td.addSegment(xmin, xmax, time='relative')

        # plot segment
        plotSegment(self.ax, xmin, xmax, facecolor=self.color, alpha=self.alpha)

        # autosave?
        if self.autosave:
            self.td.saveAnalysis()

    def disconnect(self):
        # use to disconnect SpanSelector from events
        self.selector.disconnect_events()

    def plot(self, *cols):
        # ToDo: docstring

        if not cols:
            # if no columns were given, plot all force columns
            cols = []
            for col in self.td.avData.columns:
                if col.lower().endswith('force'):
                    cols.append(col)
        # shortcut to data
        avd = self.td.avData

        # plot data
        for col in cols:
            self.ax.plot(avd['time'], avd[col], '.', label=col)
        # plot segments
        try:
            segments = self.td.analysis['segments']
        except KeyError:
            segments = {}
        t0 = avd.timeAbs[0]
        for seg in segments.values():
            plotSegment(self.ax, seg['tmin'] - t0, seg['tmax'] - t0, facecolor=self.color, alpha=self.alpha)
        # labels
        self.ax.set_ylabel(self.td.units[cols[0]])
        self.ax.set_xlabel(self.td.units['time'])
        self.ax.legend()
        self.fig.suptitle(self.td.meta['id'])


class CollectionSegmentSelector:
    # todo: docstring

    def __init__(self, td, *cols):
        if not isinstance(td, TweezersCollection):
            raise TypeError('TweezersCollection object expected but not given.')

        self.td = td
        self.current = 0
        self.cols = cols
        self.selector = None
        # get all dataset names
        self.tdKeys = list(td.keys())

        # create user interface
        self.progressBar = widgets.FloatProgress(value=0, min=0, max=1, description='Progress: ')
        self.progressCounter = widgets.Label()
        self.autosaveCheck = widgets.Checkbox(description='Autosave segments', value=True)
        statusMsgLabel = widgets.Label(value='Status:')
        self.statusMsg = widgets.Label(value='')
        self.currentDatasetDropdown = widgets.Dropdown(options=self.tdKeys, value=self.tdKeys[0],
                                                       description='Current dataset:', width='400px')
        self.currentDatasetDropdown.observe(self.currentDatasetChanged, names='value')
        self.saveButton = widgets.Button(description='Save segments')
        self.saveButton.on_click(self.saveButtonClick)
        self.resetButton = widgets.Button(description='Reset current dataset')
        self.resetButton.on_click(self.resetButtonClick)
        self.previousButton = widgets.Button(description='Previous dataset')
        self.previousButton.on_click(self.previousButtonClick)
        self.nextButton = widgets.Button(description='Next dataset')
        self.nextButton.on_click(self.nextButtonClick)

        display(widgets.VBox([
            widgets.HBox([self.progressBar, self.progressCounter]),
            widgets.HBox([statusMsgLabel, self.statusMsg]),
            widgets.HBox([self.autosaveCheck]),
            widgets.HBox([self.currentDatasetDropdown]),
            widgets.HBox([self.saveButton, self.resetButton, self.previousButton, self.nextButton])
        ]))

        # create figure and plot
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.plotCurrent()

    def plotCurrent(self):
        # cleanup
        if self.selector:
            self.selector.disconnect()
        self.ax.cla()

        # plot new
        self.statusMsg.value = 'Loading dataset...'
        self.progressBar.value = (self.current + 1) / len(self.td)
        self.progressCounter.value = str(self.current + 1) + ' / ' + str(len(self.td))
        self.currentDatasetDropdown.value = self.tdKeys[self.current]
        self.selector = SegmentSelector(self.td[self.current], *self.cols,
                                        fig=self.fig, ax=self.ax, autosave=self.autosaveCheck.value)
        self.statusMsg.value = 'Dataset loaded'

    def currentDatasetChanged(self, change):
        self.current = self.tdKeys.index(change['new'])
        self.plotCurrent()

    def saveButtonClick(self, b):
        self.td[self.current].saveAnalysis()
        self.statusMsg.value = 'Segments saved'

    def resetButtonClick(self, b):
        self.td[self.current].analysis['segments'] = {}
        if self.autosaveCheck.value:
            self.td[self.current].saveAnalysis()
        self.statusMsg.value = 'Segments reset'
        self.plotCurrent()

    def previousButtonClick(self, b):
        self.current -= 1
        if self.current >= 0:
            self.plotCurrent()
        else:
            self.current = 0

    def nextButtonClick(self, b):
        self.current += 1
        lentd = len(self.td)
        if self.current < lentd:
            self.plotCurrent()
        else:
            self.current = lentd - 1

