import ij.measure.ResultsTable
import ij.WindowManager


class SimpleSheet():
    def __init__(self, title):
        '''
        Construct a new SimpleSheet, an easy to use ResultsTable wrapper.

        Parameters
        ----------
        title : str
            The window title to use for the ResultsTable. If the table exists
            already, than it is captured.

        Example
        -------
        >>> from mina.utilities import SimpleSheet
        >>> my_table = SimpleSheet("My Analysis")
        '''
        # Record the window title
        self.title = title

        # Get the ResultsTable if the window exists or create a new one
        if title in list(ij.WindowManager.getNonImageTitles()):
            self.rt = ij.WindowManager.getWindow(title).getTextPanel(
                    ).getOrCreateResultsTable()
        else:
            self.rt = ij.measure.ResultsTable()

    def writeRow(self, *args):
        '''
        Write a row to the table using data stored in a dict-like structure.

        The data is written by iterating through the keys in whatever order they
        are stored. Thus, if the order does not matter a dictionary can be used
        and if the order does matter, OrderedDict from the collections module
        can be used.

        Parameters
        ----------
        args : dicts or collections.OrderedDicts
            The row of data to be added.

        Example
        -------
        >>> from mina.utilities import SimpleSheet
        >>> my_table = SimpleSheet("My Analysis")
        >>> my_table.writeRow({"Column A": 1, "Column B": 2}, {"Column C": 3})
        '''
        self.rt.incrementCounter()
        for arg in args:
            for key, value in arg.items():
                self.rt.addValue(key, value)

    def writeRows(self, *args):
        '''
        Write a rows to the table using data stored in a dict-like structure.

        The data is written by iterating through the keys in whatever order they
        are stored. Thus, if the order does not matter a dictionary can be used
        and if the order does matter, OrderedDict from the collections module
        can be used. The values are to be lists of the same length. If you need
        to expand a dict with single values by repeating them to the length of
        the other dicts to be written, see the repeatRow method.

        Parameters
        ----------
        args : dicts or collections.OrderedDicts
            The row of data to be added.

        Example
        -------
        >>> from mina.utilities import SimpleSheet
        >>> my_table = SimpleSheet("My Analysis")
        >>> my_table.writeRow({"Column A": 1, "Column B": 2}, {"Column C": 3})
        '''
        # Count the rows in each column
        rows = []
        for arg in args:
            for key, value in arg.items():
                if isinstance(value, list):
                    rows.append(len(value))
                else:
                    raise TypeError("A list was expected, but a %s was provided"
                                    % type(value))

        # Ensure the rows in each column are equal in length
        if len(set(rows)) != 1:
            raise Exception("columns do not contain the same number of rows!")
        else:
            rows = rows[0]

        # Add everything to the table one row at a time
        for row in range(rows):
            self.rt.incrementCounter()
            for arg in args:
                for key, value in arg.items():
                    self.rt.addValue(key, value[row])

    def getRow(self, index):
        '''
        Retrieve the data for a given row as a dictionary.

        Numeric values are converted to a floating point where possible,
        otherwise the values are captured as strings.

        Parameters
        ----------
        index : int
            The row of the data to fetch. Indexing begins at 0.

        Return
        ------
        data : dict
            The row data stored in a dictionary by column name.

        Example
        -------
        >>> from mina.utilities import SimpleSheet
        >>> my_table = SimpleSheet("My Analysis")
        >>> my_table.writeRow({"Column A": 1, "Column B": 2}
        >>> my_table.getRow(0)
        {u'Column A': 1.0, u'Column B': 2.0}
        '''
        columns = self.rt.getHeadings()
        data = {}
        for column in columns:
            value = self.rt.getStringValue(column, index)
            try:
                data[column] = float(value)
            except:
                data[column] = value
        return(data)

    def getColumn(self, column):
        '''
        Numeric values are converted to a floating point where possible,
        otherwise the values are captured as strings.

        Parameters
        ----------
        column : str
            The column name of the data to fetch.

        Return
        ------
        data : dict
            The row data stored in a dictionary by column name.

        Example
        -------
        >>> from mina.utilities import SimpleSheet
        >>> my_table = SimpleSheet("My Analysis")
        >>> my_table.writeRow({"Column A": 1, "Column B": 2})
        >>> my_table.getColumn("Column A")
        [1]
        '''
        nrows = self.rt.getCounter()
        data = []

        for row in range(nrows):
            value = self.rt.getStringValue(column, row)
            try:
                data.append(float(value))
            except:
                data.append(value)
        return(data)

    def updateDisplay(self):
        '''
        Updates the display with the added items.
        '''
        self.rt.show(self.title)
