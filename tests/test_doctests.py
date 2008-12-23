try:
    from zope.testing import doctest
except ImportError:
    import doctest
    
import unittest
import glob
import os
import utils

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS)

def list_doctests():
    return [filename
            for filename
            in glob.glob(os.path.join(os.path.dirname(__file__), '*.txt'))]

def open_file(filename, mode='r'):
    """Helper function to open files from within the tests package."""
    return open(os.path.join(os.path.dirname(__file__), filename), mode)

def setUp(test):
    test.globs.update(dict(
            open_file = open_file,
            utils = utils
            ))

def test_suite():
    return unittest.TestSuite(
        [doctest.DocFileSuite(os.path.basename(filename),
                              optionflags=optionflags,
                              setUp=setUp)
         for filename
         in list_doctests()])


def test_run():
    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(test_suite())    

if __name__ == "__main__":
    test_run()
