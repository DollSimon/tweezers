import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import ipywidgets as widgets
from IPython.display import display

from tweezers.plot.utils import plotSegment


class CollectionPlot:
    #ToDo docstring
    
    def __init__(self, data, fcn, **kwargs):
        self.tc = data.flatten()
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
        self.datasetDropdown.layout.width = '500px'
        self.datasetDropdown.observe(self.datasetDropdownChanged, names='value')

        statusMsgLabel = widgets.Label(value='Status:')
        self.statusMsg = widgets.Label(value='-')

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


class SegmentSelector(CollectionPlot):
    #ToDo docstring

    color = 'red'
    selector = None
    alpha = 0.2

    def __init__(self, td, cols=['yForce'], **kwargs):
        if isinstance(cols, str):
            self.cols = [cols]
        else:
            self.cols = cols

        super().__init__(td, self.plot, **kwargs)

        # autosave checkbox
        self.autosaveCheck = widgets.Checkbox(value=True)
        autsaveCheckLabel = widgets.Label('Autosave segments:')
        autosaveBox = widgets.HBox([autsaveCheckLabel, self.autosaveCheck])
        autosaveBox.layout.align_items = 'center'

        # save and reset buttons
        self.saveButton = widgets.Button(description='Save segments')
        self.saveButton.on_click(self.saveButtonClick)
        self.resetButton = widgets.Button(description='Reset current dataset')
        self.resetButton.on_click(self.resetButtonClick)

        # display widgets
        gui = widgets.VBox([
            autosaveBox,
            widgets.HBox([self.saveButton, self.resetButton])
        ])
        display(gui)

    def update(self):
        # disconnect current SpanSelector
        if self.selector:
            self.selector.disconnect_events()
        # plot new stuff
        super().update()
        # create new SpanSelector
        self.selector = SpanSelector(self.ax, self.segmentSelect, 'horizontal',
                                     rectprops={'alpha': 0.5, 'facecolor': self.color})

    def plot(self, t, ax):
        # plot data
        for col in self.cols:
            ax.plot(t.avData.time, t.avData[col], '.', label=t.units[col])
            ax.legend()
            ax.set_xlabel('Time [s]')

        # plot existing segments
        for seg in self.tc[self.i].segments.values():
            plotSegment(self.ax, seg['tmin'], seg['tmax'], facecolor=self.color, alpha=self.alpha)

    def segmentSelect(self, xmin, xmax):
        # add segment
        self.statusMsg.value = '{} - {}'.format(xmin, xmax)
        self.tc[self.i].addSegment(xmin, xmax)

        # plot segment
        plotSegment(self.ax, xmin, xmax, facecolor=self.color, alpha=self.alpha)

        # save segments?
        if self.autosaveCheck.value:
            self.tc[self.i].save()

    def saveButtonClick(self, b):
        self.tc[self.i].save()
        self.statusMsg.value = 'Segments saved'

    def resetButtonClick(self, b):
        # delete all segments using the higher level API
        for segId in self.tc[self.i].segments.keys():
            self.tc[self.i].deleteSegment(segId)
        # autosave?
        if self.autosaveCheck.value:
            self.tc[self.i].save()
        # update GUI
        self.statusMsg.value = 'Segments reset'
        self.update()
