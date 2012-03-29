import Queue
import curses
import logging
import subprocess
import textwrap
import threading
import traceback
from curses import ascii

logger = logging.getLogger('assertEquals.interactive.utils')


class Bucket:
    """
    """


class RefreshError(StandardError):
    """An error refreshing the summary.
    """
    def __init__(self, traceback):
        """Save the remote traceback.
        """
        StandardError.__init__(self)
        self.traceback = traceback


class CommunicationProblem(StandardError):
    """Wrap a Process that wants to talk.
    """
    def __init__(self, proc):
        StandardError.__init__(self)
        self.proc = proc


class Process(subprocess.Popen):
    """Represent a child process that might want to interact with us.
    """

    prompt = '(Pdb) ' # The signal that it wants to talk.
    intro = '' # If it wants to talk, this will be the first thing it said.
    interactive = False # whether or not we are interacting with the child

    def __init__(self, *args, **kwargs):
        """Extend to capture I/O streams.
        """
        _kwargs = { 'stdin':subprocess.PIPE
                  , 'stdout':subprocess.PIPE
                  , 'stderr':subprocess.STDOUT
                   }
        kwargs.update(_kwargs)
        subprocess.Popen.__init__(self, *args, **kwargs)


    def __str__(self):
        return "<Process #%d>" % self.pid
    __repr__ = __str__


    def communicate(self, input=None):
        """Override to support Pdb interaction.

        If input is None, then we will raise ourselves if the process wants to
        interact. Otherwise, we will return the last thing it said. To see if
        the conversation is over, use self.poll().

        """

        if input is not None:
            self.stdin.write(input + '\n')

        output = []
        i = len(self.prompt)

        while 1:
            retcode = self.poll()
            if retcode is None:
                # Conversation not done; check to see if it's our turn to talk.
                if len(output) >= i:
                    latest = ''.join(output[-i:])
                    if latest == self.prompt:
                        self.interactive = True
                        break
                output.append(self.stdout.read(1))
            else:
                # The process is done; assume we can read to EOF.
                output.append(self.stdout.read())
                break

        output = ''.join(output)
        if self.interactive and (input is None):
            self.intro = output
            raise CommunicationProblem(self)
        else:
            return output


class Spinner:
    """Represent a random work indicator, handled in a separate thread.
    """

    def __init__(self, spin):
        """Takes a callable that actually draws/undraws the spinner.
        """
        self.spin = spin
        self.flag = Queue.Queue(1)

    def start(self):
        """Show a spinner.
        """
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        """Stop the spinner.
        """
        self.flag.put(True)
        self.thread.join()

    def __call__(self, call, *args, **kwargs):
        """Convenient way to run a routine with a spinner.
        """
        self.start()
        try:
            return call(*args, **kwargs)
        finally:
            self.stop()




class DoneScrolling(StandardError):
    """Represents the edge of a scrolling area.
    """


