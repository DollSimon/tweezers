from pathlib import Path
import re
from tweezer import UnitDict


class TxtFileMpi():
    """
    A helper object to extract data from MPI-styled txt-files. Especially to get all header lines and all data lines.
    Note that this reads the files with `UTF-8` encoding.
    """

    def __init__(self, path):
        """
        Constructor for TxtFileMpi

        Args:
            path (:class:`patlhlib.Path`): path to file to read, if the input is of a different type, it is given to
                                           :class:`pathlibh.Path` to try to create an instance
        """

        # adjust input to the correct format
        if not isinstance(path, Path):
            self.path = Path(path)
        else:
            self.path = path

        # JSON header present?
        with self.path.open(encoding='utf-8') as f:
            firstLine = f.readline().strip()
        if firstLine.startswith('{'):
            self.isJson = True
        else:
            self.isJson = False

    def get_header(self):
        """
        Returns all header lines of the file and if applicable (no JSON header) a :class:`tweezer.UnitDict` with the
        units of the data columns.

        Returns:
            :class:`list` of :class:`str` and either ``None`` or :class:`tweezer.UnitDict`
        """

        if self.isJson:
            return self.read_data_json(get='header')
        else:
            return self.read_data(get='header')

    def get_data(self):
        """
        Returns the column header and all data lines from the file as one big string.

        Returns:
            :class:`list` of :class:`str` and :class:`str`
        """

        if self.isJson:
            return self.read_data_json(get='data')
        else:
            return self.read_data(get='data')

    def get_trial_number(self):
        """
        Extract the trial number from the file name. The trial number is everything before the first '_' in the name.
        If no '_' is present, the whole name without the suffix is returned

        Returns:
            :class:`str`
        """

        return self.path.stem.split('_')[0]

    def read_data_json(self, get='data'):
        """
        Read a data file with a JSON styled header.

        Args:
            get (str): either 'data' or 'header', determines what to return

        Returns:
            if 'get' is 'data: columnHeader (:class:`list` of :class:`str`), dataLines (:class:`str`)
            if 'get' is 'header': headerLines (:class:`list` of :class:`str`)
        """

        with self.path.open(encoding='utf-8') as f:
            # generator to strip each line
            strippedLines = (line.strip() for line in f)
            if get == 'header':
                headerLines = []
                for line in strippedLines:
                    if not line:
                        continue  # ignore empty lines
                    elif line == '#### DATA ####':
                        break
                    headerLines.append(line)
                return headerLines, None
            else:
                # TODO With pandas 0.15, this can probably be simplified a bit since it will support skipping empty
                # lines (a potential empty line between column header and data requires all this Affenzirkus)
                columnHeader = None
                dataLines = ''
                # go until beginning of data
                for line in strippedLines:
                    if line == '#### DATA ####':
                        break
                # find first data line, the last line before that is the header line
                for line in strippedLines:
                    if not line:
                        continue
                    elif line[0].isdigit() or line.startswith('-'):
                        dataLines += line + '\n'
                        break
                    else:
                        columnHeader = line
                # read all the other data lines
                for line in strippedLines:
                    if line:
                        dataLines += line + '\n'
                columnHeader = columnHeader.split(sep='\t')
                return columnHeader, dataLines

    def read_data(self, get='data'):
        """
        Reads the data file and splits its content between header lines and data lines. The 'get' parameter
        determines what should be returned. Even if only the header should be returned, we still have to scan through
        the whole file since there are some of the old ones which have header lines somewhere at the end.

        Args:
            get (str): either 'data' or 'header', determines what to return

        Returns:
            if 'get' is 'data: columnHeader (:class:`list` of :class:`str`), dataLines (:class:`str`)
            if 'get' is 'header': headerLines (:class:`list` of :class:`str`), units (:class:`collections.OrderedDict`)
        """

        headerLines = []
        columnHeader = None
        dataLines = ''

        with self.path.open(encoding='utf-8') as f:
            # generator to strip each line
            strippedLines = (line.strip() for line in f)
            for line in strippedLines:
                if not line:
                    # skip empty lines including lines that only contain whitespaces
                    continue

                # check for data line
                if line[0].isdigit() or line.startswith('-'):
                    # only store the data line if we should return the data
                    if get == 'data':
                        dataLines += line + '\n'
                    # if the column header line is not yet set, then it is the first time that we reached a data line
                    # use the last headerLine as column header
                    if not columnHeader:
                        columnHeader = headerLines.pop()
                # or header line
                else:
                    headerLines.append(line)

        # get column units for metadata
        regex = re.compile('(\w+(\s\w+)?)( \(([^)]*)\))?')
        res = regex.findall(columnHeader)
        units = UnitDict()
        for (column, tmp, bUnit, unit) in res:
            if unit:
                # if unit present, store it
                units[column] = unit
        # get column titles, delete whitespaces for consistency
        columns = [title[0].replace(' ', '') for title in res]

        if get == 'data':
            return columns, dataLines
        else:
            return headerLines, units