import sys
import mongoengine

from dist import *
try:
    from local import *
except ImportError:
    pass

mongoengine.connect('social_test' if 'test' in sys.argv else 'social')

import djcelery
djcelery.setup_loader()