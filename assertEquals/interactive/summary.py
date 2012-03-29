import logging
import os
import subprocess
import sys

from assertEquals.cli.utils import BANNER, BORDER, HEADERS
from assertEquals.interactive.utils import RefreshError, Process


logger = logging.getLogger('assertEquals.interactive.summary')


class Summary:
    """Represent the data from an inter-process summarize() call.

    This is designed to be a persistent object. Repeated calls to refresh will
    update the dataset. On partial updates, existing data will be marked as
    stale. There is also a show flag for each record; only items for which this
    are true are included in the name index and __len__ calls.

    """

    module = ''     # the current module dotted module name
    data = None     # a dictionary, {name:(stats, fresh)}:
                    #   stats: None or (pass5, fail, err, all)
                    #   fresh: None or False or True
    names = None    # a sorted list of names for which show is True
    run = True      # the current state of the run flag
    totals = ()     # a single 4-tuple per summarize()
    __lines = None  # for communication between _set_totals and _set_data
    __raw = ''      # for communication between _call and _set_data


    def __init__(self, stopwords=()):
        """Takes a sequence.
        """
        self.stopwords = stopwords
        self.data = {}
        self.totals = ()
        self.names = []


    # Container emulation
    # ===================

    def __getitem__(self, i):
        """Takes an int index into self.names
        """
        name = self.names[i]
        return [name] + self.data[name]

    def __len__(self):
        """Only count items for which show is True.
        """
        return len(self.names)

    def __iter__(self):
        return self.names.__iter__()
    iterkeys = __iter__


    # Main callable
    # =============

    def refresh(self, module, find_only=True):
        """Update our information.
        """
        self.module = module
        self.find_only = find_only

        self._call()

        self._set_stale()
        self._set_totals()
        self._set_data()


    def update(self, name, pass5, fail, err, all):
        """Given data on one testcase, update its info.

        This is called from DetailScreen.

        """
        if name not in self.data:
            raise StandardError("Running detail for module not in " +
                                "summary: %s." % name)
        self._set_stale()
        self.data[name] = [(pass5, fail, err, all), True]
        self.totals = [pass5, fail, err, all]


    # Helpers
    # =======

    def _call(self):
        """Invoke a child process and return its output.

        We hand on our environment and any sys.path manipulations to the child,
        and we capture stderr as well as stdout so we can handle errors.

        """
        args = [ sys.executable
               , '-u' # unbuffered, so we can interact with it
               , sys.argv[0]
               , '--stopwords=%s' % ','.join(self.stopwords)
               , '--scripted'
               , self.module
                ]
        if self.find_only:
            args.insert(4, '--find-only')

        environ = os.environ.copy()
        environ['PYTHONPATH'] = ':'.join(sys.path)

        proc = Process(args=args, env=environ)

        raw = proc.communicate()
        if BANNER not in raw:
            raise RefreshError(raw)
        self.__raw = raw


    def _set_stale(self):
        """Mark currently fresh data as stale.
        """
        for name, datum in self.data.iteritems():
            if datum[1] is True:
                datum[1] = False


    def _set_totals(self):
        """Given self.__raw, set totals and __lines on self.
        """
        lines = self.__raw.splitlines()
        self.totals = tuple(lines[-1].split()[1:])
        del lines[-1]
        self.__lines = lines


    def _set_data(self):
        """Extract and store data from __lines.
        """

        data = {}
        reading_report = False # ignore any output that precedes our report

        for line in self.__lines:

            # Decide if we want this line, and if so, split it on spaces.
            # ===========================================================

            line = line.strip('\n')
            if line == BANNER:
                reading_report = True
                continue
            if (not reading_report) or (not line) or line in (HEADERS, BORDER):
                continue
            tokens = line.split()


            # Convert the row to our record format.
            # =====================================
            # The raw report lists TestCases by full dotted name, but we want to
            # only show short names, and indent under a module tree. So we add
            # all parent modules to data, and set their value to (None, None)

            name = tokens[0]
            stats = tuple(tokens[1:])

            module_dotted, testcase = name.rsplit('.',1)

            parts = module_dotted.split('.')
            for i in range(len(parts),self.module.count('.'),-1):
                ancestor = '.'.join(parts[:i])
                data[ancestor] = [None, None]

            fresh = None
            if '-' not in stats:
                fresh = True

            data[name] = [stats, fresh]

        self.data.update(data)
        self.names = sorted(self.data.keys())
        del self.__lines

