from dist import *
try:
    from local import *
except ImportError:
    pass

import mongoengine

mongoengine.connect('social')
