import os

from assertEquals.interactive.detail import Detail as _Detail
from assertEquals.interactive.utils import RefreshError
from assertEquals.interactive.summary import Summary as _Summary
from assertEquals.tests.utils import reportersTestCase


RAW = """\
Hey there!
-------------------------------<| assertEquals |>-------------------------------
.EF..
======================================================================
ERROR: test_errs (assertEqualsTests.TestCase)
----------------------------------------------------------------------
Traceback (most recent call last):"""; RAW2= """
  File "/tmp/assertEqualsTests/__init__.py", line 21, in test_errs
    raise StandardError(\'heck\')
StandardError: heck

======================================================================
FAIL: test_fails (assertEqualsTests.TestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/assertEqualsTests/__init__.py", line 18, in test_fails
    self.assert_(0)
AssertionError

----------------------------------------------------------------------
Ran 5 tests in 0.002s

FAILED (failures=1, errors=1)
"""
_RAW = RAW+RAW2

RAW_ONE = """\
Hey there!
-------------------------------<| assertEquals |>-------------------------------
.E..
======================================================================
ERROR: test_errs (assertEqualsTests.TestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/assertEqualsTests/__init__.py", line 21, in test_errs
    raise StandardError(\'heck\')
StandardError: heck

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (errors=1)
"""

TOTALS = ('60%', '1', '1', '5')
TOTALS_ONE = ('0%', '0', '1', '1')


# cross-platform hack
import os, tempfile
hack = os.path.join('', tempfile.gettempdir(), 'assertEqualsTests', '__init__.py')

DATA = {
'test_errs' : ['error', """\
Traceback (most recent call last):
  File "%s", line 21, in test_errs
    raise StandardError(\'heck\')
StandardError: heck""" % hack],
'test_fails' : ['failure', """\
Traceback (most recent call last):
  File "%s", line 18, in test_fails
    self.assert_(0)
AssertionError""" % hack]
        }
DATA_ONE = {
'test_errs' : ['error', """\
Traceback (most recent call last):
  File "%s", line 21, in test_errs
    raise StandardError(\'heck\')
StandardError: heck""" % hack]
        }


class Detail(reportersTestCase):

    def setUpUp(self):
        self.detail = _Detail('assertEqualsTests.TestCase')

    def testCall(self):
        try:
            self.detail._call()
        except RefreshError, err:
            raise StandardError(err.traceback)
        expected = RAW
        actual = self.detail._Detail__raw[:len(RAW)]
        self.assertEqual(expected, actual)

    def testCallCatchesErrorsInChildProcess(self):
        path = os.path.join( self.site_packages
                           , 'assertEqualsTests'
                           , '__init__.py'
                            )
        open(path, 'w+').write("wheeee!")
        self.assertRaises( RefreshError
                         , self.detail._call
                          )
        try:
            self.detail._call()
        except RefreshError, err:
            expected = 'Traceback (most recent call last):'
            actual = err.traceback
            self.assertEqual(expected, actual[:len(expected)])



    # _set_data
    # =========

    def testSetData(self):
        self.detail._Detail__raw = _RAW
        self.detail._set_data()
        expected = DATA
        actual = self.detail.data
        self.assertEqual(expected, actual)

        expected = TOTALS
        actual = self.detail.totals
        self.assertEqual(expected, actual)

    def testSetDataWorksForOneTest(self):
        self.detail._Detail__raw = RAW_ONE
        self.detail._set_data()
        expected = DATA_ONE
        actual = self.detail.data
        self.assertEqual(expected, actual)

        expected = TOTALS_ONE
        actual = self.detail.totals
        self.assertEqual(expected, actual)



RAW2 = """\
Hey there!
-------------------------------<| assertEquals |>-------------------------------
MODULE                                                       PASS FAIL  ERR  ALL
--------------------------------------------------------------------------------
assertEqualsTests.TestCase                                       60%    1    1    5
assertEqualsTests.itDoesExist.TestCase                          100%    0    0    2
assertEqualsTests.itDoesExist.TestCase2                         100%    0    0    1
assertEqualsTests.subpkg.TestCase                               100%    0    0    2
--------------------------------------------------------------------------------
TOTALS                                                        80%    1    1   10
"""
LINES = [ 'Hey there!'
, '-------------------------------<| assertEquals |>-------------------------------'
, 'MODULE                                                       PASS FAIL  ERR  ALL'
, '--------------------------------------------------------------------------------'
, 'assertEqualsTests.TestCase                                       60%    1    1    5'
, 'assertEqualsTests.itDoesExist.TestCase                          100%    0    0    2'
, 'assertEqualsTests.itDoesExist.TestCase2                         100%    0    0    1'
, 'assertEqualsTests.subpkg.TestCase                               100%    0    0    2'
, '--------------------------------------------------------------------------------'
]


