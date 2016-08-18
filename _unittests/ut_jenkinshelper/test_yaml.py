"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re


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
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, evaluate_condition, convert_sequence_into_batch_file

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYaml(unittest.TestCase):

    def test_jenkins_job_verif(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local_jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34=None, Python35=sys.executable,
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj = load_yaml(yml, context=context)
        for k, v in obj.items():
            fLOG(k, type(v), v)
        assert "python" in obj
        assert isinstance(obj["python"], list)

    def test_evaluate_condition(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        r = evaluate_condition('[ ${PYTHON} == "C:\\Python35_x64\\pythonw.exe" ]',
                               dict(python="C:\\Python35_x64\\pythonw.exe"))
        assert r
        assert isinstance(r, bool)
        r = evaluate_condition('${PYTHON} == "C:\\Python35_x64\\pythonw.exe"',
                               dict(python="C:\\Python35_x64\\pythonw.exe"))
        assert r
        assert isinstance(r, bool)
        r = evaluate_condition('${PYTHON} != "C:\\Python35_x64\\pythonw.exe"',
                               dict(python="C:\\Python35_x64\\pythonw.exe"))
        assert not r
        assert isinstance(r, bool)
        r = evaluate_condition('[${PYTHON} != "C:\\Python35_x64\\pythonw.exe", ${PYTHON} == "C:\\Python35_x64\\pythonw.exe"]',
                               dict(python="C:\\Python35_x64\\pythonw.exe"))
        assert not r
        assert isinstance(r, bool)

    def test_jenkins_job_multiplication(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local_jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="fake", Python35=sys.executable,
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj = load_yaml(yml, context=context)
        res = list(enumerate_convert_yaml_into_instructions(obj))
        fLOG(len(res))
        for r in res:
            if None in r:
                raise Exception(r)
            if r[0][0] != "python":
                raise Exception(r)
        if len(res) != 6:
            rows = [str(_) for _ in res]
            raise Exception("\n".join(rows))
        doc = [[s[0] for s in seq if s[1] is not None] for seq in res]
        fLOG("------", doc)
        doc = [s for s in doc if "documentation" in s]
        self.assertEqual(len(doc), 3)

    def test_jconvert_sequence_into_batch_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            self.a_test_jconvert_sequence_into_batch_file(sys.platform)
        except NotImplementedError as e:
            pass
        self.a_test_jconvert_sequence_into_batch_file("win")

    def a_test_jconvert_sequence_into_batch_file(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local_jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="fake", Python35="C:\\Python35_x64",
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj = load_yaml(yml, context=context)
        res = list(enumerate_convert_yaml_into_instructions(obj))
        for r in res:
            conv = convert_sequence_into_batch_file(r, platform=platform)
            # fLOG("####", conv)
            assert isinstance(conv, str)
        assert len(res) > 0

        if platform.startswith("win"):
            expected = """
            @echo off

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\_virtualenv\\pyquickhelper
            if not exist "ROOT\\_virtualenv\\pyquickhelper" mkdir "ROOT\\_virtualenv\\pyquickhelper"
            "C:\\Python35_x64\\Scripts\\virtualenv.exe" --system-site-packages "ROOT\\_virtualenv\\pyquickhelper"
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\_virtualenv\\pyquickhelper\\Scripts;%PATH%
            pip install -r requirements.txt
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo SCRIPT
            set PATH=ROOT\\_virtualenv\\pyquickhelper\\Scripts;%PATH%
            python setup.py unittests [SKIP]
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo DOCUMENTATION
            set PATH=ROOT\\_virtualenv\\pyquickhelper\\Scripts;%PATH%
            python setup.py build_sphinx
            if %errorlevel% neq 0 exit /b %errorlevel%
            """.replace("            ", "").strip("\n \t\r")
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                raise Exception(mes)


if __name__ == "__main__":
    unittest.main()
