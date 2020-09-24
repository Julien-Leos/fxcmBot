class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

def dateDiffInMillisecond(date1, date2):
    delta = date1 - date2
    return (delta.days * 24 * 60 * 60 * 1000) + (delta.seconds * 1000) + (delta.microseconds / 1000)