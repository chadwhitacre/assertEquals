import curses
import logging
import traceback

from assertEquals.interactive.utils import ScrollArea
from assertEquals.interactive.screens.base import BaseScreen


logger = logging.getLogger('assertEquals.screens.debugging')


class DebuggingScreen(BaseScreen):
    """Interacts with Pdb in a child process.
    """

    console_mode = True

    def __init__(self, screen, proc):
        """Takes the screen where the error occured and a Process object.
        """
        self.screen = screen
        self.colors = screen.colors
        self.blocks = screen.blocks
        self.proc = proc
        self.win = self.screen.win

        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        self.win.idlok(1)
        self.win.scrollok(1)


    # BaseScreen contracts
    # ====================

    def init(self):
        self.win.addstr(0,0,self.proc.intro)
        self.win.refresh()

    def resize(self):
        pass

    def react(self, s):
        """Given an input string, proxy it to the child process.
        """
        if not self.proc.stdin.closed:
            output = self.proc.communicate(s)
        if self.proc.poll() is None:    # not done yet, write to screen
            self.win.addstr(output)
            self.win.refresh()
        else:                           # all done, exit cleanly
            curses.cbreak()
            curses.noecho()
            curses.curs_set(0)
            self.win.idlok(0)
            self.win.scrollok(0)
            return self.screen
