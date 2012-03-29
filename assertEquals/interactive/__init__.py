"""Interactive interface.
"""
import curses
import os

from assertEquals.interactive.screens.summary import SummaryScreen
from assertEquals.interactive.screens.detail import DetailScreen
from assertEquals.interactive.utils import Bucket


class CursesInterface:

    def __init__(self, module, stopwords):
        self.module = module
        self.stopwords = stopwords
        curses.wrapper(self.wrapme)
        os.system('clear')

    def wrapme(self, win):
        self.win = win
        curses.curs_set(0) # Don't show the cursor.

        # colors -- a bit wacky to have it here, I know
        bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_WHITE, bg)
        curses.init_pair(2, curses.COLOR_RED, bg)
        curses.init_pair(3, curses.COLOR_GREEN, bg)
        curses.init_pair(4, curses.COLOR_CYAN, bg)
        curses.init_pair(5, curses.COLOR_YELLOW, bg)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_CYAN)

        self.colors = Bucket()
        self.colors.WHITE = curses.color_pair(1)|curses.A_BOLD
        self.colors.GRAY = curses.color_pair(1)|curses.A_DIM
        self.colors.RED = curses.color_pair(2)|curses.A_BOLD
        self.colors.RED_DIM = curses.color_pair(2)|curses.A_DIM
        self.colors.GREEN = curses.color_pair(3)|curses.A_BOLD
        self.colors.GREEN_DIM = curses.color_pair(3)|curses.A_DIM
        self.colors.BLUE = curses.color_pair(4)|curses.A_BOLD
        self.colors.BLUE_DIM = curses.color_pair(4)|curses.A_DIM
        self.colors.YELLOW = curses.color_pair(5)|curses.A_BOLD
        self.colors.YELLOW_DIM = curses.color_pair(5)|curses.A_DIM

        self.blocks = Bucket()
        self.blocks.WHITE = curses.color_pair(6)|curses.A_BOLD
        self.blocks.GRAY = curses.color_pair(6)|curses.A_DIM
        self.blocks.BLUE = curses.color_pair(7)|curses.A_BOLD

        screen = SummaryScreen(self)
        try:
            while 1:
                # Each screen returns the next screen.
                # screens are responsible for their own error handling so that
                # they can return themselves and we can therefore get back to
                # them.
                screen = screen.go()
        except KeyboardInterrupt:
            pass
