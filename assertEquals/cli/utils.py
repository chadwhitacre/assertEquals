import unittest

__all__ = ( 'BANNER', 'BORDER', 'HEADERS', 'StopWord', 'dev_null', 'flatten'
          , 'load')



C = '-'
BANNER = C*31 + "<| assertEquals |>" + C*31
BORDER = C * 80
HEADERS = ' '.join(["MODULE".ljust(60), "PASS", "FAIL", " ERR", " ALL"])


class StopWord(StandardError):
    """Signals a stop word within a dotted module name.
    """


class dev_null:
    """Output buffer that swallows everything.
    """
    def write(self, wheeeee):
        pass


def flatten(_suite):
    """Given a TestSuite, return a flattened TestSuite.
    """
    suite = unittest.TestSuite()
    for item in _suite:
        if isinstance(item, unittest.TestCase):
            suite.addTest(item)
        if isinstance(item, unittest.TestSuite):
            suite.addTests(flatten(item))
    return suite


def load(name):
    """Given a dotted name, return the last-named module instead of the first.

        http://docs.python.org/lib/built-in-funcs.html

    """
    module = __import__(name)
    for _name in name.split('.')[1:]:
        module = getattr(module, _name)
    return module
