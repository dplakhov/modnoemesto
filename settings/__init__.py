from dist import *
try:
    from local import *
except ImportError:
    pass

import mongoengine
mongoengine.connect('social')

import djcelery
djcelery.setup_loader()