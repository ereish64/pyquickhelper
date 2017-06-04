"""
@brief      test log(time=3s)
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.loghelper.run_cmd import run_cmd, parse_exception_message


class TestRunCmdException(unittest.TestCase):

    def test_run_cmd_timeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "unexpectedcommand"
        try:
            out, err = run_cmd(cmd, wait=True, log_error=False, catch_exit=True, communicate=False,
                               tell_if_no_output=120, fLOG=fLOG)
            no_exception = True
        except Exception as e:
            no_exception = False
            out, err = parse_exception_message(e)
        self.assertTrue(out is not None)
        self.assertTrue(err is not None)
        self.assertTrue(not no_exception)
        self.assertEqual(len(out), 0)
        self.assertTrue(len(err) > 0)


if __name__ == "__main__":
    unittest.main()
