import logging as log
from IPython.display import clear_output


def strToBool(value):
    """
    Convert a string representation of a boolean value to a :class:`bool`.

    Args:
        value (str): string to convert

    Returns:
        :class:`bool`
    """

    true = ['true', 't', 'yes', '1', 'on']
    false = ['false', 'f', 'no', '0', 'off']

    value = value.lower()
    if value in true:
        return True
    elif value in false:
        return False
    else:
        raise ValueError


def configLogger(debug=False):
    """
    Configure the logger for use e.g. in a script or jupyter notebook.

    Args:
        debug (`bool`): turn on / off debug messages
    """

    # ToDo: check if this still applies
    # the basicConfig is not working in iPython notebooks :(
    # log.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    logger = log.getLogger()
    if debug:
        logger.setLevel(log.DEBUG)
    else:
        logger.setLevel(log.INFO)


def nbUpdateProgress(progress):
    """
    Create and update a progress bar in a Jupyter Notebook.

    Args:
        progress (float): percentage of progress
    """

    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))

    clear_output(wait=True)
    text = "Progress: [{0}] {1:.1f}%".format("#" * block + "-" * (bar_length - block), progress * 100)
    print(text)
