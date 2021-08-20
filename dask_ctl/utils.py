from tornado.ioloop import IOLoop
from distributed.cli.utils import install_signal_handlers


loop = IOLoop.current()
install_signal_handlers(loop)
