"""
@brief      test log(time=80s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import warnings
from docutils.parsers.rst import roles

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

from src.pyquickhelper.loghelper.flog import fLOG, download
from src.pyquickhelper.helpgen import generate_help_sphinx
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode import is_travis_or_appveyor


if sys.version_info[0] == 2:
    from codecs import open


class TestSphinxDocFull (unittest.TestCase):

    def test_full_documentation(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() is not None or sys.version_info[0] == 2:
            # travis due to the following:
            #       sitep = [_ for _ in site.getsitepackages() if "packages" in _]
            # AttributeError: 'module' object has no attribute
            # 'getsitepackages'
            # it also fails for python 2.7 (encoding issue)
            warnings.warn(
                "travis, appveyor, unable to test TestSphinxDocFull.test_full_documentation")
            return

        temp = get_temp_folder(__file__, "temp_full_doc_template")
        url = "https://github.com/sdpython/python3_module_template/archive/master.zip"
        fLOG("download", url)
        download(url, temp)
        assert not os.path.exists(os.path.join(temp, "src"))
        root = os.path.join(temp, "python3_module_template-master")

        fLOG("generate documentation", root)
        var = "project_name"

        # we modify conf.py to let it find pyquickhelper
        pyq = os.path.abspath(os.path.dirname(src.__file__))
        confpy = os.path.join(root, "_doc", "sphinxdoc", "source", "conf.py")
        with open(confpy, "r", encoding="utf8") as f:
            lines = f.read().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("sys."):
                break
        addition = "sys.path.append(r'{0}')".format(pyq)
        lines[i] = "{0}\n{1}".format(addition, lines[i])
        with open(confpy, "w", encoding="utf8") as f:
            f.write("\n".join(lines))

        # test
        for i in range(0, 3):
            fLOG("\n")
            fLOG("\n")
            fLOG("\n")
            fLOG("#################################################", i)
            fLOG("#################################################", i)
            fLOG("#################################################", i)

            # we add access to pyquickhelper
            p = os.path.abspath(os.path.dirname(src.__file__))
            fLOG("PYTHONPATH=", p)
            os.environ["PYTHONPATH"] = p
            if p not in sys.path:
                pos = len(sys.path)
                sys.path.append(p)
            else:
                pos = -1

            if "conf" in sys.modules:
                del sys.modules["conf"]

            fLOG("****", list(roles._roles.keys()))

            generate_help_sphinx(var, module_name=var, root=root,
                                 layout=["pdf", "html"],
                                 extra_ext=["tohelp"],
                                 from_repo=False, direct_call=i % 2 == 0)

            # we clean
            if "pyquickhelper" in sys.modules:
                del sys.modules["pyquickhelper"]
            os.environ["PYTHONPATH"] = ""
            if pos >= 0:
                del sys.path[pos]

            # checkings
            files = [os.path.join(root, "_doc", "sphinxdoc", "build", "html", "index.html"),
                     os.path.join(root, "_doc", "sphinxdoc",
                                  "build", "html", "all_indexes.html"),
                     os.path.join(root, "_doc", "sphinxdoc",
                                  "build", "html", "all_notebooks.html"),
                     ]
            for f in files:
                if not os.path.exists(f):
                    raise FileNotFoundError(f)

            assert not os.path.exists(os.path.join(temp, "_doc"))

            rss = os.path.join(
                root, "_doc", "sphinxdoc", "source", "blog", "rss.xml")
            with open(rss, "r", encoding="utf8") as f:
                content_rss = f.read()

            assert "__BLOG_ROOT__" not in content_rss
            # this should be replaced when uploading the stream onto the website
            # the website is unknown when producing the documentation
            # it should be resolved when uploading (the documentation could be
            # uploaded at different places)

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "build", "html", "index.html")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            if '<td><a class="reference internal" href="index_ext-tohelp.html#ext-tohelp"><span>ext-tohelp</span></a></td>' not in content and \
               '<td><a class="reference internal" href="index_ext-tohelp.html#ext-tohelp"><span class="std std-ref">ext-tohelp</span></a></td>' not in content:
                raise Exception(content)

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "build", "html", "all_notebooks.html")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            if '<img alt="_images/custom_notebooks.thumb.png" src="_images/custom_notebooks.thumb.png" />' not in content:
                raise Exception(content)

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "source", "all_notebooks.rst")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert 'notebooks/custom_notebooks' in content

            # checks slideshow was added
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "build", "notebooks", "bslides", "custom_notebooks.ipynb")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert '"slide"' in content

            # reveal.js + images
            rev = [os.path.join(root, "_doc", "sphinxdoc", "source", "phdoc_static", "reveal.js"),
                   os.path.join(root, "_doc", "sphinxdoc", "build",
                                "html", "_downloads", "reveal.js"),
                   os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                "_downloads", "Python_logo_and_wordmark.png"),
                   ]
            for r in rev:
                if not os.path.exists(r):
                    raise FileNotFoundError(r)


if __name__ == "__main__":
    unittest.main()
