import logging as log


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


def configLogger(verbose=True):
    #ToDo: docstring

    # ToDo: check if this still applies
    # the basicConfig is not working in iPython notebooks :(
    # log.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    logger = log.getLogger()
    if verbose:
        logger.setLevel(log.INFO)
    else:
        logger.setLevel(log.WARNING)