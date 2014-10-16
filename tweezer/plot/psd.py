import matplotlib.pyplot as plt
import seaborn
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText


class PsdPlot():
    """
    Plot PSD(s). The plot consists of distinct figures for each axis along which the PSD is available (variable
    number).
    """

    def __init__(self, container=None, **kwargs):
        """
        Constructor for PsdPlot. If ``container`` is set, the :meth:`tweezer.plot.psd.PsdPlot.add` method is executed
        and additional arguements areforwarded.

        Args:
            container (:class:`tweezer.container.Data`): data container
        """

        self.fig = None
        if container:
            self.add(container, **kwargs)

    def initialize(self, container):
        """
        Initialize the plotting environment (figure, axes, ...). Called automatically.

        Args:
            container (:class:`tweezer.container.Data`): data container
        """

        # count PSD columns and store their titles
        i = 0
        titles = []
        for title in container.psd.columns:
            if title != 'f' and not title.startswith('fit'):
                i += 1
                titles.append(title)

        self.fig, self.ax = plt.subplots(nrows=i, ncols=1)
        self.fig.set_figwidth(8)
        self.fig.set_figheight(20)
        # set figure title
        self.fig.suptitle(container.meta['title'], fontsize=16)
        # set axes properties to default values
        for ax in self.ax:
            title = titles.pop(0)

            labelX = 'f [Hz]'
            labelY = 'PSD [' + container.units[title] + ']'
            ax.set_xlabel(labelX)
            ax.set_ylabel(labelY)

            ax.set_ylim([10e-12, 10e-8])
            ax.set_title(title)

        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.95)

    def add(self, container, psd=True, psdSource=False, fit=True, fitSource=False, **kwargs):
        """
        Add a PSD to the plot. A figure is shown for each axes of the PSD. Additional arguments are forwarded to
        :meth:`tweezer.plot.psd.PsdPlot.add_psd` and :meth:`tweezer.plot.psd.PsdPlot.add_fit`. Use this method to
        add data.

        Args:
            container (:class:`tweezer.container.Data`): data container
            psd (bool): plot the PSD in :attr:`tweezer.container.Data.psd`?
            psdSource (bool): plot the PSD in :attr:`tweezer.container.Data.psdSource`?
            fit (bool): plot the fit to the PSD in :attr:`tweezer.container.Data.psd`? if no 'fit' columns are
                        available, this is skipped
            fitSource (bool): plot the fit to the PSD in :attr:`tweezer.container.Data.psdSource`?

        Returns:
            :class:`tweezer.plot.psd.PsdPlot`
        """

        if not self.fig:
            self.initialize(container)

        # get label to adjust for all three options below
        try:
            label = kwargs.pop('label')
        except KeyError:
            label = 'PSD'

        if psd:
            self.add_psd(container.psd, label=label, **kwargs)
        if psdSource:
            self.add_psd(container.psdSource, label=label + ' source', **kwargs)
        if fit:
            columns = [column for column in container.psd.columns if column.startswith('fit')]
            if columns:
                columns.append('f')
                self.add_fit(container.psd[columns],
                             meta=container.meta,
                             label=label + ' fit',
                             **kwargs)
        if fitSource:
            columns = [column for column in container.psdSource.columns if column.startswith('fit')]
            if columns:
                columns.append('f')
                self.add_fit(container.psdSource[columns],
                             meta=container.meta,
                             label=label + ' source fit',
                             suffix='Source',
                             **kwargs)

        # post-add stuff to adjust axes
        for ax in self.ax:
            ax.legend(loc=3)

        return self

    def map(self, method, *args, **kwargs):
        """
        Run a given method of the :class:`matplotlib.axes.Axes` class on all the axes in the plot. Additional
        arguments are passed on to the method.

        Args:
            method (str): name of the method

        Returns:
            :class:`tweezer.plot.psd.PsdPlot`
        """

        for ax in self.ax:
            m = getattr(ax, method)
            m(*args, **kwargs)

        return self

    def add_psd(self, psd, *args, **kwargs):
        """
        Adds PSD from container data to plot. Additional arguments are forwarded to :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            psd (:class:`pandas.DataFrame`): PSD data to plot
        """

        for ax in self.ax:
            title = ax.get_title()
            ax.loglog(psd['f'], psd[title], *args, **kwargs)

    def add_fit(self, fit, meta, label='', suffix='', **kwargs):
        """
        Adds the PSD fit from the container data to the plot. Additional arguments are forwarded to
        :meth:`matplotlib.axes.Axes.loglog`.

        Args:
            fit (:class:`pandas.DataFrame`): fit data to plot
            meta (:class:`tweezer.container.MetaDict`): metadata container with fit result data (stiffness,
                                                        corner frequency, r2)
        """

        for ax in self.ax:
            title = ax.get_title()
            locLabel = label + '\nk = = {:.5}, fc = {:.4}'.format(
                meta.get(title, 'Stiffness', suffix),
                meta.get(title, 'CornerFreq', suffix))
            # check for r2 value since it might not be present everywhere
            try:
                value = meta.get(title, 'PsdFitR2', suffix)
                locLabel += ', r2 = {:.4}'.format(value)
            except KeyError:
                pass
            ax.loglog(fit['f'], fit['fit' + title], label=locLabel, **kwargs)
