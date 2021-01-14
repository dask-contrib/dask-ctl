def format_table(rows, headers=None):
    """Formats list of lists into a table.

    If headers is not provided the first row will be used as headers.

    Examples
    --------

    >>> print(format_table([["foo", "bar"], ["fizz", "buzz"]], headers=["hello", "world"]))
    HELLO  WORLD
    foo    bar
    fizz   buzz

    """

    if headers is None:
        headers = rows.pop(0)

    if len(set([len(row) for row in rows] + [len(headers)])) != 1:
        raise ValueError("Headers and each row must be lists of equal length")

    col_widths = [
        max([len(str(row[i])) for row in rows] + [len(str(headers[i]))])
        for i in range(len(headers))
    ]

    try:
        rows.insert(0, [h.upper() for h in headers])
    except AttributeError:
        raise ValueError("Headers must be strings")

    def justify(value, length):
        if isinstance(value, int) or isinstance(value, float):
            return str(value).rjust(length)
        return str(value).ljust(length)

    return "\n".join(
        [
            "  ".join([justify(row[i], col_widths[i]) for i in range(len(row))])
            for row in rows
        ]
    )
