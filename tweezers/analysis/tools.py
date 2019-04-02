import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

from tweezers import TweezersAnalysis, TweezersAnalysisCollection
import tweezers.io as tio
from tweezers.ixo.statistics import averageData
from tweezers.ixo.fit import PolyFit
from tweezers.physics.tweezers import tcOsciHydroCorrect


# columns to ignore on baseline correction
BASELINE_IGNORE_COLUMNS = ['bsl', 'bslFlat', 'bslBeads']


def osciHydrodynamicCorr(analysis):
    """
    Correct results of thermal calibration performed with oscillation technique.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object

    Returns:
        :class:`.TweezersAnalysis`
    """

    # store original segments
    analysis['segmentsOrig'] = analysis.segments.copy()

    m = analysis.meta
    # radii in nm
    rPm = m.pmY.beadDiameter / 2 * 1000
    rAod = m.aodY.beadDiameter / 2 * 1000

    # get y distance
    dy = np.abs(m.pmY.trapPosition - m.aodY.trapPosition)

    # go through y-traps
    for trap in m.traps:
        if not trap.lower().endswith('y'):
            continue
        # the radius in the equation is that of the other bead (that causes the flow field)
        [rTrap, rOther] = [rPm, rAod] if trap.lower().startswith('pm') else [rAod, rPm]
        # get correction factor
        c = tcOsciHydroCorrect(dy, rTrap=rTrap, rOther=rOther, method='oseen')
        # store correction factor
        m[trap]['hydroCorr'] = c
        # also store for x-trap
        xTrap = trap[:-1] + 'X'
        m[xTrap]['hydroCorr'] = c

    # correct the calibration parameters
    for trap in m.traps:
        c = m[trap].hydroCorr
        m[trap].displacementSensitivity *= c
        m[trap].stiffness /= c**2
        m[trap].forceSensitivity /= c

    # correct all segments
    for seg in analysis.segments.values():
        m, u, d = tio.TxtBiotecSource.postprocessData(m, analysis.units, seg.data)

    return analysis


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

    This is currently not reliable and should be used with caution and supervision.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object that holds the baseline, requires a segment named `bsl`
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
    bslData = analysis.segments['bsl'].data
    # average data using with a rolling (moving) window
    avd = bslData.rolling(windowSize, center=True).mean()
    # calculate standard deviation for rolling window after subtracting mean from data
    std = (bslData - avd).rolling(windowSize, center=True).std()
    # select data
    # stdStd = std.rolling(windowSize, center=True).std()
    # stdThrs = std[stdAxis].min() + 4 * stdStd[stdAxis].mean()
    # select data where std is below threshold
    ds = bslData[std[stdAxis] < stdThrs]
    if ds.empty:
        raise ValueError('No data found with std below threshold in "splitBaseline".')

    # split data where beads are stuck from rest of baseline
    # fit a line to the detected stuck bead segments
    fit = PolyFit(ds.yTrapDist, ds[stdAxis], 1)
    # calculate line values (slightly shifted to ignore noise) for all trap distances
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
    Remove baseline from signal. Input :class:`.TweezersAnalysis` must have a segment "bsl" which will be
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
        bslInterp[trap] = sp.interpolate.interp1d(bslData[trapDist], bslData[trap + 'Diff'], kind='cubic')
        # reset zeroOffset: since we subtract the baseline in raw Diff signal, we should not subract this again when calculating distances and forces
        meta[trap].zeroOffset = 0

    createBslCorrField(analysis, force=True)

    for segId, seg in analysis.bslCorr.items():
        seg.data = seg.data.query('@mi <=' + trapDist + '<= @ma').copy()
        for trap in traps:
            seg.data[trap + 'Diff'] = seg.data[trap + 'Diff'] - bslInterp[trap](seg.data[trapDist])

        m, u, bslCorr = sourceClass.postprocessData(meta, analysis.units, seg.data)
        seg.addField('bslCorr')
        seg.bslCorr['bslSubAverage'] = averageBsl

    return analysis


