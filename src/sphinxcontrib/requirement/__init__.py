
from . import req

__version__ = "1.0+snapshot"

def setup(app):
    return req.setup(app)

