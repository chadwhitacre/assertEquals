import logging
import os
import re
import subprocess
import sys

from assertEquals.cli.utils import BANNER, BORDER, HEADERS
from assertEquals.interactive.utils import RefreshError, Process


BREAK1 = ("=" * 70) + '\n'
BREAK2 = ("-" * 70) + '\n'

ALL_RE = re.compile('Ran (\d*) test')
OBJ_RE = re.compile('\((\S)\)')
FAIL_RE = re.compile('failures=(\d*)')
ERR_RE = re.compile('errors=(\d*)')

logger = logging.getLogger('assertEquals.tests')


class Detail:
    """Represent the data from an inter-process detail() call.

    This is designed to be a persistent object. Repeated calls to refresh will
    update the dataset. Unlike Summary, there are no partial updates here. The
    assumption is that you will always want to re-run all tests at once. There
    is a show flag for each record; only items for which this are true are
    included in the name, index and __len__ calls.

    """

    module = ''     # the current module dotted module name
    data = None     # a dictionary, {name:<2-list>}:
                    #   0 'error' or 'failure'
                    #   1 full report
    names = None    # a sorted list of names for which show is True
    totals = ()     # a 4-tuple: (pass5, fail, err, all)


    def __init__(self, module):
        """
        """
        self.module = module
        self.data = {}
        self.names = []

    def __repr__(self):
        return "<Detail (%d tests)>" % len(self.names)



    # Container emulation
    # ===================

    def __getitem__(self, i):
        """Takes an int index into self.names
        """
        name = self.names[i]
        return [name] + self.data[name]

    def __len__(self):
        return len(self.names)

    def __iter__(self):
        return self.names.__iter__()


    # Main callable
    # =============

    def refresh(self):
        """Re-run our tests.
        """
        self._call()
        self._set_data()


    # Helpers
    # =======

    def _call(self):
        """Invoke a child process and return its output.

        We hand on our environment and any sys.path manipulations to the child,
        and we capture stderr as well as stdout so we can handle errors.

        """
        module, testcase = self.module.rsplit('.', 1)
        args = ( sys.executable
               , '-u' # unbuffered, so we can interact with it
               , sys.argv[0]
               , '--scripted'
               , '--testcase=%s' % testcase
               , module
                )
        environ = os.environ.copy()
        environ['PYTHONPATH'] = ':'.join(sys.path)

        proc = Process(args=args, env=environ)

        raw = proc.communicate()
        if BANNER not in raw:
            raise RefreshError(raw)
        self.__raw = raw


    def _set_data(self):
        """Extract and store data from __raw.
        """

        garbage, report = self.__raw.split(BANNER,1)
        items, result = report.rsplit(BREAK2,1)
        details = items.split(BREAK1)[1:]


        # Totals
        # ======

        m = ALL_RE.search(result)
        try:
            all = m.group(1)
        except:
            logger.debug(self.__raw)
            raise
        fail = err = '0'
        if 'FAILED' in result:
            m = FAIL_RE.search(result)
            if m is not None:
                fail = str(m.group(1))
            m = ERR_RE.search(result)
            if m is not None:
                err = str(m.group(1))
        pass5 = '0'
        if all != '0':
            pass5 = int(100 * (int(all) - int(fail) - int(err)) / float(all))
        pass5 = str(pass5) + '%'
        totals = (pass5, fail, err, all)


        # Data
        # ====

        data = {}
        for detail in details:
            flop, name, module, break2, traceback_ = detail.split(None, 4)
            if flop == 'FAIL:':
                flop = 'failure'
            elif flop == 'ERROR:':
                flop = 'error'
            name = '.'.join((module[1:-1], name))[len(self.module)+1:]
            traceback_ = traceback_.strip()
            data[name] = [flop, traceback_]


        # Update self.
        # ============

        self.totals = totals
        self.data = data
        self.names = sorted(data)
        del self.__raw
