import matplotlib.pyplot as plt
import seaborn as sns
from itertools import chain
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator


class PsdPlotBase():
    """
    Base class for plotting PSDs. It implements some basic functionality and declares required variables.
    """

    def __init__(self, container=None, title=None):
        """
        Constructor for PsdPlotBase

        Args:
            container (:class:`tweezer.TweezerData`): container that holds PSD data to plot
            title (str): title for the plot, optional to override default value used
        """

        self.c = container
        self.title = title
        self.fig = None
        self.ax = None
        self.nPsdAxes = 0
        self.psdTitles = []

        # count PSD columns and store their titles if container given
        if self.c:
            self.get_title_list(self.c)

    def get_title_list(self, container):
        """
        Get a list of column titles in the PSD :class:`tweezer.TweezerData` container. These titles are by default
        used as subplot titles. The result is stored in ``self.psdTitles``.

        Args:
            container (:class:`tweezer.TweezerData`): tweezer data container
        """

        self.nPsdAxes = 0
        self.psdTitles = []
        for title in container.psd.columns:
                if title.endswith('X') or title.endswith('Y'):
                    self.nPsdAxes += 1
                    self.psdTitles.append(title)

    def plot_psd(self, ax, f, psd, units=None, *args, **kwargs):
        """
        Plot a PSD into the given axes. Additional arguments are forwarded to :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            ax (:class:`matplotlib.axes.Axes`): axes for plotting the PSD
            f (array-like): frequencies
            psd (array-like): PSD values to plot
            units (str): units of the PSD
        """

        ax.set_ylim([10e-12, 10e-8])
        labelX = 'f [Hz]'
        labelY = 'PSD'
        if units:
            labelY += ' [' + units + ']'
        ax.set_xlabel(labelX)
        ax.set_ylabel(labelY)
        line = ax.loglog(f, psd, *args, **kwargs)
        return line

    def plot_residuals(self, ax, f, res, *args, **kwargs):
        """
        Plot the residuals of the PSD fit into the given axes. Additional arguments are passed to
        :meth:`matplotlib.axes.Axes.plot`.

        Args:
            ax (:class:`matplotlib.axes.Axes`): axes for plotting the PSD
            f (array-like): frequencies
            res (array-like): residuals
        """

        # plot the residuals and make them % by multiplying with 100
        ax.set_ylim([-100, 100])
        ax.set_ylabel('%')
        line = ax.plot(f, res * 100, *args, **kwargs)
        return line

    def plot_psd_fit(self, ax, f, fit, *args, **kwargs):
        """
        Plot the fit of the PSD into the given axes. Additional arguments are passed to
        :meth:`matplotlib.axes.Axes.plot`.

        Args:
            ax (:class:`matplotlib.axes.Axes`): axes for plotting the PSD
            f (array-like): frequencies
            fit (array-like): data points of the fit
        """

        line = ax.loglog(f, fit, *args, **kwargs)
        return line

    def get_color(self, line):
        """
        Return the color of a :class:`matplotlib.lines.Line2D` object.

        Args:
            line (:class:`matplotlib.lines.Line2D`): line object to get the color from
        """

        return line[0].get_color()

    def map(self, method, *args, **kwargs):
        """
        Run a given method of the :class:`matplotlib.axes.Axes` class on all the axes in the plot. Additional
        arguments are passed on to the method.

        Args:
            method (str): name of the method

        Returns:
            :class:`tweezer.plot.psd.PsdPlotBase`
        """

        for ax in self.ax:
            m = getattr(ax, method)
            m(*args, **kwargs)

        return self


class PsdFitPlot(PsdPlotBase):
    """
    Plot a PSD and the corresponding fit with residuals.
    """

    def __init__(self, container, title=None, **kwargs):
        """
        Constructor for PsdFitPlot. Additional arguments are passed on to :meth:`tweezer.plot.psd.PsdFitPlot.plot`.

        Args:
            container (:class:`tweezer.TweezerData`): container that holds PSD data to plot
            title (str): title for the plot, optional to override default value used
        """

        super().__init__(container=container, title=title)
        self.plot(**kwargs)

    def plot(self, **kwargs):
        """
        Do the plot. Parameters are passe on to the plotting routines of the base class.
        """

        # set up the figure with default properties
        self.fig = plt.figure(figsize=[18, 15])
        # check if title was given, if not use default
        if not self.title:
            self.title = self.c.meta['title']
        self.fig.suptitle(self.title, fontsize=16)
        # will break up when self.nPsdAxes is odd, too lazy to fix now ;)
        grid = gridspec.GridSpec(self.nPsdAxes//2, 2)

        resAxis = []
        psdAxis = []
        for n, gridEl in enumerate(grid):
            title = self.psdTitles[n]
            innerGrid = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=gridEl, hspace=0.01)

            # prepare psd axes
            psdAxes = plt.subplot(innerGrid[1:])
            # plot psd
            self.plot_psd(psdAxes, self.c.psd['f'], self.c.psd[title], units=self.c.units[title],
                          label='PSD', **kwargs)
            # plot fit
            label = 'k = {:.5}, fc = {:.4}, Chi2 = {:.4}'.format(self.c.meta.get(title, 'Stiffness'),
                                                               self.c.meta.get(title, 'CornerFreq'),
                                                               self.c.meta.get(title, 'PsdFitChi2'))
            self.plot_psd_fit(psdAxes, self.c.psdFit['f'], self.c.psdFit[title + 'Fit'],
                              label=label, **kwargs)
            # add legend to PSD plot
            psdAxes.legend(loc=3)

            # prepare residuals axes
            resAxes = plt.subplot(innerGrid[0], sharex=psdAxes)
            plt.setp(resAxes.get_xticklabels(), visible=False)
            resAxes.set_title(title)
            # plot residuals
            self.plot_residuals(resAxes, self.c.psdFit['f'], self.c.psdFit[title + 'Residuals'], **kwargs)
            # remove lowest tick label so they don't overlap
            nbins = len(resAxes.get_yticklabels())
            resAxes.yaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='lower'))

            # store references to axis
            psdAxis.append(psdAxes)
            resAxis.append(resAxes)

        self.fig.subplots_adjust(top=0.94)


