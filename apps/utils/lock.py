from django.core.cache import cache
import time

class CacheLock():
    def __init__(self, key):
        self.key = "lock.%s" % key

    def __enter__(self):
        while True:
            value = cache.add(self.key, "1", 60000)
            if value == True:
                return
            time.sleep(.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        cache.delete(self.key)
        return False
