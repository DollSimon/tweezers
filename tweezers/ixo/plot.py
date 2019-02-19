from matplotlib.offsetbox import AuxTransformBox, AnchoredOffsetbox, TextArea, VPacker, HPacker
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox


class ScaleBar(AnchoredOffsetbox):
    """
    Scale bar class to allow adding scale bars to `matplotlib.axis.Axis`
    """

    def __init__(self, ax, pos, length, thickness, vertical=False, text=None, units=None, color=None, textprops=None,
                 **kwargs):
        """
        Create the scale bar. It still has to be added to the `matplotlib.axis.Axis`.

        The length of the scale bar is passed in data units of the axes, thickness is passed in axis coordinates.
        This allows to have a fixed thickness even if the plotting range changes.

        Example:
            This creates a vertical scale bar.\

                >>> bar = ScaleBar(ax, (0.1, 0.1), 30, 5, vertical=True)
                >>> ax.add_artist(bar)

        Args:
            ax (`matplotlib.axis.Axis`): axis object to which the scale bar is added (used for coordinate
                                         transformations, not the actual adding)
            pos (tuple): 2-tuple with x and y values for the scale bar position, given in axis-coordinates
            length (float): length of the scale bar in data units of x-axis if `vertical=False` and of y-axis otherwise
            thickness (float): thickness of the scale bar in axis units
            vertical (bool): create a vertical scale bar? horizontal otherwise (default: False)
            text (str): text for the scale bar; if nothing is specified, `lengt` is displayed
            units (str): specify the units the scalebar displays; if passed, this is appended to `length` for the label;
                         this is a convenience parameter to not having to use `text` manually
            color: matplotlib color
            textprops (dict): text arguments like fontsize can be specified here and are passed on to the text
            **kwargs: key-word arguments passed to `matplotlib.offsetbox.AnchoredOffsetbox`
        """

        loc = 2
        if not color:
            color = 'black'
        _textprops = textprops if textprops else {}
        # transform length and thickness to height and width
        transBox = Bbox.from_bounds(0, 0, thickness, thickness).inverse_transformed(ax.transData)

        allTxtProps = {'ha': 'left', 'va': 'bottom', 'color': color}

        # settings for vertical or horizontal
        if vertical:
            height = length
            width = transBox.width
            Packer = HPacker
            allTxtProps['rotation'] = 90
        else:
            height = transBox.height
            width = length
            Packer = VPacker
            allTxtProps['rotation'] = 0

        # make bar
        bar = AuxTransformBox(ax.transData)
        bar.add_artist(Rectangle((0, 0), width, height, fill=True, fc=color))

        if not text:
            text = '{}'.format(length)
            if units:
                text += ' ' + units

        allTxtProps.update(_textprops)
        txt = TextArea(text, textprops=allTxtProps)

        if vertical:
            children = [txt, bar]
        else:
            children = [bar, txt]

        box = Packer(children=children, align='center', pad=0, sep=2)

        AnchoredOffsetbox.__init__(self, loc, child=box, frameon=False, bbox_to_anchor=pos, bbox_transform=ax.transAxes,
                                   **kwargs)


def addScaleBar(ax, *args, **kwargs):
    """
    Utility function to add a scalebar to a plot.

    Args:
        ax (`matplotlib.axes.Axes`): axes object to which to add the scale bar
        *args: arguments passed on to `.ScaleBar`
        **kwargs: key-word arguments passed on to `.ScaleBar`

    Returns:
        `.ScaleBar`
    """

    bar = ScaleBar(ax, *args, **kwargs)
    ax.add_artist(bar)
    return bar
