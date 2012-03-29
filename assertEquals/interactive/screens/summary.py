import Queue
import curses
import logging
import traceback
from curses import ascii

from assertEquals.interactive.summary import Summary
from assertEquals.interactive.utils import ScrollArea, Spinner
from assertEquals.interactive.screens.base import BaseScreen
from assertEquals.interactive.screens.detail import DetailScreen
from assertEquals.interactive.screens.error import ErrorScreen


logger = logging.getLogger('assertEquals.screens.summary')


class SummaryScreen(BaseScreen):
    """Represents the main module listing.

    UI-driven events:

        <ctrl>-F5 -- refresh list of modules, resetting tests to un-run
        F5/enter/space -- run selected tests, possibly going to results screen

    """

    banner = " assertEquals " # shows up at the top
    bottomrows = 3          # the number of boilerplate rows at the bottom
    listing = None          # a ScrollArea
    selected = ''           # the dotted name of the currently selected item
    summary = {}            # a data dictionary per summarize()
    toprows = 3             # the number of boilerplate rows at the top
    win = None              # a curses window


    def __init__(self, iface):
        """Takes a CursesInterface object.
        """
        self.win = iface.win
        self.module = iface.module
        self.colors = iface.colors
        self.blocks = iface.blocks
        self.stopwords = iface.stopwords
        self.spinner = Spinner(self.spin)
        self.summary = Summary(self.stopwords)


    # BaseScreen contracts
    # ====================

    ui_chars = ( ord('q')
               , ord(' ')
               , curses.KEY_F5
               , curses.KEY_ENTER
               , curses.KEY_UP
               , curses.KEY_DOWN
               , curses.KEY_RIGHT
               , curses.KEY_NPAGE
               , curses.KEY_PPAGE
               , curses.KEY_HOME
               , curses.KEY_END
               , ascii.LF
               , ascii.FF
                )

    def init(self):
        self.spinner(self.summary.refresh, self.module)
        self.update_selection()
        self.populate()
        self.draw_content()

    def resize(self):
        c1h = c2h = self.H - self.toprows - self.bottomrows
        c2w = 20
        c1w = self.W - c2w - 7
        self.c1 = (c1h, c1w)
        self.c2 = (c2h, c2w)
        self.draw_frame()
        if self.inited:
            self.populate()
            self.draw_content()

    def react(self, c):

        if c == ord('q'):
            raise KeyboardInterrupt
        elif c == ord('h'):
            return # return HelpScreen(self)


        # NB: page_up() and page_down() are switched because of observed
        # behavior. I don't know if this is a quirk of my terminal or
        # an error in ScrollArea or what. Also, I haven't observed the
        # home() and down() functions in action. Again, probably a
        # terminal quirk. UPDATE: Actually, I think it might be an error
        # in the curses docs? Or is this nomenclature just Unix lore?

        if c == curses.KEY_UP:          # up
            self.listing.scroll(-1)
        elif c == curses.KEY_DOWN:      # down
            self.listing.scroll(1)
        elif c == curses.KEY_PPAGE:     # page up
            self.listing.page_up()
        elif c == curses.KEY_NPAGE:     # page down
            self.listing.page_down()
        elif c == curses.KEY_HOME:      # home
            self.listing.home()
        elif c == curses.KEY_END:       # end
            self.listing.end()


        # Actions that do work
        # ====================

        elif c == ascii.FF:             # refresh our TestCase list
            self.reload()
        elif c in ( ord(' ')            # run tests!
                  , ascii.LF
                  , curses.KEY_ENTER
                  , curses.KEY_RIGHT
                  , curses.KEY_F5
                   ):

            # Update the summary if we are on a module/package, or go to a
            # DetailScreen if we are on a TestCase and not all tests pass.

            if self.selected:
                isTestCase = self.summary.data[self.selected][0]
                if isTestCase:          # TestCase
                    detailscreen = self.spinner(DetailScreen, self)
                    if c != ord(' '):
                        if detailscreen.detail.totals[0] != '100%':
                            return detailscreen
                else:                   # module/package
                    self.spinner( self.summary.refresh
                                , self.selected
                                , find_only=False
                                 )
                    self.update_selection()

            else:
                raise StandardError("No module selected.")


        self.draw_content()


    # Helpers
    # =======

    def reload(self):
        self.summary = Summary(self.stopwords)
        self.spinner(self.summary.refresh, self.module)
        self.update_selection()

    def populate(self):
        """[Re]create the scroll area if needed.

        In order to retain the current page and selection, we only recreate the
        pane if its size parameters have changed.

        """

        args = { 'numrows': self.c1[0]+1
               , 'numitems':len(self.summary)
               , 'toprow': self.toprows
                }

        if not self.listing:
            self.listing = ScrollArea(**args)
        else:
            for k,v in args.items():
                if getattr(self.listing, k) != v:
                    self.listing = ScrollArea(**args)
                    break


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

    def update_selection(self):
        if (not self.selected) and self.summary.names:
            self.selected = self.summary.names[0]


    # Methods that actually write to the screen
    # =========================================

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

        bold = curses.A_BOLD

        self.win.bkgd(' ')
        self.win.border() # not sure how to make this A_BOLD
        self.win.addch(0,0,curses.ACS_ULCORNER,bold)
        self.win.addch(0,W,curses.ACS_URCORNER,bold)
        self.win.addch(H,0,curses.ACS_LLCORNER,bold)
        #self.win.addch(H,W,curses.ACS_LRCORNER,bold) error! why?
        for i in range(1,W):
            self.win.addch(0,i,curses.ACS_HLINE,bold)
            self.win.addch(H,i,curses.ACS_HLINE,bold)
        for i in range(1,H):
            self.win.addch(i,0,curses.ACS_VLINE,bold)
            self.win.addch(i,W,curses.ACS_VLINE,bold)

        # headers bottom border
        self.win.addch(2,0,curses.ACS_LTEE,bold)
        for i in range(0,W-1):
            self.win.addch(2,i+1,curses.ACS_HLINE,bold)
        self.win.addch(2,W,curses.ACS_RTEE,bold)

        # footer top border
        self.win.addch(H-2,0,curses.ACS_LTEE,bold)
        for i in range(0,W-1):
            self.win.addch(H-2,i+1,curses.ACS_HLINE,bold)
        self.win.addch(H-2,W,curses.ACS_RTEE,bold)

        # column border
        bw = (W-c2w-3)
        self.win.addch(0,bw,curses.ACS_TTEE,bold)
        self.win.vline(1,bw,curses.ACS_VLINE,H-1,bold)
        self.win.addch(2,bw,curses.ACS_PLUS,bold)
        self.win.addch(H-2,bw,curses.ACS_PLUS,bold)
        self.win.addch(H,bw,curses.ACS_BTEE,bold)


        # Banner text and column headers
        # ==============================

        l = (W - len(self.banner)) / 2
        r = l + len(self.banner)
        self.win.addch(0,l-2,curses.ACS_LARROW,bold)
        self.win.addch(0,l-1,curses.ACS_VLINE,bold)
        self.win.addch(0,r,curses.ACS_VLINE,bold)
        self.win.addch(0,r+1,curses.ACS_RARROW,bold)

        self.draw_banner()

        self.win.addstr(1,3,"TESTCASES",bold)
        self.win.addstr(1,self.W-c2w-1,"PASS",bold)
        self.win.addstr(1,self.W-c2w-1+5,"FAIL",bold)
        self.win.addstr(1,self.W-c2w-1+10," ERR",bold)
        self.win.addstr(1,self.W-c2w-1+15," ALL",bold)


        # Commit writes.
        # ==============

        self.win.refresh()


    def draw_content(self):
        """Draw the list of modules; called on almost every UI event.
        """

        W = self.W
        c1h, c1w = self.c1
        c2h, c2w = self.c2
        longname = self.selected


        # Clear listing area and draw any scrollbar.
        # ==========================================

        bg = curses.ACS_CKBOARD

        for i in range(self.toprows, self.toprows+self.listing.numrows):
            self.win.addstr(i,1,' '*(c1w+3))
            self.win.addstr(i,c1w+5,' '*(c2w+2))

            if self.listing.bar is None:
                self.win.addch(i,W,curses.ACS_VLINE,self.colors.WHITE)
            elif i in self.listing.bar:
                self.win.addstr(i,W,' ',self.blocks.BLUE)
            else:
                self.win.addch(i,W,bg,self.colors.BLUE)


        # Write listing rows if we have any.
        # ==================================
        # parent is a signal for the submodule bullets logic.

        if self.listing.numitems != 0:
            parent = ''
            for index, rownum  in self.listing:
                parent = self.draw_row(index, rownum, parent)
            self.selected = self.summary.names[self.listing.curitem]


        # Update totals.
        # ==============

        tpass5, tfail, terr, tall = self.summary.totals
        if tpass5 == '-':
            tpass5 = '- '
        if len(tfail) > 4:
            tfail = '9999'
        if len(terr) > 4:
            terr = '9999'
        if len(tall) > 4:
            tall = '9999'

        if not '%' in tpass5:
            color = self.colors.WHITE
        elif int(tfail) or int(terr):
            color = self.colors.RED
        else:
            color = self.colors.GREEN

        h = self.toprows + 1 + c1h + 1
        w = self.W-c2w-1
        self.win.addstr(h,w,tpass5.rjust(4),color)
        self.win.addstr(h,w+5,tfail.rjust(4),color)
        self.win.addstr(h,w+10,terr.rjust(4),color)
        self.win.addstr(h,w+15,tall.rjust(4),color)

        module = self.summary.module
        if len(module) > c1w:
            module = module[:c1w-3] + '...'
        module = module.ljust(c1w)
        self.win.addstr(h,3,module,color)


        # Finally, commit our writes.
        # ===========================

        self.win.refresh()


    def draw_row(self, index, rownum, parent):
        """Given two ints, write a row to the screen.

        The first int is the index into self.names. The second is the number of
        the row on the screen to write to. Both are 0-indexed. parent is a
        signal to our bullet logic (we show a secondary bullet for submodules).

        """

        c1h, c1w = self.c1
        c2h, c2w = self.c2

        name, stats, fresh = self.summary[index]


        # Pick a color, and see if we have a result to show.
        # ==================================================


        if stats is None:           # module/package

            color = self.colors.GRAY
            show_result = False

        else:                       # TestCase

            pass5, fail, err, all = stats

            if fresh is None:           # not run yet
                color = self.colors.WHITE
            elif fresh is False:        # run but not most recently
                if pass5 != '100%':
                    color = self.colors.RED_DIM
                else:
                    color = self.colors.GREEN_DIM
            elif fresh is True:         # just run
                if pass5 != '100%':
                    color = self.colors.RED
                else:
                    color = self.colors.GREEN

            show_result = True


        # Show the result if applicable.
        # ==============================

        if show_result:
            if not int(all):
                pass5 = fail = err = '-'

            if pass5 == '-':
                pass5 = '- '
            if len(fail) > 4:
                fail = '9999'
            if len(err) > 4:
                err = '9999'
            if len(all) > 4:
                all = '9999'

            w = self.W-c2w-1
            self.win.addstr(rownum,w,pass5.rjust(4),color)
            self.win.addstr(rownum,w+5,fail.rjust(4),color)
            self.win.addstr(rownum,w+10,err.rjust(4),color)
            self.win.addstr(rownum,w+15,all.rjust(4),color)


        # Short name, with indent.
        # ========================

        i = len('.'.join(self.module.split('.')[:-1]))
        parts = name[i:].lstrip('.').split('.')
        shortname = ('  '*(len(parts)-1)) + parts[-1]
        if len(shortname) > c1w:
            shortname = shortname[:c1w-3] + '...'
        shortname = shortname.ljust(c1w)
        self.win.addstr(rownum,3,shortname,color)


        # Bullet(s)
        # =========

        l = ' '
        r = ' '
        a = self.colors.BLUE
        if index == self.listing.curitem:
            if not parent:
                parent = name
            l = curses.ACS_RARROW
            r = curses.ACS_LARROW
        elif parent and name.startswith(parent):
            l = r = curses.ACS_BULLET
        self.win.addch(rownum,1,l,a)
        self.win.addch(rownum,self.W-1,r,a)


        return parent
