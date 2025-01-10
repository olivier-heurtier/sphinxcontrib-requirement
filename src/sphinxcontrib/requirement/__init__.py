
from . import req

__version__ = "1.2+snapshot"

def setup(app):
    return req.setup(app)

