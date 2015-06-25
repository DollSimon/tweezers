import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import numpy as np
import math


class PsdPlotBase():
    """
    Base class for plotting PSDs. It implements some basic functionality and declares required variables.
    """

    def __init__(self, container, title=None):
        """
        Constructor for PsdPlotBase

        Args:
            container (:class:`tweezers.TweezersData`): container that holds PSD data to plot
            title (str): title for the plot, optional to override default value used
        """

        self.c = container
        # get figure title
        if title:
            self.title = title
        else:
            self.title = self.c.meta['title']

        self.fig = None
        self.ax = None
        self.psdAxes = []

        # count PSD columns and store their titles if container given
        self.getTitleList(self.c)

    def getTitleList(self, container):
        """
        Get a list of column titles that do not end on 'Std' in the PSD :class:`tweezers.TweezersData` container. These
        titles are by default used as subplot titles. The result is stored in ``self.psdTitles``.

        Args:
            container (:class:`tweezers.TweezersData`): tweezers data container
        """

        for title in container.psd.columns:
            if title is not 'f' and not title.lower().endswith('std'):
                self.psdAxes.append(title)

    def plotPsd(self, ax, f, psd, units=None, *args, **kwargs):
        """
        Plot a PSD into the given axes. Additional arguments are forwarded to :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            ax (:class:`matplotlib.axes.Axes`): axes for plotting the PSD
            f (array-like): frequencies
            psd (array-like): PSD values to plot
            units (str): units of the PSD
        """

        ax.set_ylim([10e-14, 10e-8])
        labelX = 'f [Hz]'
        labelY = 'PSD'
        if units:
            labelY += ' [' + units + ']'
        ax.set_xlabel(labelX)
        ax.set_ylabel(labelY)
        line = ax.loglog(f, psd, *args, **kwargs)
        return line

    def plotPsdErrors(self, ax, f, psd, errors, *args, **kwargs):
        """
        Plot PSD errors into the given axes. Additional arguments are forwarded to
        :meth:`matplotlib.axes.Axes.fill_between`.

        Args:
            ax (:class:`matplotlib.axes.Axes`): axes for plotting the PSD
            f (array-like): frequencies
            psd (array-like): PSD values to plot
            errors (array-like): errors for each data point of the PSD
        """

        lowerLimit = psd - errors
        lowerLimit[lowerLimit <= 0] = 1e-15

        # set alpha
        kwargs['alpha'] = 0.3

        ax.fill_between(f, psd + errors, lowerLimit, *args, **kwargs)

    def plotResiduals(self, ax, f, res, *args, **kwargs):
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

    def plotPsdFits(self, ax, f, fit, *args, **kwargs):
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

    def getColor(self, line):
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
            :class:`tweezers.plot.psd.PsdPlotBase`
        """

        for ax in self.ax:
            m = getattr(ax, method)
            m(*args, **kwargs)

        return self

    def legend(self, ax, **kwargs):
        """
        Adds a legend to the given axis, also used to update the legend after adding content. All
        parameters are forwarded to :meth:`matplotlib.axes.Axes.legend`.
        """

        ax.legend(loc=3)

    def save(self, path, **kwargs):
        """
        Save the current figure to ``path``. All further arguments are forwarded to :meth:`matplotlib.figure.savefig`.

        Args:
            path (str): filename to save the figure to
        """

        if type(path) is not str:
            path = str(path)

        self.fig.savefig(path, **kwargs)


class PsdFitPlot(PsdPlotBase):
    """
    Plot a PSD and the corresponding fit with residuals.
    """

    def __init__(self, container, title=None, residuals=True, **kwargs):
        """
        Constructor for PsdFitPlot. Additional arguments are passed on to :meth:`tweezers.plot.psd.PsdFitPlot.plot`.

        Args:
            container (:class:`tweezers.TweezersData`): container that holds PSD data to plot
            title (str): title for the plot, optional to override default value used
        """

        super().__init__(container=container, title=title)
        self.residuals = residuals
        self.plot(**kwargs)

    def plot(self, **kwargs):
        """
        Do the plot. Parameters are passed on to the plotting routines of the base class.
        """

        # set figure height depending if we should plot the residuals
        nrows = math.ceil(len(self.psdAxes) / 2)
        if self.residuals:
            figureSize = [15, 5 * nrows + 2]
        else:
            figureSize = [18, 6 * nrows]

        # set up the figure
        self.fig = plt.figure(figsize=figureSize)
        self.fig.suptitle(self.title, fontsize=16)
        # create grid for all the PSDs
        grid = gridspec.GridSpec(nrows, 2)
        grid.update(hspace=0.25, wspace=0.22)

        f = self.c.psd['f']
        fFit = self.c.psdFit['f']

        for n, axis in enumerate(self.psdAxes):
            gridEl = grid[n]

            # prepare axes
            if self.residuals and axis + 'Residuals' in self.c.psdFit.columns:
                innerGrid = gridspec.GridSpecFromSubplotSpec(100, 1, subplot_spec=gridEl, hspace=0.01)
                psdAxes = plt.subplot(innerGrid[20:])
            else:
                # in case we wanted to plot them but the data is not there, set it to false
                self.residuals = False
                # prepare axes
                psdAxes = plt.subplot(gridEl)
                psdAxes.set_title(axis)

            # plot psd
            psdLine = self.plotPsd(psdAxes, f, self.c.psd[axis],
                                   units=self.c.units['psd'],
                                   label='PSD',
                                   **kwargs)

            # plot psd errors if available
            if axis + 'Std' in self.c.psd.columns:
                # calculate standard error
                errors = self.c.psd[axis + 'Std'] / np.sqrt(self.c.meta['psdNBlocks'])
                self.plotPsdErrors(psdAxes, f, self.c.psd[axis],
                                   errors,
                                   color=self.getColor(psdLine),
                                   **kwargs)

            # plot fit
            # we want a label with stiffness but take diffusion coeff if it is not there
            if 'stiffness' in self.c.meta[axis]:
                label = 'k = {:.5} {}, fc = {:.1f} Hz\n$\\beta$ = {:.4} {}'.format(
                    self.c.meta[axis]['stiffness'],
                    self.c.units[axis]['stiffness'],
                    self.c.meta[axis]['cornerFrequency'],
                    self.c.meta[axis]['displacementSensitivity'],
                    self.c.units[axis]['displacementSensitivity'])
            else:
                label = 'D = {:.5} {}, fc = {:.1f} Hz'.format(self.c.meta[axis]['diffusionCoefficient'],
                                                              self.c.units[axis]['diffusionCoefficient'],
                                                              self.c.meta[axis]['cornerFrequency'])
            # check if chi2 is available
            if 'psdFitChi2' in self.c.meta[axis]:
                label += ', $\\chi^2$ = {:.4}'.format(self.c.meta[axis]['psdFitChi2'])
            # plot fit
            self.plotPsdFits(psdAxes, fFit, self.c.psdFit[axis + 'Fit'],
                             label=label, **kwargs)
            # add legend to PSD plot
            self.legend(psdAxes)

            # plot residuals if required
            if self.residuals:
                residualAxes = plt.subplot(innerGrid[:20], sharex=psdAxes)
                plt.setp(residualAxes.get_xticklabels(), visible=False)
                residualAxes.set_title(axis)
                # plot residuals
                self.plotResiduals(residualAxes, fFit, self.c.psdFit[axis + 'Residuals'], **kwargs)
                # remove lowest tick label so they don't overlap
                nbins = len(residualAxes.get_yticklabels())
                residualAxes.yaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='lower'))

        self.fig.subplots_adjust(top=0.94)


class PsdPlot(PsdPlotBase):
    """
    Plot all PSDs in a :class:`tweezers.TweezersData` object.
    """

    def __init__(self, container, title=None, **kwargs):
        super().__init__(container, title=title)
        self.plot(**kwargs)

    def plot(self, **kwargs):
        """
        Plot the PSDs. All arguments are forwarded to the plotting functions of ``matplotlib``.

        Returns:
            :class:`tweezers.plot.psd.PsdPlot`
        """

        self.fig, self.ax = plt.subplots()
        self.fig.set_figheight(6)
        self.fig.set_figwidth(8)
        self.fig.suptitle(self.title, fontsize=16)

        # get general info
        f = self.c.psd['f']
        unit = self.c.units['psd']
        # plot all PSDs
        for psd in self.psdAxes:
            psdLine = self.plotPsd(self.ax,
                                    f,
                                    self.c.psd[psd],
                                    label=psd,
                                    units=unit,
                                    **kwargs)
            # check if error column exists
            if psd + 'Std' in self.c.psd.columns:
                # calculate standard error
                errors = self.c.psd[psd + 'Std'] / np.sqrt(self.c.meta['psdNBlocks'])
                self.plotPsdErrors(self.ax,
                                     f,
                                     self.c.psd[psd],
                                     errors,
                                     color=self.getColor(psdLine),
                                     **kwargs)

        # add legend
        self.legend(self.ax)
