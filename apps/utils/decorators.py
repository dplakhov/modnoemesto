def cached_property(fn):
    def getinstance(self, *args, **kwarg):
        cashed = '_%s' % fn.__name__
        if not hasattr(self, cashed):
            setattr(self, cashed, fn(self, *args, **kwarg))
        return getattr(self, cashed)
    return property(getinstance)