class PsdPlot(PsdPlotBase):
    """
    Plot PSD(s). The plot consists of distinct figures for each axis along which the PSD is available (variable
    number).
    """

    def __init__(self, container=None, title=None, **kwargs):
        """
        Constructor for PsdPlot. If ``container`` is set, the :meth:`tweezer.plot.psd.PsdPlotBase.add` method
        is executed
        and additional arguements areforwarded.

        Args:
            container (:class:`tweezer.TweezerData`): data container
        """

        super().__init__(None, title)
        if container:
            self.add(container, **kwargs)

    def initialize(self, container):
        """
        Initialize the plotting environment (figure, axes, ...). Called automatically.

        Args:
            container (:class:`tweezer.TweezerData`): data container
        """

        # count PSD columns and store their titles
        self.get_title_list(container)

        # this will break for odd number of axes, use gridspec instead and create axis only where required
        self.fig, self.ax = plt.subplots(nrows=self.nPsdAxes//2, ncols=2)
        # flatten axis list
        self.ax = self.ax.flatten()
        # figure properties
        self.fig.set_figwidth(18)
        self.fig.set_figheight(15)
        # set figure title, use default if none was provided
        if not self.title:
            self.title = container.meta['title']
        self.fig.suptitle(self.title, fontsize=16)
        # set axes properties to default values
        for ax in self.ax:
            title = self.psdTitles.pop(0)
            ax.set_title(title)

    def add(self, container, psd=True, psdSource=False, fit=False, fitSource=False, **kwargs):
        """
        Add a PSD to the plot. A figure is shown for each axes of the PSD. Additional arguments are forwarded to
        :meth:`tweezer.plot.psd.PsdPlotBase.add_psd` and :meth:`tweezer.plot.psd.PsdPlotBase.add_fit`. Use this method to
        add data.

        Args:
            container (:class:`tweezer.TweezerData`): data container
            psd (bool): plot the PSD in :attr:`tweezer.TweezerData.psd`?
            psdSource (bool): plot the PSD in :attr:`tweezer.TweezerData.psdSource`?
            fit (bool): plot the fit to the PSD in :attr:`tweezer.TweezerData.psd`? if no 'fit' columns are
                        available, this is skipped
            fitSource (bool): plot the fit to the PSD in :attr:`tweezer.TweezerData.psdSource`?

        Returns:
            :class:`tweezer.plot.psd.PsdPlotBase`
        """

        if not self.fig:
            self.initialize(container)

        # get label to adjust for all three options below
        try:
            label = kwargs.pop('label')
        except KeyError:
            label = 'PSD'

        # variables to hold PSD colors so that the fits can have the same one
        color = None
        colorSource = None
        if psd:
            color = self.add_psd(container.psd, label=label, **kwargs)
        if psdSource:
            colorSource = self.add_psd(container.psdSource, label=label + ' source', **kwargs)
        if fit:
            self.add_fit(container.psdFit, meta=container.meta, label=label + ' fit', color=color, **kwargs)
        if fitSource:
            self.add_fit(container.psdFitSource,
                         meta=container.meta,
                         label=label + ' fit',
                         color=colorSource,
                         titleSuffix='Source',
                         **kwargs)
        # post-add stuff to adjust axes and figure
        for ax in self.ax:
            ax.legend(loc=3)
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.95)

        return self

    def add_psd(self, psd, *args, **kwargs):
        """
        Adds PSD from container data to plot. Additional arguments are forwarded to :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            psd (:class:`pandas.DataFrame`): PSD data to plot
        """

        for ax in self.ax:
            title = ax.get_title()
            line = self.plot_psd(ax, psd['f'], psd[title], *args, **kwargs)
            color = self.get_color(line)
        # return the color of the added line, it is assumed that all axes objects are at the same point in their
        # color cycle
        return color

    def add_fit(self, fit, meta, label='', titleSuffix='', **kwargs):
        """
        Adds the PSD fit from the container data to the plot. Additional arguments are forwarded to
        :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            fit (:class:`pandas.DataFrame`): fit data to plot
            meta (:class:`tweezer.MetaDict`): metadata container with fit result data (stiffness,
                                                        corner frequency, r2)
        """

        for ax in self.ax:
            title = ax.get_title()
            locLabel = label + '\nk = {:.5}, fc = {:.4}'.format(
                meta.get(title + titleSuffix, 'Stiffness'),
                meta.get(title + titleSuffix, 'CornerFreq'))
            # check for r2 value since it might not be present everywhere
            try:
                value = meta.get(title + titleSuffix, 'PsdFitR2')
                locLabel += ', r2 = {:.4}'.format(value)
            except KeyError:
                pass

            # check if plotting color was given
            if 'color' in kwargs and kwargs['color'] is None:
                kwargs.pop('color')
            self.plot_psd_fit(ax, fit['f'], fit[title + 'Fit'], label=locLabel, **kwargs)
