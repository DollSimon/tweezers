import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

from tweezers import TweezersAnalysis, TweezersAnalysisCollection
import tweezers.io as tio
from tweezers.ixo.statistics import averageData
from tweezers.ixo.fit import PolyFit


# columns to ignore on baseline correction
BASELINE_IGNORE_COLUMNS = ['BSL', 'bslFlat', 'bslBeads']


def createBslCorrField(analysis, force=False):
    """
    In a :class:`.TweezersAnalysis`, creates the empty structure to hold the baseline corrected data.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object in which the structure is created
        force (bool): forces creation (and overwriting) of structure

    Returns:
        :class:`.TweezersAnalysis`
    """

    if 'bslCorr' not in analysis.keys() or force:
        analysis.addField('bslCorr')
        for segId, seg in analysis.segments.items():
            if segId in BASELINE_IGNORE_COLUMNS:
                continue

            analysis.bslCorr.addField(segId)
            analysis.bslCorr[segId]['data'] = seg.data.copy()
            analysis.bslCorr[segId]['id'] = seg.id
            analysis.bslCorr[segId]['idSafe'] = seg.idSafe
    return analysis


def splitBaseline(analysis, windowSize=500, stdThrs=0.3, stdAxis='pmYForce', lineShift=50):
    """
    Split the baseline in a :class:`.TweezersAnalysis`. This splits it into a segment which is "flat", for baseline
    subtraction, and a segment where the beads are touching / stuck. This is determined by the standard deviation of
    the signal which goes down when beads are touching. The code uses a threshold for the standard deviation.

    The standard deviation is calculated in a rolling window (moving window) of the given size.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object that holds the baseline, requires a segment named `BSL`
        windowSize (int): size of the rolling window to compute standard deviation (default: 500)
        stdThrs (float): threshold for standard deviation, below this value, beads are considered to touch (default:
            0.3)
        stdAxis (str): axis along which to calculate the standard deviation (default: `pmYForce`)
        lineShift (int): after fitting a line to the segment where beads are touching, this line is shifted to the
            right (in force - trap distance plot) and everything to the right of this line is the flat baseline

    Returns:
        :class:`tweezers.TweezersAnalysis`
    """

    # get baseline data
    bslData = analysis.segments['BSL'].data
    # average data using with a rolling (moving) window
    avd = bslData.rolling(windowSize, center=True).mean()
    # calculate standard deviation for rolling window after subtracting mean from data
    std = (bslData - avd).rolling(windowSize, center=True).std()
    # select data where std is below threshold
    ds = bslData[std[stdAxis] < stdThrs]

    # split data where beads are stuck from rest of baseline
    # fit a line to the detected stuck bead segments
    fit = PolyFit(ds.yTrapDist, ds[stdAxis], 1)
    # # calculate line values (slightly shifted to ignore noise) for all trap distances
    lineThrs = fit(bslData.yTrapDist - lineShift)
    # select data where the signal is below the line
    bslFlat = bslData[bslData[stdAxis] < lineThrs]

    analysis.segments.addField('bslFlat')
    analysis.segments.bslFlat['data'] = bslFlat
    analysis.segments.addField('bslBeads')
    analysis.segments.bslBeads['data'] = ds

    return analysis


def baselineSubtraction(analysis, axis='y', averageBsl=None):
    """
    Remove baseline from signal. Input :class:`.TweezersAnalysis` must have a segment "BSL" which will be
    used as baseline. For all other segments, the baseline is subtracted. Baseline-corrected data is stored in
    `bslCorr`. The independent signal used as baseline "x" is trap distance.
    Data is cropped to the available trap distance.

    Args:
        analysis (:class:`.TweezersAnalysis`): input analysis object
        axis (str): `x` or `y`, axis to baseline (default: `y`)
        averageBsl (int): Average baseline data before subracting it? `None` for no averaging, `int` for number of
                          samples to average.

    Returns:
        :class:`tweezers.TweezersAnalysis`
    """

    bslData = analysis.segments['bslFlat'].data
    # get the axis for bsl correction
    trapDist = axis.lower() + 'TrapDist'
    # get data source class
    sourceClass = getattr(tio, analysis.meta.sourceClass)

    if averageBsl:
        bslData = averageData(bslData, nsamples=averageBsl)

    # get range of baseline
    mi = bslData[trapDist].min()
    ma = bslData[trapDist].max()

    # traps for which to subtract baseline (can't do all axes)
    traps = [trap for trap in analysis.meta.traps if trap.lower().endswith(axis.lower())]

    bslInterp = {}
    meta = analysis.meta.copy()
    for trap in traps:
        # get interpolation function
        bslInterp[trap] = sp.interpolate.interp1d(bslData[trapDist], bslData[trap + 'Diff'])
        # reset zeroOffset: since we subtract the baseline in raw Diff signal, we should not subract this again when calculating distances and forces
        meta[trap].zeroOffset = 0

    createBslCorrField(analysis, force=True)

    for segId, seg in analysis.bslCorr.items():
        seg.data = seg.data.query('@mi <=' + trapDist + '<= @ma').copy()
        for trap in traps:
            seg.data[trap + 'Diff'] = seg.data[trap + 'Diff'] - bslInterp[trap](seg.data[trapDist])

        m, u, bslCorr = sourceClass.postprocessData(meta, analysis.units, seg.data)
        seg['bslSubAverage'] = averageBsl

    return analysis


