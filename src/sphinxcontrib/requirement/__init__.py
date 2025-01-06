
from . import req

__version__ = "1.1.0"

def setup(app):
    return req.setup(app)

