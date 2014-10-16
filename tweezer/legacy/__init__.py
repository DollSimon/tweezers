def read(fileName, fileType='man_data', **kwargs):
    """
    Convenience function to read the data from a given tweezer file name into \
    a pandas DataFrame. It tries to make an educated guess about the fileType\
    of the file in question and to dispatch the appropriate function call.

    :param fileName: (path) to the file to be read into a pandas.DataFrame

    :return data: (pandas.DataFrame) If applicable this return type contains \
    the time series data in a DataFrame and any metadata as its attributes
    """
    # TODO: find a place for this convenience wrapper in another module to keep the top level clean.
    from tweezer.legacy.io import (read_tdms,
                            read_tweebot_data,
                            read_tweebot_logs,
                            read_tweezer_image_info,
                            read_tracking_data,
                            read_tweezer_txt,
                            read_thermal_calibration,
                            read_tweezer_power_spectrum)

    # classify file
    try:
        ftype = classify(fileName)
        if 'unknown' in ftype.lower():
            ftype = fileType
    except:
        print("Can't classify the file type myself. Trying the fileType \
            default ('man_data')")
        ftype = fileType

    if 'frequency' in kwargs:
        f = kwargs['frequency']
        read_tweezer_power_spectrum = partial(read_tweezer_power_spectrum,
                                              frequency=f)

        read_tdms = partial(read_tdms, frequency=f)

    # use dictionary to dispatch the appropriate function
    # (functions are first-class citizens!)
    readMapper = {
        'man_data': read_tweezer_txt,
        'man_pics': read_tweezer_image_info,
        'man_track': read_tracking_data,
        'tc_psd': read_tweezer_power_spectrum,
        'tc_ts': read_thermal_calibration,
        'bot_data': read_tweebot_data,
        'bot_tdms': read_tdms,
        'bot_log': read_tweebot_logs
    }

    data = readMapper[ftype.lower()](fileName)

    return data