def zeroDistance(analysis, axis='y', useTrap='pm'):
    """
    Find the trap distance at which the beads touch and use this as an offset to calculate the extension.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis file to check
        axis (str): axis on which to do the correction, either 'y' (default) or 'x'
        useTrap (str): trap signal to use for zero distance detection (default: 'pm')

    Returns:
        :class:`.TweezersAnalysis`
    """

    traps = [trap for trap in analysis.meta.traps if trap.lower().endswith(axis.lower())]

    axesToCorrect = {'x': ['xDistVolt'],
                     'y': ['yDistVolt']}

    # get the axis for zeroing
    trapDist = axis.lower() + 'TrapDist'
    d = analysis.segments['bslBeads'].data

    # fit line to data where beads are touching / stuck
    for trap in traps:
        fit = PolyFit(d[trapDist], d[trap + 'Force'], 1)
        # get distance where line goes through 0
        offset = -fit.coef[0] / fit.coef[1]
        # store correction results
        analysis.meta[trap].addField('bslCorr')
        analysis.meta[trap].bslCorr['zeroExt'] = offset
        analysis.meta[trap].bslCorr['zeroExtIntercept'] = fit.coef[0]
        analysis.meta[trap].bslCorr['zeroExtR2'] = fit.rsquared()
        analysis.meta[trap].bslCorr['keffExp'] = fit.coef[1]
        k1 = analysis.meta['pm' + axis.upper()].stiffness
        k2 = analysis.meta['aod' + axis.upper()].stiffness
        analysis.meta[trap].bslCorr['keffTheo'] = k1 * k2 / (k1 + k2)

        # add units
        analysis.units[trap].addField('bslCorr')
        analysis.units[trap].bslCorr['zeroExt'] = analysis.units[trapDist]
        analysis.units[trap].bslCorr['zeroExtIntercept'] = analysis.units[trapDist]
        analysis.units[trap].bslCorr['keffExp'] = analysis.units[trap + 'Force'] + '/' + analysis.units[trapDist]
        analysis.units[trap].bslCorr['keffTheo'] = analysis.units[trap].bslCorr['keffExp']

    createBslCorrField(analysis)

    offset = analysis.meta[useTrap.lower() + axis.upper()].bslCorr.zeroExt
    # offset data
    for segId, seg in analysis.bslCorr.items():
        for ax in axesToCorrect[axis]:
            seg.data[ax] = seg.data[ax] - offset
            seg['zeroExt'] = offset
            seg['zerExtTrap'] = useTrap.lower() + axis.upper()

    return analysis


