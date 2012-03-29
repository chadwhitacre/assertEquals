import os
import sys
import tempfile
import unittest


MODULE = """\
import unittest

class TestCase(unittest.TestCase):
    def test_foo(self):
        pass
    def test_bar(self):
        pass

class TestCase2(unittest.TestCase):
    def test_blam(self):
        pass

"""

MODULE_2 = """\
import unittest

# This module is never imported, and therefore never shows up in our reports.

class TestCase(unittest.TestCase):
    def test_foo(self):
        pass
    def test_bar(self):
        pass

class TestCase2(unittest.TestCase):
    def test_blam(self):
        pass

"""

_INIT__2 = """\
import unittest

class TestCase(unittest.TestCase):
    def test_foo(self):
        pass
    def test_bar(self):
        pass

class TestCase2(unittest.TestCase):
    pass

"""

_INIT__ = """\
import unittest

from assertEqualsTests import itDoesExist, subpkg


def my_program():
    print 'Hey there!'

class TestCase(unittest.TestCase):

    def test_passes(self):
        self.assert_(1)

    def test_does_nothing(self):
        pass

    def test_fails(self):
        self.assert_(0)

    def test_errs(self):
        raise StandardError('heck')

    def test_prints_stuff(self):
        my_program()

"""



class reportersTestCase(unittest.TestCase):
    """A base class for reporter tests. Provides setUpUp and pkg hooks.

    """

    # fixture
    # =======

    def setUp(self):
        self.tmp = tempfile.gettempdir()
        self.site_packages = os.path.join(self.tmp, 'site-packages')
        sys.path.insert(0, self.site_packages)

        # [re]build a temporary package tree in /tmp/site-packages/
        self.removeTestPkg()
        self.buildTestPkg()

        if hasattr(self, 'setUpUp'):
            self.setUpUp()

    def tearDown(self):
        if self.site_packages in sys.path:
            sys.path.remove(self.site_packages)
        for pkgname in os.listdir(self.site_packages):
            for modname in list(sys.modules.keys()):
                if modname.startswith(pkgname):
                    del sys.modules[modname]
        self.removeTestPkg()


    # test package
    # ============
    # pkg is a list of strings and tuples. If a string, it is interpreted as a
    # path to a directory that should be created. If a tuple, the first element
    # is a path to a file, the second is the contents of the file. You must use
    # forward slashes in your paths (they will be converted cross-platform). Any
    # leading slashes will be removed before they are interpreted.
    #
    # site_packages is the filesystem path under which to create the test site.

    site_packages = ''                                  # set in setUp
    pkg = [  'assertEqualsTests'                           # can be overriden
          , ('assertEqualsTests/__init__.py', _INIT__)
          , ('assertEqualsTests/itDoesExist.py', MODULE)
          ,  'assertEqualsTests/subpkg'
          , ('assertEqualsTests/subpkg/__init__.py', _INIT__2)
           ]

    def buildTestPkg(self):
        """Build the package described in self.pkg.
        """
        os.mkdir(self.site_packages)
        for item in self.pkg:
            if isinstance(item, basestring):
                path = self.convert_path(item.lstrip('/'))
                path = os.sep.join([self.site_packages, path])
                os.mkdir(path)
            elif isinstance(item, tuple):
                filepath, contents = item
                path = self.convert_path(filepath.lstrip('/'))
                path = os.sep.join([self.site_packages, path])
                file(path, 'w').write(contents)

    def removeTestPkg(self):
        """Remove the package described in self.pkg.
        """
        if not os.path.isdir(self.site_packages):
            return
        for root, dirs, files in os.walk(self.site_packages, topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir(self.site_packages)

    def convert_path(self, path):
        """Given a Unix path, convert it for the current platform.
        """
        return os.sep.join(path.split('/'))

    def convert_paths(self, paths):
        """Given a tuple of Unix paths, convert them for the current platform.
        """
        return tuple([self.convert_path(p) for p in paths])
