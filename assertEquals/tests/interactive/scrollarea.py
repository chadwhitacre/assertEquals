import unittest

from assertEquals.interactive.utils import ScrollArea, DoneScrolling


def refuse_pass():
    pass
def refuse_raise():
    raise DoneScrolling


class TwoAndAHalfPageListing(unittest.TestCase):

    def setUp(self):
        #wheeee!
        self.area = ScrollArea(20, 50, 3)
        self.area.refuse = refuse_pass

    def testInit(self):
        expected = (20, 0, 50, 0, 20, 0, [3, 4, 5, 6, 7, 8, 9, 10, 11])
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # scroll_one
    # ==========

    def testScrollOne(self):
        self.area.scroll_one()
        expected = (20, 1, 50, 0, 20, 1, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollDownThenUp(self):
        self.area.scroll_one()
        self.area.scroll_one(up=True)
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # scroll
    # ======

    def testScroll(self):
        self.area.scroll(1)
        expected = (20, 1, 50, 0, 20, 1, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollToEdgeOfScreen(self):
        self.area.scroll(19)
        expected = (20, 19, 50, 0, 20, 19, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollJustPastEdgeOfScreen(self):
        self.area.scroll(20)
        expected = (20, 19, 50, 1, 21, 20, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollWellPastEdgeOfScreen(self):
        self.area.scroll(25)
        expected = (20, 19, 50, 6, 26, 25, range(5,14))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollToEdgeOfList(self):
        self.area.scroll(50)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollJustPastEdgeOfList(self):
        self.area.scroll(51)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollWellPastEdgeOfList(self):
        self.area.scroll(1000)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollTooFarDownTriggersRefusal(self):
        self.area.refuse = refuse_raise
        self.assertRaises(DoneScrolling, self.area.scroll, 1000)


    # scroll up

    def testScrollAllTheWayDownAndThenUpToEdgeOfList(self):
        self.area.scroll(50)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

        self.area.scroll(-50)
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollAllTheWayDownAndThenUpJustPastEdgeOfList(self):
        self.area.scroll(50)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

        self.area.scroll(-51)
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollAllTheWayDownAndThenUpWellPastEdgeOfList(self):
        self.area.scroll(50)
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

        self.area.scroll(-1000)
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollTooFarUpTriggersRefusal(self):
        self.area.refuse = refuse_raise
        self.assertRaises(DoneScrolling, self.area.scroll, -1000)


    # page_down
    # =========

    def testPageDown(self):
        self.area.page_down()
        expected = (20, 0, 50, 20, 40, 20, range(11,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageDownFullThenPartial(self):
        self.area.page_down()
        self.area.page_down()
        expected = (20, 0, 50, 40, 50, 40, range(19,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageDownFullThenPartialThenFinal(self):
        self.area.page_down()
        self.area.page_down()
        self.area.page_down()
        expected = (20, 0, 50, 49, 50, 49, range(22,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageDownCursorStaysPut(self):
        self.area.cursor = 7
        self.area.page_down()
        expected = (20, 7, 50, 20, 40, 27, range(11,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # page_up
    # =======
    # Each starts by scrolling all the way down.

    def testPageUp(self):
        self.area.scroll(50)
        self.area.page_up()
        expected = (20, 19, 50, 10, 30, 29, range(7,16))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageUpFullThenPartial(self):
        self.area.scroll(50)
        self.area.page_up()
        self.area.page_up()
        #expected = (20, 19, 50, 0, 20, 19, range(3,12))
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageUpCursorStaysPut(self):
        self.area.scroll(50)
        self.area.cursor = 7
        self.area.page_up()
        expected = (20, 7, 50, 10, 30, 17, range(7,16))
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # combined
    # ========

    def testPageDownIntoPartialThenUp(self):
        self.area.page_down()
        self.area.page_down()
        self.area.page_up()
        expected = (20, 0, 50, 20, 40, 20, range(11,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # home/end
    # ========

    def testHome(self):
        self.area.scroll(50)
        self.area.home()
        expected = (20, 0, 50, 0, 20, 0, range(3,12))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testEnd(self):
        self.area.end()
        expected = (20, 19, 50, 30, 50, 49, range(15,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)




class HalfPageListing(unittest.TestCase):

    def setUp(self):
        self.area = ScrollArea(20, 10, 3)
        self.area.refuse = refuse_pass

    def testInit(self):
        expected = (20, 0, 10, 0, 10, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # scroll_one
    # ==========

    def testScrollOne(self):
        self.area.scroll_one()
        expected = (20, 1, 10, 0, 10, 1, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollDownThenUp(self):
        self.area.scroll_one()
        self.area.scroll_one(up=True)
        expected = (20, 0, 10, 0, 10, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # scroll
    # ======

    def testScroll(self):
        self.area.scroll(1)
        expected = (20, 1, 10, 0, 10, 1, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollToEdgeOfScreen(self):
        self.area.scroll(19)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollJustPastEdgeOfScreen(self):
        self.area.scroll(20)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollWellPastEdgeOfScreen(self):
        self.area.scroll(25)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollToEdgeOfList(self):
        self.area.scroll(9)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollJustPastEdgeOfList(self):
        self.area.scroll(11)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollWellPastEdgeOfList(self):
        self.area.scroll(1000)
        expected = (20, 9, 10, 0, 10, 9, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollTooFarDownTriggersRefusal(self):
        self.area.refuse = refuse_raise
        self.assertRaises(DoneScrolling, self.area.scroll, 1000)


    # scroll up

    def testScrollAllTheWayDownAndThenUpToEdgeOfList(self):
        self.area.scroll(9)
        self.area.scroll(-9)
        expected = (20, 0, 10, 0, 10, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollAllTheWayDownAndThenUpJustPastEdgeOfList(self):
        self.area.scroll(9)
        self.area.scroll(-10)
        expected = (20, 0, 10, 0, 10, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollAllTheWayDownAndThenUpWellPastEdgeOfList(self):
        self.area.scroll(9)
        self.area.scroll(-1000)
        expected = (20, 0, 10, 0, 10, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollTooFarUpTriggersRefusal(self):
        self.area.refuse = refuse_raise
        self.assertRaises(DoneScrolling, self.area.scroll, -1000)



class EmptyPage(unittest.TestCase):

    def setUp(self):
        self.area = ScrollArea(20, 0, 3)
        self.area.refuse = refuse_raise

    def testInit(self):
        expected = (20, 0, 0, 0, 0, 0, None)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollDown(self):
        self.assertRaises(DoneScrolling, self.area.scroll, 1)

    def testScrollUp(self):
        self.assertRaises(DoneScrolling, self.area.scroll, -1)

    def testPageDown(self):
        self.assertRaises(DoneScrolling, self.area.page_down)

    def testPageUp(self):
        self.assertRaises(DoneScrolling, self.area.page_up)

    def testHome(self):
        self.assertRaises(DoneScrolling, self.area.home)

    def testEnd(self):
        self.assertRaises(DoneScrolling, self.area.end)



class ExactlyOneFullPage(unittest.TestCase):

    def setUp(self):
        self.area = ScrollArea(20, 20, 3)
        self.area.refuse = refuse_raise

    def testInit(self):
        expected = (20, 0, 20, 0, 20, 0, range(3,23))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testScrollDown(self):
        self.assertRaises(DoneScrolling, self.area.scroll, 20)

    def testScrollUp(self):
        self.assertRaises(DoneScrolling, self.area.scroll, -1)

    def testPageDown(self):
        self.assertRaises(DoneScrolling, self.area.page_down)

    def testPageUp(self):
        self.assertRaises(DoneScrolling, self.area.page_up)

    def testHome(self):
        self.assertRaises(DoneScrolling, self.area.home)

    def testEnd(self):
        self.area.end()
        self.assertRaises(DoneScrolling, self.area.end)



class PageDownBorking:#(unittest.TestCase):

    def setUp(self):
        self.area = ScrollArea(4, 5, 3)
        self.area.refuse = refuse_raise

    def testInit(self):
        expected = (4, 0, 5, 0, 4, 0)
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPageDown(self):
        self.area.page_down()
        expected = (4, 0, 5, 4, 5, 4)
        actual = self.area.stat()
        self.assertEqual(expected, actual)
        self.assertRaises(DoneScrolling, self.area.page_down)

    def testPageDownThenScrollUp(self):
        self.area.page_down()
        self.area.scroll(-1)
        expected = (4, 0, 5, 3, 5, 3)
        actual = self.area.stat()
        self.assertEqual(expected, actual)



class PageDownMultiplePages(unittest.TestCase):

    def setUp(self):
        self.area = ScrollArea(20, 50, 0)
        self.area.refuse = refuse_raise


    # cursor == 0

    def testOneRowShowing(self):
        self.area.start = 49
        self.area.end_ = 50
        self.assertRaises(DoneScrolling, self.area.page_down)
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testTwoRowsShowing(self):
        self.area.start = 48
        self.area.end_ = 50
        self.assertRaises(DoneScrolling, self.area.page_down)
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testPartialPageShowing(self):
        self.area.start = 30
        self.area.end_ = 50
        self.assertRaises(DoneScrolling, self.area.page_down)
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testExactlyOnePageShowing(self):
        self.area.start = 30
        self.area.end_ = 50
        self.assertRaises(DoneScrolling, self.area.page_down)
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testOneRowTillLastPage(self):
        self.area.start = 29
        self.area.end_ = 49
        self.area.page_down()
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testSeveralRowsTillLastPage(self):
        self.area.start = 24
        self.area.end_ = 44
        self.area.page_down()
        expected = (20, 0, 50, 44, 50, 44, range(17,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testExactlyOnePageTillLastPage(self):
        self.area.start = 10
        self.area.end_ = 30
        self.area.page_down()
        expected = (20, 0, 50, 30, 50, 30, range(12,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)


    # cursor != 0

    def testCursorExactlyOnePageTillLastPage(self):
        self.area.cursor = 1
        self.area.start = 10
        self.area.end_ = 30
        self.area.page_down()
        expected = (20, 1, 50, 30, 50, 31, range(12,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)

    def testExactlyOnePageShowingCursorAtBottom(self):
        self.area.cursor = 20
        self.area.start = 30
        self.area.end_ = 50
        self.assertRaises(DoneScrolling, self.area.page_down)
        expected = (20, 0, 50, 49, 50, 49, range(19,20))
        actual = self.area.stat()
        self.assertEqual(expected, actual)