def videoCorrection(analysis, axis='y', lowForceLimit=5):
    """
    Fit a line to the video displacement vs trap displacement signal and correct the offset in the video signal. This
    combines offsets in trapping template from actual bead center and trap calibration offsets.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object
        axis:`x` or `y`, axis to do the video correction (default: `y`)
        lowForceLimit (float): ignore signal where force is below this limit (default: 5)

    Returns:
        :class:`.TweezersAnalysis`
    """

    traps = [trap for trap in analysis.meta.traps if trap.lower().endswith(axis.lower())]

    createBslCorrField(analysis)

    for segId, seg in analysis.bslCorr.items():
        d = seg.data
        for trap in traps:
            d[trap + 'DispVid'] = d[trap + 'Bead'] - d[trap + 'Trap']
            if trap == 'pmY':
                # invert PM bead displacement for convenience, disp is positive when pulled towards AOD ("up")
                d['pmYDispVid'] = -d['pmYDispVid']

            # get only data above a specific force, should we use trap separation instead?
            queryStr = '{}Force > {}'.format(trap, lowForceLimit)
            dq = d.query(queryStr)
            if dq.empty:
                raise ValueError('No data found for "videoCorrection" of axis "{}"'.format(trap))

            fit = PolyFit(dq[trap + 'Disp'], dq[trap + 'DispVid'], 1)

            d[trap + 'DispVid'] = d[trap + 'DispVid'] - fit.coef[0]
            seg[trap + 'ZeroVid'] = fit.coef[0]
            seg[trap + 'ZeroVidSlope'] = fit.coef[1]
            seg[trap + 'ZeroVidR2'] = fit.rsquared()

            # store units
            analysis.units[trap + 'ZeroVid'] = analysis.units[trap + 'Disp']
            
        seg['zeroVidFitForceLow'] = lowForceLimit

        # correct distance from video signal
        a = axis.upper()
        d[axis + 'DistVid'] = d['pm' + a + 'Trap'] - d['aod' + a + 'Trap'] \
                              - seg.zeroExt - d['pm' + a + 'DispVid'] - d['aod' + a + 'DispVid']

    return analysis


