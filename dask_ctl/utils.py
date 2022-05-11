import asyncio


def run_sync(f, *args, **kwargs):
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(f(*args, **kwargs))
    except RuntimeError:
        f = asyncio.run_coroutine_threadsafe(f(*args, **kwargs), loop)
        return f.result()


class _AsyncTimedIterator:

    __slots__ = ("_iterator", "_timeout", "_sentinel")

    def __init__(self, iterable, timeout):
        self._iterator = iterable.__aiter__()
        self._timeout = timeout

    async def __anext__(self):
        return await asyncio.wait_for(self._iterator.__anext__(), self._timeout)


class AsyncTimedIterable:
    """Wrapper for an AsyncIterable that adds a timeout

    See https://stackoverflow.com/a/50245879/1003288

    """

    __slots__ = ("_factory",)

    def __init__(self, iterable, timeout=None):
        self._factory = lambda: _AsyncTimedIterator(iterable, timeout)

    def __aiter__(self):
        return self._factory()
