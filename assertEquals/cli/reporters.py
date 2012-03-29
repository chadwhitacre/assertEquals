import os
import sys
import types
import unittest
from StringIO import StringIO

from assertEquals.cli.utils import *


def detail(module_name, testcase_name):
    """Given a module name and a TestCase name, return a detail report.
    """

    # Get a TestSuite for a single TestCase.
    # ======================================

    try:
        module = load(module_name)
        testcase = getattr(module, testcase_name)
    except:
        raise ImportError("Unable to find %s in " % testcase_name +
                          "%s." % module_name)
    if not isinstance(testcase, (type, types.ClassType)):
        raise TypeError("%s is not a TestCase." % testcase_name)
    if not issubclass(testcase, unittest.TestCase):
        raise TypeError("%s is not a TestCase." % testcase_name)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testcase)


    # Run tests.
    # ==========
    # We only write our report to stdout after the tests have been run. This is
    # necessary because we don't want to clutter the report with an program
    # output and/or pdb sessions.

    report = StringIO()
    print >> report, BANNER
    runner = unittest.TextTestRunner(report)
    runner.run(suite)
    return report.getvalue()


class _Summarize:
    """Given a dotted module name, return a summary report on its tests.

    The format of the report is:

        -------------<| assertEquals |>-------------
        <header row>
        --------------------------------------------
        <name> <passing> <failures> <errors> <total>
        --------------------------------------------
        TOTALS <passing> <failures> <errors> <total>

    Boilerplate rows are actually 80 characters long, though. <passing> is given
    as a percentage (with a terminating percent sign); the other three are given
    in absolute terms. Data rows will be longer than 80 characters iff the field
    values exceed the following character lengths:

        name        60
        failures     4
        errors       4
        total        4

    If run is False, then no statistics on passes, failures, and errors will be
    available, and the output for each will be a dash character ('-'). run
    defaults to True. All submodules will also be included in the output, unless
    their name contains a stopword.

    The report is delivered after it is fully complete. We do this rather than
    delivering data in real time in order to avoid program output and pdb
    sessions from cluttering up our report.

    This callable is implemented as a class to make testing easier. It should be
    used via the singleton named summarize.

    """

    def __init__(self):
        """
        """
        self.report = StringIO()
        self.runner = unittest.TextTestRunner(dev_null())
        self.make_suite = unittest.defaultTestLoader.loadTestsFromTestCase


    def __call__(self, module, find_only=False, stopwords=()):
        """
        """
        self.module = module
        self.find_only = find_only
        self.stopwords = stopwords

        self.find_testcases()

        self.print_header()
        self.print_body()
        self.print_footer()

        return self.report.getvalue()


    def load_testcases(self, module):
        """Given a module, return a list of TestCases defined there.

        We only keep the TestCase if it has tests.

        """
        testcases = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, (type, types.ClassType)):
                if issubclass(obj, unittest.TestCase):
                    for _name in dir(obj):
                        if _name.startswith('test'):
                            name_dotted = module.__name__+'.'+obj.__name__
                            testcases.append((name_dotted, obj))
                            break
        return testcases


    def find_testcases(self):
        """Store a list of TestCases below the currently named module.
        """

        basemod = load(self.module)
        testcases = self.load_testcases(basemod)

        path = os.path.dirname(basemod.__file__)
        for name in sorted(sys.modules):
            if name == basemod.__name__:
               continue
            try:
                for word in self.stopwords:
                    if word and word in name:
                        stop = True
                        raise StopWord
            except StopWord:
                continue
            if not name.startswith(self.module):
                continue
            module = sys.modules[name]
            if module is None:
                continue
            if not module.__file__.startswith(path):
                # Skip external modules that ended up in our namespace.
                continue
            testcases.extend(self.load_testcases(module))

        self.__testcases = testcases


    def print_header(self):
        """Print the report header.
        """
        print >> self.report, BANNER
        print >> self.report, HEADERS
        print >> self.report, BORDER


    def print_body(self):
        """Print the report body; set three members on self for print_footer.
        """

        tfail = terr = tall = 0

        for name, testcase in self.__testcases:

            pass5 = fail = err = 0 # FWIW: pass -> pass% -> pass5
            suite = self.make_suite(testcase)
            all = suite.countTestCases()


            # Run tests if requested.
            # =======================

            if not self.find_only:
                pass5 = fail = err = 0
                if all != 0:
                    result = self.runner.run(suite)
                    fail = len(result.failures)
                    err = len(result.errors)
                    pass5 = (all - fail - err) / float(all)
                    pass5 =  int(round(pass5*100))

                tall += all
                tfail += fail
                terr += err

            else:
                pass5 = fail = err = '-'
                tall += all


            # Format and print.
            # =================

            name = name.ljust(60)
            sfail, serr, sall = [str(s).rjust(4) for s in (fail, err, all)]
            if pass5 == '-':
                pass5 = '  - '
            else: # int
                pass5 = str(pass5).rjust(3)+'%'
            print >> self.report, name, pass5, sfail, serr, sall


        self.__totals = tfail, terr, tall


    def print_footer(self, *totals):
        """Print the report footer; uses the 3 integers set by print_body.
        """

        tfail, terr, tall = self.__totals

        if not self.find_only:
            tpass5 = 0
            if tall:
                tpass5 = (tall - tfail - terr) / float(tall)
            tpass5 = int(round(tpass5*100))
            tpass5 = str(tpass5).rjust(3)+'%'
        else:
            tfail = '-'
            terr = '-'
            tpass5 = '- '

        raw = (tpass5, tfail, terr, tall)
        tpass5, tfail, terr, tall = [str(s).rjust(4) for s in raw]

        print >> self.report, BORDER
        print >> self.report, "TOTALS".ljust(60), tpass5, tfail, terr, tall


summarize = _Summarize()
