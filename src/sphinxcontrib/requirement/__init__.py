
from . import req

__version__ = "1.3+snapshot"

def setup(app):
    return req.setup(app)