RAW_ALL_PASSING = """\
Hey there!
-------------------------------<| assertEquals |>-------------------------------
MODULE                                                       PASS FAIL  ERR  ALL
--------------------------------------------------------------------------------
assertEqualsTests                                                60%    0    0    5
assertEqualsTests.itDoesExist                                   100%    0    0    2
--------------------------------------------------------------------------------
TOTALS                                                       100%    0    0    7
"""
LINES_ALL_PASSING = [ 'Hey there!'
, '-------------------------------<| assertEquals |>-------------------------------'
, 'MODULE                                                       PASS FAIL  ERR  ALL'
, '--------------------------------------------------------------------------------'
, 'assertEqualsTests                                                60%    0    0    5'
, 'assertEqualsTests.itDoesExist                                   100%    0    0    2'
, '--------------------------------------------------------------------------------'
]


RAW_DOTTED = """\
Hey there!
-------------------------------<| assertEquals |>-------------------------------
MODULE                                                       PASS FAIL  ERR  ALL
--------------------------------------------------------------------------------
assertEqualsTests.itDoesExist                                   100%    0    0    2
--------------------------------------------------------------------------------
TOTALS                                                        71%    1    1    7
"""
LINES_DOTTED = [ 'Hey there!'
, '-------------------------------<| assertEquals |>-------------------------------'
, 'MODULE                                                       PASS FAIL  ERR  ALL'
, '--------------------------------------------------------------------------------'
, 'assertEqualsTests.itDoesExist                                   100%    0    0    2'
, '--------------------------------------------------------------------------------'
]
DATA_DOTTED = {
    'assertEqualsTests': [None, None]
  , 'assertEqualsTests.itDoesExist': [('100%', '0', '0', '2'), True]
   }


TRACEBACK = """\
Traceback (most recent call last):
  File "./bin/assertEquals", line 3, in ?
    raise SystemExit(main())
  File "/usr/home/whit537/workbench/assertEquals/site-packages/assertEquals/cli/main.py", line 66, in main
    report = summarize(base, quiet, recursive, run, stopwords)
  File "/usr/home/whit537/workbench/assertEquals/site-packages/assertEquals/cli/reporters.py", line 87, in __call__
    self.modules = self.get_modules()
  File "/usr/home/whit537/workbench/assertEquals/site-packages/assertEquals/cli/reporters.py", line 100, in get_modules
    module = load(self.base)
  File "/usr/home/whit537/workbench/assertEquals/site-packages/assertEquals/cli/utils.py", line 44, in load
    module = __import__(name)
  File "/tmp/assertEqualsTests/__init__.py", line 3, in ?
    from assertEqualsTests import itDoesExist
  File "/tmp/assertEqualsTests/itDoesExist.py", line 3
    wheeee!
          ^
SyntaxError: invalid syntax
"""




class Summary(reportersTestCase):

    def setUpUp(self):
        self.summary = _Summary()


    # _call
    # =====

    def testCall(self):
        self.summary.module = 'assertEqualsTests'
        self.summary.find_only = False
        try:
            self.summary._call()
        except RefreshError, err:
            raise StandardError(err.traceback)
        expected = RAW2
        actual = self.summary._Summary__raw
        self.assertEqual(expected, actual)

    def testCallCatchesErrorsInChildProcess(self):
        path = os.path.join( self.site_packages
                           , 'assertEqualsTests'
                           , '__init__.py'
                            )
        open(path, 'w+').write("wheeee!")
        self.summary.base = 'assertEqualsTests'
        self.summary.find_only = False
        self.assertRaises( RefreshError
                         , self.summary._call
                          )
        try:
            self.summary._call()
        except RefreshError, err:
            expected = 'Traceback (most recent call last):'
            actual = err.traceback
            self.assertEqual(expected, actual[:len(expected)])


    # _set_totals
    # ===========

    def testSetTotals(self):
        self.summary._Summary__raw = RAW2
        self.summary._set_totals()

        expected = LINES
        actual = self.summary._Summary__lines
        self.assertEqual(expected, actual)

        expected = ('80%', '1', '1', '10')
        actual = self.summary.totals
        self.assertEqual(expected, actual)

    def testSetTotalsAllPassing(self):
        self.summary._Summary__raw = RAW_ALL_PASSING
        self.summary._set_totals()

        expected = LINES_ALL_PASSING
        actual = self.summary._Summary__lines
        self.assertEqual(expected, actual)

        expected = ('100%', '0', '0', '7')
        actual = self.summary.totals
        self.assertEqual(expected, actual)

    def testSetTotalsDotted(self):
        self.summary._Summary__raw = RAW_DOTTED
        self.summary._set_totals()

        expected = LINES_DOTTED
        actual = self.summary._Summary__lines
        self.assertEqual(expected, actual)

        expected = ('71%', '1', '1', '7')
        actual = self.summary.totals
        self.assertEqual(expected, actual)



    # _set_data
    # =========

    def testSetData(self):
        self.summary._Summary__raw = RAW2
        self.summary._set_totals()

        expected = LINES
        actual = self.summary._Summary__lines
        self.assertEqual(expected, actual)

        expected = ('80%', '1', '1', '10')
        actual = self.summary.totals
        self.assertEqual(expected, actual)

    def testSetDataDotted(self):
        self.summary._Summary__lines = LINES_DOTTED
        self.summary._set_data()
        expected = DATA_DOTTED
        actual = self.summary.data
        self.assertEqual(expected, actual)
