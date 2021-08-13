from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO

from tornado.ioloop import IOLoop
from distributed.cli.utils import install_signal_handlers


loop = IOLoop.current()
install_signal_handlers(loop)


@contextmanager
def suppress_output():
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        yield
