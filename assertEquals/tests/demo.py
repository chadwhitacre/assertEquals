import unittest

class BadTests(unittest.TestCase):

    def testFailure(self):
        self.assertEqual(1,2)

    def testError(self):
        raise 'heck'

    def testDebug(self):
        expected = 1
        actual = 2
        #import pdb; pdb.set_trace()
        self.assertEqual(expected, actual)

