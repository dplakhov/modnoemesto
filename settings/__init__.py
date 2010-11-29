import sys
import mongoengine

from dist import *
try:
    from local import *
except ImportError:
    pass


mongoengine.connect(MONGO_DATABASE +
                    ('_test' if 'test' in sys.argv else ''),
                    host=MONGO_HOST
    )

import djcelery
djcelery.setup_loader()