def zeroDistance(analysis, axis='y', useTrap='pm'):

    axesToCorrect = {'x': ['xDistVolt'],
                     'y': ['yDistVolt']}

    d = analysis.segments['bslBeads'].data
    forceChan = useTrap.lower() + axis.upper() + 'Force'
    trapDistChan = axis.lower() + 'TrapDist'
    dZeroForce = d.query('-0.05 <= ' + forceChan + ' <= 0.05')
    offset = dZeroForce[trapDistChan].mean()

    createBslCorrField(analysis)

    # offset data
    for segId, seg in analysis.bslCorr.items():
        seg.addField('bslCorr')
        for ax in axesToCorrect[axis]:
            seg.data[ax] = seg.data[ax] - offset
            seg.bslCorr['zeroExt'] = offset
            seg.bslCorr['zeroExtTrap'] = useTrap.lower() + axis.upper()
            seg.bslCorr['zeroExtUnit'] = analysis.units[trapDistChan]

    return analysis

def zeroDistanceByFit(analysis, axis='y', useTrap='pm'):
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
        analysis.meta[trap].bslCorr['zeroExtR2'] = fit.rsquared
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
        seg.addField('bslCorr')
        for ax in axesToCorrect[axis]:
            seg.data[ax] = seg.data[ax] - offset
            seg.bslCorr['zeroExt'] = offset
            seg.bslCorr['zeroExtTrap'] = useTrap.lower() + axis.upper()

    return analysis


def displacementCorrection(analysis, axis='y', lowForceLimit=5):
    """
    Correct the displacement data (displacement of bead from trap center).

    The procedure is to fit a line to the video displacement vs trap displacement signal. The intercept of the line
    is used as an offset for the video signal (zero displacement is well determined from PSD signal). The slope of
    the line is used to correct the displacement from the trap signal which is not reliable for larger displacements
    (depending on trap stiffness).

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object
        axis: `x` or `y`, axis to do the displacement correction (default: `y`)
        lowForceLimit (float): ignore signal where force is below this limit (default: 5)

    Returns:
        :class:`.TweezersAnalysis`
    """

    createBslCorrField(analysis)
    traps = [trap for trap in analysis.meta.traps if trap.lower().endswith(axis.lower())]

    for segId, seg in analysis.bslCorr.items():
        seg.addField('bslCorr')
        d = seg.data

        for trap in traps:
            # get only data above a specific force, should we use trap separation instead?
            queryStr = '{}Force > {}'.format(trap, lowForceLimit)
            dq = d.query(queryStr)
            if dq.empty:
                raise ValueError('No data found for "videoCorrection" of axis "{}" in "{}"'.format(trap, seg.id))

            # fit Video vs Trap data with line
            fit = PolyFit(dq[trap + 'Disp'], dq[trap + 'DispVid'], 1)
            intercept = fit.coef[0]
            slope = fit.coef[1]

            # store parameters
            seg.bslCorr[trap + 'ZeroVid'] = intercept
            seg.bslCorr[trap + 'ZeroVidSlope'] = slope
            seg.bslCorr[trap + 'ZeroVidR2'] = fit.rsquared
            # store units
            analysis.units[trap + 'ZeroVid'] = analysis.units[trap + 'Disp']

            # shift video displacement by offset
            d[trap + 'DispVid'] = d[trap + 'DispVid'] - intercept
            # parallel projection
            d[trap + 'Disp'] *= slope

            # # we trust the zero of the trap signal, but not the one of the video signal
            # queryStr = '-10 < {}Disp < 10'.format(trap)
            # dq = d.query(queryStr)
            # zeroVid = dq[trap + 'DispVid'].mean()
            # d[trap + 'DispVid'] -= zeroVid
            # seg.bslCorr[trap + 'ZeroVid'] = zeroVid
            # # store units
            # analysis.units[trap + 'ZeroVid'] = analysis.units[trap + 'Disp']
            # # temporary fix
            # seg.bslCorr[trap + 'ZeroVidSlope'] = np.nan
            # seg.bslCorr[trap + 'ZeroVidR2'] = np.nan
            #
            # # we trust the displacement from the video, but not the one from the trap signal but want the better
            # # resolution of the trap signal
            # ds = d.sort_values(by='aodYDisp')
            # dm = ds.rolling(15, center=True).mean()
            #
            # d[trap + 'Disp'] = ds[trap + 'Disp'] + (dm[trap + 'DispVid'] - dm[trap + 'Disp'])

        seg.bslCorr['zeroVidFitForceLow'] = lowForceLimit

        a = axis.upper()
        try:
            # the 'zeroDistance' function should not be required to run this one
            offset = seg.bslCorr.zeroExt
        except KeyError:
            offset = 0
        trapDist = d['pm' + a + 'Trap'] - d['aod' + a + 'Trap'] - offset
        # correct extension from video signal
        d[axis + 'DistVid'] = trapDist - d['pm' + a + 'DispVid'] - d['aod' + a + 'DispVid']

        # correct extension from trap signal
        d[axis + 'DistVolt'] = trapDist - d['pm' + a + 'Disp'] - d['aod' + a + 'Disp']

    return analysis


