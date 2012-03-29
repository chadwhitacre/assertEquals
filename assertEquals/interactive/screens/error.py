import curses
import logging
import traceback
from curses import ascii

from assertEquals.interactive.utils import ScrollArea, format_tb
from assertEquals.interactive.screens.base import BaseScreen


logger = logging.getLogger('assertEquals.screens.error')


class ErrorScreen(BaseScreen):
    """Display a traceback within curses.
    """

    def __init__(self, screen, traceback_):
        """Takes the screen where the error occured and the traceback.
        """
        self.screen = screen
        self.colors = screen.colors
        self.blocks = screen.blocks
        self.traceback_ = traceback_
        self.win = self.screen.win
        self.win.clear()
        self.win.refresh()


    # BaseScreen contracts
    # ====================

    ui_chars = ( ord('q')
               , curses.KEY_UP
               , curses.KEY_DOWN
               , curses.KEY_LEFT
               , curses.KEY_PPAGE
               , curses.KEY_NPAGE
               , curses.KEY_BACKSPACE
                )

    def resize(self):
        try:
            self.lines = format_tb(self.W-1, self.traceback_)
            self.area = ScrollArea(self.H, len(self.lines), 0)
            self.draw()
        except:
            logger.critical(traceback.format_exc())

    def react(self, c):
        try:
            if c in ( ord('q')
                    , curses.KEY_BACKSPACE
                    , ascii.BS
                    , ascii.ESC
                    , curses.KEY_LEFT
                     ):
                return self.screen
            elif c == curses.KEY_UP:    # up
                self.area.move_cursor(0)
                self.area.scroll(-1)
            elif c == curses.KEY_DOWN:  # down
                self.area.move_cursor(self.area.numrows-1)
                self.area.scroll(1)
            elif c == curses.KEY_PPAGE: # page up
                self.area.page_up()
            elif c == curses.KEY_NPAGE: # page down
                self.area.page_down()
            self.draw()
        except:
            logger.critical(traceback.format_exc())


    # Writes
    # ======

    def draw(self):

        # Clear the screen and then draw our rows.
        # ========================================

        self.win.clear()
        self.win.refresh()
        for index, rownum in self.area:
            self.win.addstr(rownum,0,self.lines[index])


        # Continuation indicators
        # =======================

        color = self.colors.BLUE

        if self.area.start > 0:
            c = curses.ACS_UARROW
        else:
            c = ord(' ')
        self.win.addch(0,self.W,c,color)

        if self.area.end_ < self.area.numitems:
            c = curses.ACS_LANTERN
        else:
            c = ord(' ')
        self.win.addch(self.H-1,self.W,c,color)


        # Commit
        # ======

        self.win.refresh()
