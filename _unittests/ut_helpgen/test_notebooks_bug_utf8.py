"""
@brief      test log(time=30s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import re
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

from src.pyquickhelper import fLOG, process_notebooks
from src.pyquickhelper.helpgen.sphinx_main import setup_environment_for_help
from src.pyquickhelper.helpgen.post_process import post_process_latex

if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugUtf8(unittest.TestCase):

    def test_notebook_utf8(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_utf8"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["latex", "pdf"]

        temp = os.path.join(path, "temp_nb_bug_utf8")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        if "travis" in sys.executable:
            warnings.warn(
                "travis, unable to test TestNoteBooksBugSvg.test_notebook_svg")
            return

        setup_environment_for_help()

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])

        with open(os.path.join(temp, "seance4_projection_population_correction.tex"), "r", encoding="utf8") as f:
            content = f.read()
        exp = "seance4_projection_population_correction_50_0.pdf"
        if exp not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()