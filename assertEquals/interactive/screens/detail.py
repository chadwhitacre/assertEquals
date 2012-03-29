import Queue
import curses
import logging
import traceback
from curses import ascii

from assertEquals.interactive.detail import Detail
from assertEquals.interactive.utils import Spinner, ScrollArea, format_tb
from assertEquals.interactive.screens.base import BaseScreen
from assertEquals.interactive.screens.error import ErrorScreen


logger = logging.getLogger('assertEquals.screens.detail')

TESTS = 'tests'
RESULT = 'result'


class DetailScreen(BaseScreen):
    """Represent a detail report for a specific module.

        F5/space -- rerun the tests for this module


    """

    banner = " assertEquals " # shows up at the top
    bottomrows = 3  # the number of boilerplate rows at the bottom
    toprows = 3     # the number of boilerplate rows at the top of the screen
    focus = TESTS   # the currently selected ScrollArea: tests/result
    tests = None    # the left ScrollArea
    result = None   # the right ScrollArea
    detail = None   # a Detail instance
    curresult = ()  # list of lines in the currently displayed result text
    selected = ''   # the name of the currently selected test


    def __init__(self, summary):
        """Takes a dotted module name.
        """
        self.summary = summary
        self.win = summary.win
        self.base = summary.selected
        self.colors = summary.colors
        self.blocks = summary.blocks
        self.spinner = Spinner(self.spin)
        self.detail = Detail(self.base)
        self.refresh()


    # BaseScreen contracts
    # ====================

    ui_chars = ( ord('q')
               , ord(' ')
               , curses.KEY_F5
               , curses.KEY_BACKSPACE
               , curses.KEY_ENTER
               , curses.KEY_UP
               , curses.KEY_DOWN
               , curses.KEY_LEFT
               , curses.KEY_RIGHT
               , curses.KEY_PPAGE
               , curses.KEY_NPAGE
               , curses.KEY_HOME
               , curses.KEY_END
               , ascii.BS
               , ascii.TAB
               , ascii.LF
               , ascii.ESC
                )

    def init(self):
        if self.detail.names:
            self.selected = self.detail.names[0]
        self.populate()
        self.draw_content()

    def resize(self):
        c1h = c2h = self.H - self.toprows - self.bottomrows
        c1w = (self.W/2) - 5
        c2w = self.W - c1w - 5 - 3
        self.c1 = (c1h, c1w)
        self.c2 = (c2h, c2w)
        self.draw_frame()
        if self.inited:
            self.populate()
            self.draw_content()

    def react(self, c):

        # Commands that do work
        # =====================

        if c in ( ord('q')                      # back to summary
                , curses.KEY_BACKSPACE
                , ascii.ESC
                , ascii.BS
                , curses.KEY_LEFT):
            return self.summary

        elif c in ( curses.KEY_ENTER            # forward to traceback
                  , ascii.LF
                  , curses.KEY_RIGHT
                   ):
            if self.selected == '':
                return StandardError("No test selected.")
            else:
                traceback_ = self.detail.data[self.selected][1]
                return ErrorScreen(self, traceback_)

        elif c in (ord(' '), curses.KEY_F5):    # stay put and refresh
            self.spinner(self.refresh)
            if self.detail.totals[0] == '100%': # all tests passed!
                return self.summary
            if self.selected not in self.detail.names:
                self.selected = self.detail.names[0]
            self.populate()


        # Focus/paging commands
        # =====================

        elif c == ascii.TAB:
            self.focus = (self.focus == RESULT) and TESTS or RESULT

        elif self.focus == TESTS:
            if c == curses.KEY_UP:      # up
                self.tests.scroll(-1)
            elif c == curses.KEY_DOWN:  # down
                self.tests.scroll(1)
            elif c == curses.KEY_PPAGE: # page up
                self.tests.page_up()
            elif c == curses.KEY_NPAGE: # page down
                self.tests.page_down()
            elif c == curses.KEY_HOME:  # home
                self.tests.home()
            elif c == curses.KEY_END:   # down
                self.tests.end()
        else:
            if c == curses.KEY_UP:      # up
                self.result.move_cursor(0)
                self.result.scroll(-1)
            elif c == curses.KEY_DOWN:  # down
                self.result.move_cursor(self.result.numrows-1)
                self.result.scroll(1)
            elif c == curses.KEY_PPAGE: # page up
                self.result.page_up()
            elif c == curses.KEY_NPAGE: # page down
                self.result.page_down()

        self.draw_content()


    # Helpers
    # =======

    def spin(self):
        """Put a 'working' indicator in the banner.

        This is called by our Spinner instance.

        """
        l = (self.W - len(self.banner)) / 2
        stop = False
        while not stop:
            for i in range(4):
                spun = "  working%s  " % ('.'*i).ljust(3)
                self.win.addstr(0,l,spun,self.colors.BLUE)
                self.win.refresh()
                try:
                    stop = self.spinner.flag.get(timeout=0.25)
                except Queue.Empty:
                    pass
        self.draw_banner()

    def populate(self):
        """[Re]create both ScrollAreas.

        In order to retain the current page and selection, we only recreate
        the tests pane if the parameters of this area have changed.

        """

        args = { 'numrows': self.c1[0]+1
               , 'numitems':len(self.detail)
               , 'toprow': self.toprows
                }

        if not self.tests:
            self.tests = ScrollArea(**args)
        else:
            for k,v in args.items():
                if getattr(self.tests, k) != v:
                    self.tests = ScrollArea(**args)
                    break

        self.populate_result()

    def populate_result(self):
        """[Re]create just the result ScrollArea.
        """
        if self.selected == '':
            curresult = ()
        else:
            traceback_ = self.detail.data[self.selected][1]
            self.curresult = format_tb(self.c2[1], traceback_)
        self.result = ScrollArea( self.c1[0]+1
                                , len(self.curresult)
                                , self.toprows
                                 )

    def refresh(self):
        """Refresh our results and update the summary too.
        """
        self.detail.refresh()
        if not self.selected:
            if self.detail.names:
                self.selected = self.detail.names[0]
        self.summary.summary.update(self.base, *self.detail.totals)


    # Writers
    # =======

    def draw_banner(self):
        l = (self.W - len(self.banner)) / 2
        self.win.addstr(0,l,self.banner,self.colors.BLUE_DIM)


    def draw_frame(self):
        """Draw the screen.
        """

        H, W = self.H, self.W
        c1h, c1w = self.c1
        c2h, c2w = self.c2


        # Background and border
        # =====================

        color = self.colors.WHITE

        self.win.bkgd(' ')
        self.win.border() # not sure how to make this A_BOLD
        self.win.addch(0,0,curses.ACS_ULCORNER,color)
        self.win.addch(0,W,curses.ACS_URCORNER,color)
        self.win.addch(H,0,curses.ACS_LLCORNER,color)
        #self.win.addch(H,W,curses.ACS_LRCORNER,color) error! why?
        for i in range(1,W):
            self.win.addch(0,i,curses.ACS_HLINE,color)
            self.win.addch(H,i,curses.ACS_HLINE,color)
        for i in range(1,H):
            self.win.addch(i,0,curses.ACS_VLINE,color)
            self.win.addch(i,W,curses.ACS_VLINE,color)

        # headers bottom border
        self.win.addch(2,0,curses.ACS_LTEE,color)
        for i in range(0,W-1):
            self.win.addch(2,i+1,curses.ACS_HLINE,color)
        self.win.addch(2,W,curses.ACS_RTEE,color)

        # footer top border
        self.win.addch(H-2,0,curses.ACS_LTEE,color)
        for i in range(0,W-1):
            self.win.addch(H-2,i+1,curses.ACS_HLINE,color)
        self.win.addch(H-2,W,curses.ACS_RTEE,color)

        # column border
        bw = c1w+5
        self.win.vline(3,bw,curses.ACS_VLINE,H-5,color)
        self.win.addch(2,bw,curses.ACS_TTEE,color)
        self.win.addch(H-2,bw,curses.ACS_BTEE,color)


        # Banner text and column headers
        # ==============================

        l = (W - len(self.banner)) / 2
        r = l + len(self.banner)
        self.win.addch(0,l-2,curses.ACS_LARROW,color)
        self.win.addch(0,l-1,curses.ACS_VLINE,color)
        self.draw_banner()
        self.win.addch(0,r,curses.ACS_VLINE,color)
        self.win.addch(0,r+1,curses.ACS_RARROW,color)


        # Commit our changes.
        # ===================

        self.win.refresh()


    def draw_content(self):
        """Erase the current listing and redraw.
        """

        W = self.W
        c1h, c1w = self.c1
        c2h, c2w = self.c2


        # Clear both panes and draw scrollbar(s).
        # =======================================

        if self.focus == TESTS:
            tests_scrollbg_color = self.colors.BLUE
            tests_scrollbar_color = self.blocks.BLUE
            result_scrollbg_color = self.colors.GRAY
            result_scrollbar_color = self.blocks.GRAY
        else:
            tests_scrollbg_color = self.colors.GRAY
            tests_scrollbar_color = self.blocks.GRAY
            result_scrollbg_color = self.colors.BLUE
            result_scrollbar_color = self.blocks.BLUE

        bg = curses.ACS_CKBOARD

        for i in range(self.toprows, self.toprows+self.c1[0]+1):
            self.win.addstr(i,1,' '*(c1w+4))
            self.win.addstr(i,c1w+6,' '*(c2w+2))

            if self.tests.bar is None:
                self.win.addch(i,0,curses.ACS_VLINE,self.colors.WHITE)
            elif i in self.tests.bar:
                self.win.addstr(i,0,' ',tests_scrollbar_color)
            else:
                self.win.addch(i,0,bg,tests_scrollbg_color)

            if self.result.bar is None:
                self.win.addch(i,W,curses.ACS_VLINE,self.colors.WHITE)
            elif i in self.result.bar:
                self.win.addstr(i,W,' ',result_scrollbar_color)
            else:
                self.win.addch(i,W,bg,result_scrollbg_color)


        # tests
        # =====

        if self.tests.numitems != 0:
            for index, rownum  in self.tests:
                self.draw_row(index, rownum)
            selected = ''
            if self.focus == TESTS:
                self.selected = self.detail.names[self.tests.curitem]
                self.populate_result()


        # result
        # ======

        color = self.colors.GRAY
        if self.focus == RESULT:
            color = self.colors.WHITE
        for index, rownum in self.result:
            self.win.addstr(rownum,c1w+7,self.curresult[index],color)


        # Totals
        # ======

        pass5, fail, err, all = self.detail.totals

        color = self.colors.RED
        if pass5 == '100%':
            color = self.colors.GREEN

        if len(fail) > 4:
            fail = '9999'
        if len(err) > 4:
            err = '9999'
        if len(all) > 4:
            all = '9999'

        h = self.H-1
        w = self.W-21
        self.win.addstr(h,w,pass5.rjust(4),color)
        self.win.addstr(h,w+5,fail.rjust(4),color)
        self.win.addstr(h,w+10,err.rjust(4),color)
        self.win.addstr(h,w+15,all.rjust(4),color)

        base = self.base
        w = w-4
        if len(base) > w:
            base = base[:w-3] + '...'
        base = base.ljust(w)
        self.win.addstr(self.H-1,3,base,color)


        # Commit changes.
        # ===============

        self.win.refresh()


    def draw_row(self, index, rownum):
        """Given two ints, write a row to the screen.

        The first int is the index into self.names. The second is the number of
        the row on the screen to write to. Both are 0-indexed.

        """

        c1h, c1w = self.c1
        c2h, c2w = self.c2

        name, flub, result = self.detail[index]


        # Determine highlighting for this row.
        # ====================================

        if self.focus == RESULT:
            bullet_color = self.colors.GRAY
            if flub == 'error':
                color = self.colors.YELLOW_DIM
            elif flub == 'failure':
                color = self.colors.RED_DIM
            else:
                color = self.colors.WHITE_DIM
        else:
            bullet_color = self.colors.BLUE
            if flub == 'error':
                color = self.colors.YELLOW
            elif flub == 'failure':
                color = self.colors.RED
            else:
                color = self.colors.WHITE


        # Test name and bullets
        # =====================

        if len(name) > c1w:
            name = name[:c1w-3] + '...'
        name = name.ljust(c1w)
        self.win.addstr(rownum,3,name,color)

        l = ' '
        r = ' '
        if index == self.tests.curitem:
            l = curses.ACS_RARROW
            r = curses.ACS_LARROW
        self.win.addch(rownum,1,l,bullet_color)
        self.win.addch(rownum,c1w+4,r,bullet_color)