def segmentSummaryFig(analysis, segId, display=True, saveDir=None):
    """
    Creates a summary figure for a data segment from a :class:`.TweezersAnalysis` object after the baseline
    and video corrections.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object
        segId (int or str): segment ID for which to create the figure
        display (bool): should the figure be displayed? a new figure is created if so
        saveDir (str): path to save the figure to, if set to `None` it will not be saved (default: None)

    Returns:
        :class:`matplotlib.figure.Figure`
    """

    a = analysis
    s = a.bslCorr[segId]
    m = a.meta
    u = a.units

    # should we display the figure?
    if not display:
        if mpl.get_backend() == 'nbAgg':
            # if run from a notebook, turn off interactive mode
            plt.ioff()

    ### create figure ###
    fig = plt.figure(figsize=(12, 6), constrained_layout=True)
    gs = fig.add_gridspec(nrows=3, ncols=6, width_ratios=[1, 1, 1, 1, 1, 0.1])
    # extension axis
    axExt = fig.add_subplot(gs[:2, :2])
    # displacement axes
    ax0 = fig.add_subplot(gs[0, 2])
    ax1 = fig.add_subplot(gs[0, 3])
    ax2 = fig.add_subplot(gs[0, 4])
    ax3 = fig.add_subplot(gs[0, 5])
    axsDisp = [ax0, ax1, ax2, ax3]
    # bsl axes
    ax0 = fig.add_subplot(gs[1, 2])
    ax1 = fig.add_subplot(gs[1, 3])
    axsBsl = [ax0, ax1]
    # text axes
    axTxt = fig.add_subplot(gs[2, :])
    axTxt.set_axis_off()

    ### force - extension plot ###
    plotArgs = {'markersize': 1, 'rasterized': True}

    # hack to find rip and plot only until there
    d = s.data.sort_values('yDistVolt', ascending=False)
    dist = d[d.pmYForce > 10].iloc[0].yDistVolt
    queryStr = 'yDistVolt < @dist'

    ax = axExt
    d = s.data.query(queryStr)
    ax.plot(d.yDistVid, d.pmYForce, '.', label='Video', **plotArgs)
    d = a.segments[segId].data.copy()
    d.yDistVolt = d.yDistVolt - a.bslCorr[0].zeroExt
    d = d.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap', **plotArgs)
    d = s.data.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap - BSL', **plotArgs)
    # legend with fixed marker size
    ax.legend(markerscale=10, fontsize=8)
    ax.set_xlabel('Extension [nm]', fontsize=12)
    ax.set_ylabel('PM Y Force [pN]', fontsize=12)
    ax.set_title('Force - Extension', fontsize=14)

    ### config ###
    axsLbl = {'fontsize': 10}
    axsTtl = {'fontsize': 12}
    tickPrms = {'labelsize': 9}

    ### video - trap displacement plot ###
    d = s.data

    minF = d[['pmYForce', 'aodYForce', 'yForce']].min().min()
    maxF = d[['pmYForce', 'aodYForce', 'yForce']].max().max()
    scatterArgs = {'cmap': 'viridis', 'vmin': minF, 'vmax': maxF, 's': 10, 'rasterized': True}

    ax = axsDisp[0]
    # scatter plot, using "values" for color argument to convert pandas series to numpy array, series cause errors
    # for determining categorical or continuous colorbar by mpl
    p = ax.scatter(d.pmYDisp, d.pmYDispVid, c=d.pmYForce.values, **scatterArgs)
    # fit limit line
    idx = (d.pmYForce - s.zeroVidFitForceLow).abs().idxmin()
    ax.axvline(d.loc[idx].pmYDisp, color='0.7', linestyle='--')
    # slope 1 line
    lim = [d.pmYDisp.min(), d.pmYDisp.max()]
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], 'r', linestyle='--')
    ax.set_title('PM Y Displacement', **axsTtl)
    ax.set_ylabel('Video [nm]', **axsLbl)

    ax = axsDisp[1]
    ax.scatter(d.aodYDisp, d.aodYDispVid, c=d.aodYForce.values, **scatterArgs)
    # fit limit line
    idx = (d.aodYForce - s.zeroVidFitForceLow).abs().idxmin()
    ax.axvline(d.loc[idx].aodYDisp, color='0.7', linestyle='--')
    # slope 1 line
    lim = [d.aodYDisp.min(), d.aodYDisp.max()]
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], 'r', linestyle='--')
    ax.set_title('AOD Y Displacement', **axsTtl)

    ax = axsDisp[2]
    ax.scatter(d.yDistVolt, d.yDistVid, c=d.pmYForce.values, **scatterArgs)
    # slope 1 line
    lim = [d.yDistVolt.min(), d.yDistVolt.max()]
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], 'r', linestyle='--')
    ax.set_title('Extension Y', **axsTtl)

    cbar = fig.colorbar(p, cax=axsDisp[-1])
    cbar.set_label('Force [pN]', **axsLbl)

    for ax in axsDisp[:3]:
        ax.set_xlabel('Trap [nm]', **axsLbl)
    for ax in axsDisp:
        ax.tick_params(**tickPrms)

    ### bsl plot ###
    plotArgs = {'rasterized': True}
    # bsl pm
    ax = axsBsl[0]
    d = a.segments.BSL.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL', **plotArgs)
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Beads', **plotArgs)
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Flat', **plotArgs)
    if s.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslSubAverage)
        ax.plot(d.yTrapDist, d.pmYForce, '.', **plotArgs)

    ax.set_title('PM Y', **axsTtl)
    ax.set_ylabel('Force [pN]', **axsLbl)

    # bsl aod
    ax = axsBsl[1]
    d = a.segments.BSL.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL', **plotArgs)
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Beads', **plotArgs)
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Flat', **plotArgs)
    if s.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslSubAverage)
        ax.plot(d.yTrapDist, d.aodYForce, '.', label='_', **plotArgs)
    ax.set_title('AOD Y', **axsTtl)
    ax.legend(fontsize=6)

    for ax in axsBsl:
        ax.set_xlabel('Trap Dist [nm]', **axsLbl)
        ax.tick_params(**tickPrms)

    ### results text ###
    txtArgs = {'fontsize': 12, 'verticalalignment': 'top'}

    # general info
    txtId = s.id.translate(str.maketrans({'_': '\_', '#': '\#'}))
    txt = r'\textbf{{Exp ID:}}\\\\{}\\\\'.format(txtId) + \
          r'\begin{tabular}{l r l}' + \
          r'Temperature: & {:.1f} & {}\\'.format(m.temperature, u.temperature) + \
          r'Laser Power: & {:.1f} & {}\\'.format(m.laserPower, u.laserPower) + \
          r'Laser Temperature: & {:.1f} & {}'.format(m.laserTemperature, u.laserTemperature) + \
          r'\end{tabular}'

    axTxt.text(0, 1, txt, **txtArgs)

    # add AOD
    trapPm = 'pmY'
    trapAod = 'aodY'
    if 'bslCorr' in m.pmX.keys():
        trapPm = 'pmX'
        trapAod = 'aodX'

    # extension zero
    txt = r'\textbf{{Extension zero:}} {}\\\\' + \
          r'\begin{tabular}{l r r l}' + \
          r'& PM & AOD &\\' + \
          r'$\Delta x_0$: & {:.1f} & {:.1f} & {}\\'.format(m[trapPm].bslCorr.zeroExt, m[trapAod].bslCorr.zeroExt,
                                                           u[trapPm].bslCorr.zeroExt) + \
          r'$k_{{eff}}$: & {:.3f} & {:.3f} & {}\\'.format(m[trapPm].bslCorr.keffExp, m[trapAod].bslCorr.keffExp,
                                                          u[trapPm].bslCorr.keffExp) + \
          r'$k^{{exp}}_{{eff}}/k^{{theo}}_{{eff}}$: & {:.2f} & {:.2f} &\\'.format(
              m[trapPm].bslCorr.keffExp / m[trapPm].bslCorr.keffTheo,
              m[trapAod].bslCorr.keffExp / m[trapAod].bslCorr.keffTheo) + \
          r'$r^2$: & {:.2f} & {:.2f} & \\'.format(m[trapPm].bslCorr.zeroExtR2, m[trapAod].bslCorr.zeroExtR2) + \
          r'\end{tabular}'

    axTxt.text(0.35, 1, txt, **txtArgs)

    # video correction
    txt = r'\textbf{{Video correction:}} {}\\\\' + \
          r'\begin{tabular}{l r r l}' + \
          r'& PM & AOD & \\' + \
          r'$\Delta x$: & {:.1f} & {:.1f} & {}\\'.format(s.pmYZeroVid, s.aodYZeroVid, a.units.pmYZeroVid) + \
          r'Slope: & {:.3f} & {:.3f} & \\'.format(s.pmYZeroVidSlope, s.aodYZeroVidSlope) + \
          r'$r^2$: & {:.2f} & {:.2f} & \\'.format(s.pmYZeroVidR2, s.aodYZeroVidR2) + \
          r'\end{tabular}'

    axTxt.text(0.6, 1, txt, **txtArgs)

    saveArgs = {'facecolor': 'white', 'dpi': 300}

    if saveDir:
        p = Path(saveDir)
        if not p.exists() or not p.is_dir():
            raise FileExistsError('Directory given to save the figure does not exist.')
        fig.savefig(str(p / (s.id + '.pdf')), **saveArgs)

    # reset interactive state
    if not display:
        # close figure
        plt.close(fig)
        if mpl.get_backend() == 'nbAgg':
            # restore interactive mode
            plt.ion()

    return fig


