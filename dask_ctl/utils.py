import asyncio
import concurrent.futures


def run_sync(f, *args, **kwargs):
    async def canary():
        """An empty coroutine to check if we are inside an event loop"""
        pass

    try:
        asyncio.run(canary())
    except RuntimeError:
        # event loop is already running and not running with jupyter (eg nest-asyncio)
        pass
    else:
        return asyncio.run(f(*args, **kwargs))

    with concurrent.futures.ThreadPoolExecutor(1) as tpe:
        return tpe.submit(asyncio.run, f(*args, **kwargs)).result()


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
