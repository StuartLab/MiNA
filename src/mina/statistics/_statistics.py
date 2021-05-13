

def mean(data):
    '''
    Return the mean value of numeric data.

    Parameters
    ----------
    data : list of numeric type
        The data to compute the mean from.

    Return
    ------
    average : float
        The mean of the data or "nan" if the set is empty.

    Example
    -------
    >>> from mina.statistics import mean
    >>> mean([1, 3, 5])
    3.0
    >>> mean([1, 3, 5, 7.5])
    4.125
    '''
    n = len(data)
    if n >= 1:
        return(sum(data) / float(n))
    else:
        return(float("nan"))


def median(data):
    '''
    Return the median (middle value) of numeric data.

    When the number of data points is odd, return the middle data point.
    When the number of data points is even, the median is interpolated by
    taking the average of the two middle values:

    Parameters
    ----------
    data : list of numeric type
        The data to get the median from.

    Return
    ------
    average : int or float
        The median value of the data or 'nan' if the set is empty.

    Example
    -------
    >>> from mina.statistics import median
    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4.0

    Notes
    -----
    This implementation is adapted from the statistics module of the CPython
    standard library implementation. It can be viewed on GitHub at https://githu
    b.com/python/cpython/blob/30afc91f5e70cf4748ffac77a419ba69ebca6f6a/Lib/stati
    stics.py#L364. Rather than raise a specific error on an empty set, it simply
    returns a "nan" float.
    '''
    data = sorted(data)
    n = len(data)
    if n == 0:
        return(float("nan"))
    if n % 2 == 1:
        return data[n // 2]
    else:
        i = n // 2
        return (data[i - 1] + data[i]) / 2.0


def stdev(data):
    '''
    Calculate the population standard deviation.

    Parameters
    ----------
    data : list of numeric type
        The data to compute the population standard deviation from.

    Return
    ------
    deviation : float
        The population standard deviation of the data or "nan" if the set is
        empty.

    Example
    -------
    >>> from mina.statistics import stdev
    >>> stdev([1, 3, 5])
    1.63299316186
    >>> stdev([1, 3, 5, 7.5])
    2.40767003553
    '''
    n = len(data)
    if n >= 1:
        average = mean(data)
        sse = sum([(x - average) ** 2.0 for x in data])
        return((sse / n ) ** 0.5)
    else:
        return(float("nan"))
