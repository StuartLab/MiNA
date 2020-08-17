import collections


def commentToDict(raw_comment, maintain_order=True):
    '''
    Process a string comment into key value pairs.

    Function allows a comment to be provided where key value pairs are indicated
    as key=value. Multiple key value pairs can be provided by separating each
    with a comma. Leading and trailing white space around the keys and values is
    removed before storing them in the dictionary.

    Parameters
    ----------
    raw_comment : str
        The original comment as a string.
    maintain_order : bool
        Should the order of the key value pairs be maintained? If True, an
        OrderedDict is used instead of a plain dictionary.
    '''
    if maintain_order is True:
        smart_comment = collections.OrderedDict()
    else:
        smart_comment = {}

    # Parse the comment
    if raw_comment != None and raw_comment != "":
        if "=" in raw_comment:
            comments = raw_comment.split(",")
            for comment in comments:
                key = comment.split("=")[0].strip()
                value = comment.split("=")[1].strip()
                smart_comment[key] = value
        else:
            smart_comment["Comment"] = raw_comment

    # Return the dict
    return(smart_comment)


def repeatDictValues(row, n_repeats=1):
    '''
    Repeat the values of a dict to be a dict of lists with the value repeated.

    Parameters
    ----------
    row : dict or OrderedDict
        The row-like dict to be repeated into a table like dict (list of values
        for each key).
    n_repeats : how many times should the value be repeated for each column.

    Return
    ------
    repeated : dict
        The table like dictionary where each key indexes a list of repeated
        values.
    '''
    if isinstance(row, collections.OrderedDict):
        repeated = collections.OrderedDict()
    else:
        repeated = {}

    for key, value in row.items():
        repeated[key] = [value] * n_repeats

    return(repeated)
