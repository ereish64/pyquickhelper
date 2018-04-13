# -*- coding: utf-8 -*-
"""
@brief      test log(time=21s)
"""

import sys
import os
import unittest


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.ipythonhelper import test_notebook_execution_coverage
from src.pyquickhelper.pycode import add_missing_development_version


class TestFunctionTestNotebook(unittest.TestCase):

    def setUp(self):
        add_missing_development_version(["jyquickhelper"], __file__, hide=True)

    def test_notebook_example_pyquickhelper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        folder = os.path.join(os.path.dirname(__file__),
                              "..", "..", "_doc", "notebooks")
        test_notebook_execution_coverage(__file__, "compare_python_distribution", folder,
                                         'pyquickhelper', fLOG=fLOG,
                                         copy_files=["README.txt"])


if __name__ == "__main__":
    unittest.main()
