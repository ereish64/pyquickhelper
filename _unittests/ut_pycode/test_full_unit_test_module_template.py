"""
@brief      test log(time=600s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import time

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

from src.pyquickhelper.loghelper.flog import fLOG, noLOG
from src.pyquickhelper.pycode import get_temp_folder, process_standard_options_for_setup, is_travis_or_appveyor
from src.pyquickhelper.loghelper import git_clone

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class TestUnitTestFull(unittest.TestCase):

    def test_full_unit_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() == "travis":
            # disabled on travis
            return

        if sys.version_info[0] == 2:
            # the downloaded code is python 3
            return

        if __name__ != "__main__" or not os.path.exists("temp_full_unit_test"):
            temp_ = get_temp_folder(__file__, "temp_full_unit_test")
            temp = os.path.join(temp_, "python3_module_template")
            if not os.path.exists(temp):
                os.mkdir(temp)
            git_clone(temp, "github.com", "sdpython",
                      "python3_module_template")
            wait = 0
            while not os.path.exists(os.path.join(temp, "src")) and wait < 5:
                fLOG("wait", wait)
                time.sleep(1000)
                wait += 1
        else:
            temp = os.path.abspath(os.path.join(
                "temp_full_unit_test", "python3_module_template"))
        root = temp
        setup = os.path.join(root, "setup.py")
        pyq = os.path.join(os.path.dirname(src.pyquickhelper.__file__), "..")

        if "src" in sys.modules:
            memo = sys.modules["src"]
            del sys.modules["src"]
        else:
            memo = None

        def skip_function(name, code):
            return "test_example" not in name

        blog_list = """
            <?xml version="1.0" encoding="UTF-8"?>
            <opml version="1.0">
                <head>
                    <title>blog</title>
                </head>
                <body>
                    <outline text="python3_module_template"
                        title="python3_module_template"
                        type="rss"
                        xmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/python3_module_template/_downloads/rss.xml"
                        htmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/python3_module_template/blog/main_0000.html" />
                </body>
            </opml>
            """

        stdout = StringIO()
        stderr = StringIO()
        fLOG("setup", setup)
        thispath = os.path.abspath(os.path.dirname(__file__))
        thispath = os.path.normpath(os.path.join(thispath, "..", "..", "src"))

        fLOG("unit tests", root)
        for command in ["version", "write_version", "clean_pyd",
                        "setup_hook", "build_script", "copy27",
                        "unittests", "unittests_LONG", "unittests_SKIP",
                        "build_sphinx"]:
            if command == "build_sphinx" and is_travis_or_appveyor():
                # InkScape not installed for AppVeyor
                continue

            fLOG("#######################################################")
            fLOG(command)
            fLOG("#######################################################")
            rem = False
            PYTHONPATH = os.environ.get("PYTHONPATH", "")
            new_val = PYTHONPATH + ";" + thispath
            os.environ["PYTHONPATH"] = new_val.strip(";")
            if command == "build_sphinx":
                if thispath not in sys.path:
                    sys.path.append(thispath)
                    fLOG("add", thispath)
                    rem = True
            r = process_standard_options_for_setup(
                [command], setup, "python3_module_template", module_name="project_name",
                port=8067, requirements=["pyquickhelper"], blog_list=blog_list,
                fLOG=noLOG, additional_ut_path=[pyq, (root, True)],
                skip_function=skip_function, coverage_options={
                    "disable_coverage": True},
                hook_print=False, stdout=stdout, stderr=stderr, use_run_cmd=True)
            fLOG(r)
            if rem:
                del sys.path[sys.path.index(thispath)]
            os.environ["PYTHONPATH"] = PYTHONPATH

        fLOG("OUT:\n", stdout.getvalue())
        fLOG("ERR:\n", stderr.getvalue())

        if memo is not None:
            sys.modules["src"] = memo


if __name__ == "__main__":
    unittest.main()