def analysisSummaryFig(analysis, saveDir):
    """
    Loop through all segments of a :class:`.TweezersAnalysis` or :class:`.TweezersAnalysisCollection`
    and create the summary figure.

    Args:
        analysis (:class:`.TweezersAnalysis` or :class:`.TweezersAnalysisCollection`): analysis or
            collection object
        saveDir (str): output path to save the summary figures
    """

    if isinstance(analysis, TweezersAnalysis):
        ac = TweezersAnalysisCollection()
        ac[analysis.meta.beadId] = analysis
    else:
        ac = analysis.copy()

    for a in ac.values:
        for segId in a.bslCorr.keys():
            segmentSummaryFig(a, segId, saveDir=saveDir, display=False)


def bslCorrectAndSummarize(pathIn, pathOut=False, save=False, averageBsl=100, debug=False):
    """
    Load all :class:`.TweezersAnalysis` files from the given path, run the baseline
    and video corrections and export the summary figure for each segment.

    Args:
        pathIn (str): path to load the data from
        pathOut (str): path to export the summary figues, if `None`, exports to `pathIn` (default: None)
        save (bool): if `True`, the results are saved back to the analysis files that were loaded
        averageBsl (int): passed to :meth:`.baselineSubtraction`
        debug (bool): if `True`, print additional information (e.g. progress)

    Returns:
        :class:`.TweezersAnalysisCollection`
    """

    if not pathOut:
        pathOut = pathIn
    ac = TweezersAnalysisCollection.load(pathIn)
    for a in ac.values():
        if debug:
            print(a.name)
        # check if baseline is available
        if 'BSL' not in a.segments.keys():
            continue
        # baseline and video corrections
        splitBaseline(a)
        baselineSubtraction(a, averageBsl=averageBsl)
        zeroDistance(a)
        videoCorrection(a)

        # save summary figures
        for segId in a.bslCorr.keys():
            segmentSummaryFig(a, segId, saveDir=pathOut, display=False)

    if save:
        # save results back to analysis files
        ac.save()

    return ac
