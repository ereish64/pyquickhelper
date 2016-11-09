"""
@brief      test log(time=18s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestNoteBooksBugDocx(unittest.TestCase):

    def test_notebook_docx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_docx"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["ipynb", "html", "python", "rst", "pdf", "docx"]

        temp = os.path.join(path, "temp_nb_bug_docx")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        if is_travis_or_appveyor() is not None:
            warnings.warn(
                "travis, appveyor, unable to test TestNoteBooksBugDocx.test_notebook_docx")
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])


if __name__ == "__main__":
    unittest.main()