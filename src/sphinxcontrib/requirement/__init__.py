
from . import req

__version__ = "1.3.0"

def setup(app):
    return req.setup(app)