class ScrollArea:
    """Represents a scrollable portion of a screen.
    """

    numrows = 0         # number of viewable rows; len semantics
    cursor = 0          # index of the currently curitem row; 0-indexed
    toprow = 0          # index of our top row within the window; 0-indexed

    numitems = 0        # the total number of items in the list; len semantics
    curitem = 0         # index of the currently curitem item; 0-indexed
    start = end_ = 0    # coordinates in your list of items; slice semantics
    bar = None          # a range() within range(numrows) for which a scrollbar
                        #   should be drawn

    def __init__(self, numrows, numitems, toprow):
        """
        """
        self.numrows = numrows
        self.numitems = numitems
        self.toprow = toprow
        if self.numitems < self.numrows:
            self.end_ = self.numitems
        else:
            self.end_ = self.numrows
        self.update()

    def __repr__(self):
        return "<ScrollArea %s>" % str(self.stat())
    __str__ = __repr__


    # Container emulation
    # ===================
    # As a container, we are a list of 2-tuples: (index, rownum)
    #   index -- an index of an item currently being displayed
    #   rownum -- a row number relative to the current window object

    def __list(self):
        def rownum(i):
            return self.toprow + i - self.start
        return [(i, rownum(i)) for i in range(self.start, self.end_)]

    def __iter__(self):
        return iter(self.__list())

    def __len__(self):
        return len(self.__list())


    # Basic API
    # =========

    def scroll_one(self, up=False):
        """Scroll the viewport by one row.
        """

        if self.numitems == 0: # short-circuit
            raise DoneScrolling

        if up: # scroll up
            if self.cursor == 0: # top of viewport
                if self.start == 0: # top of list
                    raise DoneScrolling
                else: # not top of list
                    self.start -= 1
                    if self.end_ - self.start > self.numrows:
                        self.end_ -= 1
            else: # not top of viewport
                self.cursor -= 1

        else: # scroll down
            if self.curitem + 1 == self.numitems: # bottom of list
                raise DoneScrolling
            else: # not bottom of list
                if self.cursor + 1 == self.numrows: # bottom of viewport
                    self.start += 1
                    self.end_ += 1
                else: # not bottom of viewport
                    self.cursor += 1

        self.update()


    def scroll(self, delta):
        """Support multi-line scrolling.
        """
        up = delta < 0
        delta = abs(delta)
        try:
            for i in range(delta):
                self.scroll_one(up)
        except DoneScrolling:
            self._refuse()


    # Extended API
    # ============

    def page_up(self):
        """Scroll up one page.
        """
        if self.numitems == 0:              # empty page
            self._refuse()
        elif self.numitems <= self.numrows: # partial/single page
            self.cursor = 0
            self._refuse()
        elif self.numitems > self.numrows:  # multiple pages

            # already at top
            if self.curitem == 0:
                self.cursor = 0
                self._refuse()

            # less than a full page above
            elif self.start+1 - self.numrows < 0:
                self.start = 0
                self.end_ = self.numrows
                self.cursor = 0
                self._refuse()

            # exactly one page above
            elif self.start+1 - self.numrows == 0:
                self.start = 0
                self.end_ = self.numrows
                self.cursor = 0

            # more than one page above
            else:
                self.start -= self.numrows
                self.end_ = self.start + self.numrows

        self.update()


    def page_down(self):
        """
        """
        if self.numitems == 0:              # empty page
            self._refuse()
        elif self.numitems <= self.numrows: # partial/single page
            self.cursor = self.numitems - 1
            self._refuse()
        elif self.numitems > self.numrows:  # multiple pages

            #if hasattr(self, 'flag'):
            #    import pdb; pdb.set_trace()

            # already on the last page (exact or partial)
            if self.numitems - self.start <= self.numrows:
                self.start = self.numitems - 1
                self.end_ = self.numitems
                self.cursor = 0
                self._refuse()

            # less than a full page left
            elif self.numitems - self.end_ < self.numrows:
                self.start = self.end_
                self.end_ = self.numitems
                rows_displayed = self.end_ - self.start
                if self.cursor > rows_displayed:
                    self.cursor = rows_displayed - 1

            # one full page or more left
            else:
                self.start += self.numrows
                self.end_ += self.numrows

        self.update()


    def home(self):
        """
        """
        if self.numitems == 0:              # empty page
            self._refuse()
        elif self.numitems <= self.numrows: # partial/single page
            if self.cursor == 0:
                self._refuse()
            else:
                self.cursor = 0
        elif self.numitems > self.numrows:  # multiple pages
            self.start = 0
            self.end_ = self.start + self.numrows
            self.cursor = 0
            if self.curitem == 0:
                self._refuse()
        self.update()


    def end(self):
        """
        """
        if self.numitems == 0:              # empty page
            self._refuse()
        elif self.numitems <= self.numrows: # partial/single page
            if self.cursor == self.numitems - 1:
                self._refuse()
            else:
                self.cursor = self.numitems - 1
        elif self.numitems > self.numrows:  # multiple pages
            self.cursor = self.numrows - 1
            self.end_ = self.numitems
            self.start = self.end_ - self.numrows
            if self.curitem == self.numitems - 1:
                self._refuse()
        self.update()


    # Helpers
    # =======

    def _refuse(self):
        """Factored out for easier testing.
        """
        self.update()
        self.refuse()

    def refuse(self):
        """Factored out for easier testing.
        """
        curses.beep()

    def update(self):
        """Update self.bar and self.curitem.
        """
        if self.numrows > self.numitems:
            bar = None
        else:
            numitems_f = float(self.numitems)
            size = int((self.numrows/numitems_f) * self.numrows)
            start = int((self.start/numitems_f) * self.numrows)
            end = start + size + 1
            if end > self.numrows:
                end = self.numrows
            bar = range(start+self.toprow, end+self.toprow)
        self.bar = bar
        self.curitem = self.start + self.cursor

    def stat(self):
        return ( self.numrows   # 1-indexed
               , self.cursor    # 0-indexed
               , self.numitems  # 1-indexed
               , self.start     # 0-indexed
               , self.end_      # 0-indexed
               , self.curitem   # 0-indexed
               , self.bar       # 0-indexed
                )

    def move_cursor(self, rownum):
        """Move the cursor to a specific row, selecting the item there.
        """
        if (self.numrows < self.numitems) and (rownum in range(self.numrows)):
            self.cursor = rownum
            if rownum not in [i[1] for i in self]:
                self._refuse()
            else:
                self.update()
        else:
            self._refuse()


wrapper_1 = textwrap.TextWrapper( initial_indent=''
                                , subsequent_indent=''
                                , break_long_words=True
                                 )
wrapper_2 = textwrap.TextWrapper( initial_indent='  '
                                , subsequent_indent='    '
                                , break_long_words=True
                                 )

def format_tb(width, traceback_):
    """Given a traceback, return a list of strings.

    I would like to format tracebacks differently, but that will have to
    wait for another day.

    """
    wrapper_1.width = wrapper_2.width = width
    raw = traceback_.splitlines()
    lines = wrapper_1.wrap(raw[0])
    lines.append('')
    for line in raw[1:-1]:
        line = line.strip()
        lines.extend(wrapper_2.wrap(line))
        if not line.startswith('File'):
            lines.append('')
    lines.extend(wrapper_1.wrap(raw[-1]))
    return lines
