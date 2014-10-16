import json


def write_data(fileName, data):
    """
    Write data structure to file with JSON header and tab-separated values.

    Args:
        fileName (pathlib.Path): file to write to
        data (pandas.DataFrame): data to write
    """

    with fileName.open(mode='w') as f:
        f.write(json.dumps(data.meta, indent=4))
        f.write("\n\n#### DATA ####\n\n")

    header = [column + ' (' + data.units[column] + ')' for column in data.columns.values.tolist()]
    data.to_csv(path_or_buf=fileName.__str__(), header=header, sep='\t', mode='a', index=False)