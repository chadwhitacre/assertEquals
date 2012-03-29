"""Main function a la Guido:

    http://www.artima.com/weblogs/viewpost.jsp?thread=4829

"""
import getopt
import sys

from assertEquals.cli.reporters import detail, summarize


WINDOWS = sys.platform.find('win') == 0


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            short = "fst:x:"
            long_ = [ "find-only"
                    , "scripted"
                    , "testcase=","TestCase="
                    , "stopwords="
                     ]
            opts, args = getopt.getopt(argv[1:], short, long_)
        except getopt.error, msg:
            raise Usage(msg)

        find_only = False   # -f
        scripted = False    # -s
        stopwords = []      # -x
        testcase = None     # -t

        for opt, value in opts:
            if opt in ('-f', '--find-only'):
                find_only = True
            elif opt in ('-s', '--scripted'):
                scripted = True
            elif opt in ('-x', '--stopwords'):
                stopwords = value.split(',')
            elif opt in ('-t', '--testcase', '--TestCase'):
                testcase = value

        if len(args) == 1:
            module = args[0]
        else:
            raise Usage("Please specify a module.")

        if WINDOWS or scripted:
            if testcase is None:
                report = summarize(module, find_only, stopwords)
            else:
                report = detail(module, testcase)
            sys.stdout.write(report)
            
            tfail, terr, tall = summarize._Summarize__totals
            if tfail > 0 or terr > 0: return 2 # non-zero exit-code on errors
            else: return 0
        else:
            from assertEquals.interactive import CursesInterface
            CursesInterface(module, stopwords)

    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "'man 1 assertEquals' for instructions."
        return 2