def detectRip(analysis, axis='y'):
    """
    Detect rip in each segment in 'bslCorr' by finding analyzing the force vs trap distance signal. Stores
    `ripTrapDist` and `ripPmYForce` in the segment.
    Also adds the `dist20` key that is the mean force @ 20 pN.

    Args:
        analysis (:class:`.TweezersAnalysis`): analysis object
        axis: axis: `x` or `y`, axis to check of force step (default: `y`)

    Returns:
        :class:`.TweezersAnalysis`
    """

    dist = axis.lower() + 'TrapDist'
    force = axis.lower() + 'Force'

    for seg in analysis.bslCorr.values():
        seg.addField('bslCorr')

        # get and sort data
        d = seg.data.sort_values(dist)
        # get preliminary ripping trap distance by force threshold
        ripDist = d.query(force + ' > 5').iloc[-1][dist]
        # refine ripping distance if available
        ds = d.query(dist + ' < @ripDist').iloc[-100:]
        limForce = ds[force].max() * 2 / 3
        sel = ds.query(force + ' < @limForce')
        if not sel.empty:
            ripDist = sel.iloc[0][dist]
        # get ripping force
        d = d.query(dist + ' < @ripDist')
        ripF = d.iloc[-10:].pmYForce.max()
        # store as rip distance
        seg['ripTrapDist'] = ripDist
        # store ripping force
        seg['ripPmYForce'] = ripF

        # dist @ 20 pN
        d = seg.data.query('19.5 < pmYForce < 20.5')
        if d.empty:
            d20 = np.nan
        else:
            d20 = d.yDistVolt.mean()
        seg['dist20'] = d20

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

    # plot until rip
    dist = s.ripTrapDist
    queryStr = 'yTrapDist < @dist'

    ax = axExt
    d = s.data.query(queryStr)
    ax.plot(d.yDistVid, d.pmYForce, '.', label='Video', **plotArgs)
    d = a.segments[segId].data.copy()
    d.yDistVolt = d.yDistVolt - a.bslCorr[0].bslCorr.zeroExt
    d = d.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap', **plotArgs)
    d = s.data.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap - corr', **plotArgs)
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
    # original data
    dorig = a.segments[segId].data

    ax = axsDisp[0]
    # original data
    ax.scatter(dorig.pmYDisp, dorig.pmYDispVid, c='lightgray', **scatterArgs)
    # fixed data
    # scatter plot, using "values" for color argument to convert pandas series to numpy array, series cause errors
    # for determining categorical or continuous colorbar by mpl
    p = ax.scatter(d.pmYDisp, d.pmYDispVid, c=d.pmYForce.values, **scatterArgs)
    # fit limit line
    idx = (d.pmYForce - s.bslCorr.zeroVidFitForceLow).abs().idxmin()
    ax.axvline(d.loc[idx].pmYDisp, color='0.7', linestyle='--')
    # slope 1 line
    lim = [d.pmYDisp.min(), d.pmYDisp.max()]
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], 'r', linestyle='--')
    ax.set_title('PM Y Displacement', **axsTtl)
    ax.set_ylabel('Video [nm]', **axsLbl)

    ax = axsDisp[1]
    # original data
    ax.scatter(dorig.aodYDisp, dorig.aodYDispVid, c='lightgray', **scatterArgs)
    # fixed data
    ax.scatter(d.aodYDisp, d.aodYDispVid, c=d.aodYForce.values, **scatterArgs)
    # fit limit line
    idx = (d.aodYForce - s.bslCorr.zeroVidFitForceLow).abs().idxmin()
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
    plotArgs = {'rasterized': True, 'markersize': 1}
    # bsl pm
    ax = axsBsl[0]
    if 'bsl' in a.segments.keys():
        d = a.segments.bsl.data
        ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL', color='gray', **plotArgs)

    # plot bslBeads
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Beads', zorder=5, **plotArgs)
    # plot bslFlat
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Flat', zorder=3, **plotArgs)
    if s.bslCorr.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslCorr.bslSubAverage)
        ax.plot(d.yTrapDist, d.pmYForce, '.', zorder=4, **plotArgs)

    # general
    ax.set_title('PM Y', **axsTtl)
    ax.set_ylabel('Force [pN]', **axsLbl)

    # bsl aod
    ax = axsBsl[1]
    if 'bsl' in a.segments.keys():
        d = a.segments.bsl.data
        ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL', color='gray', **plotArgs)

    # plot bslBeads
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Beads', zorder=5, **plotArgs)
    # plot bslFlat
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Flat', zorder=3, **plotArgs)
    if s.bslCorr.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslCorr.bslSubAverage)
        ax.plot(d.yTrapDist, d.aodYForce, '.', label='_', zorder=4, **plotArgs)
    # general
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

    # more general info
    d20 = s.dist20 if 'dist20' in s.keys() else np.nan
    ripF = s.ripPmYForce if 'ripPmYForce' in s.keys() else np.nan

    txt = r'\textbf{{General:}}\\\\' + \
          r'\begin{tabular}{l r l}' + \
          r'$d_\mathrm{{PM}}$: & {:.2f} & {}\\'.format(m.pmY.beadDiameter, u.pmY.beadDiameter) + \
          r'$d_\mathrm{{AOD}}$: & {:.2f} & {}\\'.format(m.aodY.beadDiameter, u.aodY.beadDiameter) + \
          r'$d(\SI{{20}}{{pN}})$: & {:.0f} & {}\\'.format(d20, u.yDistVolt) + \
          r'$F_\mathrm{{rip}}$: & {:.1f} & pN\\'.format(ripF)

    if 'hydroCorr' in m.pmY.keys():
        txt += r'$c^\mathrm{{PM}}_\mathrm{{hydro}}$: & {:.2f} & \\'.format(m.pmY.hydroCorr) + \
               r'$c^\mathrm{{AOD}}_\mathrm{{hydro}}$: & {:.2f} & \\'.format(m.aodY.hydroCorr)

    txt += r'\end{tabular}'

    axTxt.text(0.34, 1, txt, **txtArgs)

    # extension zero
    txt = r'\textbf{{Extension zero:}} {}\\\\' + \
          r'\begin{tabular}{l r l}' + \
          r'& PM &\\' + \
          r'$\Delta x_0$: & {:.1f} & {}\\'.format(s.bslCorr.zeroExt, s.bslCorr.zeroExtUnit) + \
          r'\end{tabular}'

    axTxt.text(0.55, 1, txt, **txtArgs)

    # video correction
    txt = r'\textbf{{Video correction:}} {}\\\\' + \
          r'\begin{tabular}{l r r l}' + \
          r'& PM & AOD & \\' + \
          r'$\Delta x$: & {:.1f} & {:.1f} & {}\\'.format(s.bslCorr.pmYZeroVid, s.bslCorr.aodYZeroVid, a.units.pmYZeroVid) + \
          r'Slope: & {:.3f} & {:.3f} & \\'.format(s.bslCorr.pmYZeroVidSlope, s.bslCorr.aodYZeroVidSlope) + \
          r'$r^2$: & {:.2f} & {:.2f} & \\'.format(s.bslCorr.pmYZeroVidR2, s.bslCorr.aodYZeroVidR2) + \
          r'\end{tabular}'

    axTxt.text(0.75, 1, txt, **txtArgs)

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


