import logging
import traceback

from assertEquals.interactive.utils import CommunicationProblem


logger = logging.getLogger('assertEquals.base')


class BaseScreen:
    """This is a mixin for objects representing curses screens.

    Provides:

        H, W -- the height and width of the screen, 0-indexed
        __loop() -- main event loop; calls react()
        go() -- called by CursesInterface; returns another BaseScreen
                error handling happens here
        getsize() -- returns the (H, W) tuple
        inited -- a boolean indicating whether init() has been run
        console_mode -- a boolean indicating whether to use getch() or getstr()


    Expects:

        init() -- called after the object is created, but before entering the
                  UI event loop; not called on resizes.
        react() -- method that takes a single curses key character, and returns
                   None or another BaseScreen
        resize() -- called before init(), and again every time the terminal is
                    resized.
        ui_chars -- sequence of keys to trap

    """

    inited = False
    console_mode = False

    def go(self):
        """Interact with the user, return the next screen.
        """
        try:
            self.H = self.W = 0 # triggers a call to resize, redrawing screen
            return self.__loop()
        except KeyboardInterrupt, SystemExit:
            raise
        except CommunicationProblem, prob:
            return DebuggingScreen(self, prob.proc)
        except Exception, exc:
            if hasattr(exc, 'traceback'):
                tb = exc.traceback
            else:
                tb = traceback.format_exc()
            return ErrorScreen(self, tb)
        except:
            tb = traceback.format_exc()
            return ErrorScreen(self, tb)


    def __loop(self):
        """Main loop.
        """

        while 1:

            # React to UI events, including resizes.
            # ======================================

            H, W = self.getsize()

            if (H <= 10) or (W <= 40): # terminal is too small
                self.win.clear()
                self.win.refresh()
                msg = "Terminal too small."
                if (H == 0) or (W < len(msg)):
                    continue
                self.win.addstr(H/2,(W-len(msg))/2,msg)
                self.win.refresh()
                c = self.win.getch()
                if c == ord('q'):
                    raise KeyboardInterrupt
                continue

            elif (self.H, self.W) != (H, W): # terminal has been resized
                self.win.clear()
                self.win.refresh()
                self.H, self.W = (H, W)
                self.resize()

            elif not self.inited:
                if hasattr(self, 'init'):
                    self.init()
                self.inited = True

            else: # react to key presses
                screen = None
                if self.console_mode:
                    screen = self.react(self.win.getstr())
                else:
                    c = self.win.getch()
                    if c in self.ui_chars:
                        screen = self.react(c)
                if screen is not None:
                    return screen


    def getsize(self):
        """getmaxyx is 1-indexed, but just about everything else is 0-indexed.
        """
        H, W = self.win.getmaxyx()
        return (H-1, W-1)



# Down here to dodge circular import without repeated import.
# ===========================================================
from assertEquals.interactive.screens.error import ErrorScreen
from assertEquals.interactive.screens.debugging import DebuggingScreen
