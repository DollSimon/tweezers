import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


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
    for seg in td.segments.values():
        plotSegment(ax, seg['tmin'], seg['tmax'])
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
