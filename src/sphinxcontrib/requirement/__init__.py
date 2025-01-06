
from . import req

__version__ = "1.1+snapshot"

def setup(app):
    return req.setup(app)

