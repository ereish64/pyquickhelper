"""
@file
@brief Publishing coverage

.. versionadded:: 1.3
"""
import os
import re
import sys
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from ..loghelper import SourceRepository, noLOG
from ..filehelper import explore_folder_iterfile


if sys.version_info[0] == 2:
    FileNotFoundError = Exception
    from StringIO import StringIO
else:
    from io import StringIO


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=noLOG):
    """
    Publishes the coverage report on `codecov <https://codecov.io/>`_.
    See blog post :ref:`blogpost_coverage_codecov`.

    @param      path            path to source
    @param      token           token on codecov
    @param      commandline     see @see cl SourceRepository
    @param      fLOG            logging function
    @return                     out, err from function @see fn run_cmd
    """
    if os.path.isfile(path):
        report = path
    else:
        report = os.path.join(path, "_doc", "sphinxdoc",
                              "source", "coverage", "coverage_report.xml")

    report = os.path.normpath(report)
    if not os.path.exists(report):
        raise FileNotFoundError(report)

    proj = os.path.normpath(os.path.join(
        os.path.dirname(report), "..", "..", "..", ".."))

    src = SourceRepository(commandline=commandline)
    last = src.get_last_commit_hash(proj)
    cmd = ["--token={0}".format(token), "--file={0}".format(report),
           "--commit={0}".format(last), "--root={0} -X gcov".format(proj)]
    if token is not None:
        import codecov
        new_out = StringIO()
        new_err = StringIO()
        with redirect_stdout(new_out):
            with redirect_stderr(new_err):
                codecov.main(*cmd)
        out = new_out.getvalue()
        err = new_err.getvalue()
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\n[pyqerror]\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd


def coverage_combine(data_files, output_path, source, process=None):
    """
    Merges multiples reports.

    @param      data_files  report files (``.coverage``)
    @param      output_path output path
    @param      source      source directory
    @param      process     function which processes the coverage report

    The function *process* should have the signature:

    ::

        def process(content):
            # ...
            return content
    """
    reg = re.compile(',\\"(.*?[.]py)\\"')

    def copy_replace(source, dest, root_source):
        with open(source, "r") as f:
            content = f.read()
        if process is not None:
            content = process(content)
        cf = reg.findall(content)
        co = Counter([_.split('src')[0] for _ in cf])
        mx = max((v, k) for k, v in co.items())
        root = mx[1].rstrip('\\/')
        if '\\\\' in root:
            s2 = root_source.replace('\\', '\\\\').replace('/', '\\\\')
        else:
            s2 = root_source
        content = content.replace(root, s2)
        with open(dest, "w") as f:
            f.write(content)

    from coverage import Coverage
    dests = [os.path.join(output_path, '.coverage{0}'.format(
        i)) for i in range(len(data_files))]
    for fi, de in zip(data_files, dests):
        copy_replace(fi, de, source)
    cov = Coverage(source=source)
    cov.combine(dests)
    cov.html_report(directory=output_path)


def find_coverage_report(folder, exclude=None):
    """
    Finds all coverage reports in one subfolder.

    @param      folder      which folder to look at
    @param      exclude     list of subfolder not to look at
    @return                 list of files ``.coverage``

    The structure is supposed to:

    ::

        folder
          +- hash1
          |    +- date1
          |    |    +- .coverage - not selected
          |    +- date2
          |         +- .coverage - selected
          +- hash2
               +- date
                    +- .coverage - selected
    """
    regexp = re.compile('data_file=([a-zA-Z_]+)')
    regcov = re.compile(
        '<h1>Coveragereport:<spanclass=.?pc_cov.?>([0-9]+)%</span>')
    covs = {}
    subfold = os.listdir(folder)
    for sub in subfold:
        if exclude is not None and sub in exclude:
            continue
        full = os.path.join(folder, sub)
        keep = []
        nn = None
        cov = None
        for it in explore_folder_iterfile(full):
            name = os.path.split(it)[-1]
            dt = os.stat(full).st_mtime
            if name == 'index.html':
                with open(it, 'r') as f:
                    htd = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
                cont = regcov.findall(htd)
                if len(cont) > 0:
                    cov = cont[0]
            if name == 'covlog.txt':
                with open(it, 'r') as f:
                    logd = f.read()
                cont = regexp.findall(logd)
                if len(cont) > 0:
                    nn = cont[0]
            if name == '.coverage':
                keep.append((dt, it))
        if len(keep) == 0:
            continue
        mx = max(keep)
        covs[sub] = (mx[-1], nn, cov)
    return covs