def segmentSummaryFigByFit(analysis, segId, display=True, saveDir=None):
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

    # plot until rip
    dist = s.ripTrapDist
    queryStr = 'yTrapDist < @dist'

    ax = axExt
    d = s.data.query(queryStr)
    ax.plot(d.yDistVid, d.pmYForce, '.', label='Video', **plotArgs)
    d = a.segments[segId].data.copy()
    d.yDistVolt = d.yDistVolt - a.bslCorr[0].bslCorr.zeroExt
    d = d.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap', **plotArgs)
    d = s.data.query(queryStr)
    ax.plot(d.yDistVolt, d.pmYForce, '.', label='Trap - corr', **plotArgs)
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
    idx = (d.pmYForce - s.bslCorr.zeroVidFitForceLow).abs().idxmin()
    ax.axvline(d.loc[idx].pmYDisp, color='0.7', linestyle='--')
    # slope 1 line
    lim = [d.pmYDisp.min(), d.pmYDisp.max()]
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], 'r', linestyle='--')
    ax.set_title('PM Y Displacement', **axsTtl)
    ax.set_ylabel('Video [nm]', **axsLbl)

    ax = axsDisp[1]
    ax.scatter(d.aodYDisp, d.aodYDispVid, c=d.aodYForce.values, **scatterArgs)
    # fit limit line
    idx = (d.aodYForce - s.bslCorr.zeroVidFitForceLow).abs().idxmin()
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
    plotArgs = {'rasterized': True, 'markersize': 1}
    # bsl pm
    ax = axsBsl[0]
    if 'bsl' in a.segments.keys():
        d = a.segments.bsl.data
        ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL', color='gray', **plotArgs)

    # plot bslBeads
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Beads', zorder=5, **plotArgs)
    # plot fit to determine zeroExt
    x = np.arange(d.yTrapDist.min(), d.yTrapDist.max())
    y = a.meta.pmY.bslCorr.keffExp * x + a.meta.pmY.bslCorr.zeroExtIntercept
    ax.plot(x, y, '.', label='_', zorder=6, **plotArgs)
    # plot bslFlat
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.pmYForce, '.', label='BSL Flat', zorder=3, **plotArgs)
    if s.bslCorr.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslCorr.bslSubAverage)
        ax.plot(d.yTrapDist, d.pmYForce, '.', zorder=4, **plotArgs)

    # general
    ax.set_title('PM Y', **axsTtl)
    ax.set_ylabel('Force [pN]', **axsLbl)

    # bsl aod
    ax = axsBsl[1]
    if 'bsl' in a.segments.keys():
        d = a.segments.bsl.data
        ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL', color='gray', **plotArgs)

    # plot bslBeads
    d = a.segments.bslBeads.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Beads', zorder=5, **plotArgs)
    x = np.arange(d.yTrapDist.min(), d.yTrapDist.max())
    y = a.meta.aodY.bslCorr.keffExp * x + a.meta.aodY.bslCorr.zeroExtIntercept
    ax.plot(x, y, '.', label='_', zorder=6, **plotArgs)
    # plot bslFlat
    d = a.segments.bslFlat.data
    ax.plot(d.yTrapDist, d.aodYForce, '.', label='BSL Flat', zorder=3, **plotArgs)
    if s.bslCorr.bslSubAverage:
        d = averageData(a.segments.bslFlat.data, s.bslCorr.bslSubAverage)
        ax.plot(d.yTrapDist, d.aodYForce, '.', label='_', zorder=4, **plotArgs)
    # general
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

    # more general info
    d20 = s.dist20 if 'dist20' in s.keys() else np.nan
    ripF = s.ripPmYForce if 'ripPmYForce' in s.keys() else np.nan

    txt = r'\textbf{{General:}}\\\\' + \
          r'\begin{tabular}{l r l}' + \
          r'd(\SI{{20}}{{pN}}): & {:.0f} & {}\\'.format(d20, u.yDistVolt) + \
          r'$F_\mathrm{{rip}}$: & {:.1f} & pN\\'.format(ripF)

    if 'hydroCorr' in m.pmY.keys():
        txt += r'$c^\mathrm{{PM}}_\mathrm{{hydro}}$: & {:.2f} & \\'.format(m.pmY.hydroCorr) + \
               r'$c^\mathrm{{AOD}}_\mathrm{{hydro}}$: & {:.2f} & \\'.format(m.aodY.hydroCorr)

    txt += r'\end{tabular}'

    axTxt.text(0.34, 1 , txt, **txtArgs)

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

    axTxt.text(0.5, 1, txt, **txtArgs)

    # video correction
    txt = r'\textbf{{Video correction:}} {}\\\\' + \
          r'\begin{tabular}{l r r l}' + \
          r'& PM & AOD & \\' + \
          r'$\Delta x$: & {:.1f} & {:.1f} & {}\\'.format(s.bslCorr.pmYZeroVid, s.bslCorr.aodYZeroVid, a.units.pmYZeroVid) + \
          r'Slope: & {:.3f} & {:.3f} & \\'.format(s.bslCorr.pmYZeroVidSlope, s.bslCorr.aodYZeroVidSlope) + \
          r'$r^2$: & {:.2f} & {:.2f} & \\'.format(s.bslCorr.pmYZeroVidR2, s.bslCorr.aodYZeroVidR2) + \
          r'\end{tabular}'

    axTxt.text(0.75, 1, txt, **txtArgs)

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

    for a in ac.values():
        for segId in a.bslCorr.keys():
            segmentSummaryFig(a, segId, saveDir=saveDir, display=False)


def bslCorrectAndSummarize(pathIn, pathOut=False, save=False, averageBsl=100, lowForceLimit=5, debug=False):
    """
    Load all :class:`.TweezersAnalysis` files from the given path, run the baseline
    and video corrections and export the summary figure for each segment.

    Args:
        pathIn (str): path to load the data from
        pathOut (str): path to export the summary figues, if `None`, exports to `pathIn` (default: None)
        save (bool): if `True`, the results are saved back to the analysis files that were loaded
        averageBsl (int): passed to :func:`baselineSubtraction`
        lowForceLimit (float): passed to :func:`displacementCorrection`
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
        if 'bslBeads' not in a.segments.keys():
            continue
        # baseline and video corrections
        if a.meta.psdType == 'oscillation':
            osciHydrodynamicCorr(a)
        baselineSubtraction(a, averageBsl=averageBsl)
        zeroDistance(a)
        displacementCorrection(a, lowForceLimit=lowForceLimit)
        detectRip(a)

        # save summary figures
        for segId in a.bslCorr.keys():
            segmentSummaryFig(a, segId, saveDir=pathOut, display=False)

    if save:
        # save results back to analysis files
        ac.save()

    return ac
