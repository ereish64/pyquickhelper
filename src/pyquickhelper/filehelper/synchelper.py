# -*- coding: utf-8 -*-
"""
@file
@brief Series of functions related to folder, explore, synchronize, remove (recursively).
"""

import os
import re
import sys
import fnmatch
from typing import Callable
from ..loghelper.flog import fLOG
from .file_tree_node import FileTreeNode
from .files_status import FilesStatus, checksum_md5
from ..loghelper.pqh_exception import PQHException

if sys.version_info[0] == 2:
    from codecs import open


def explore_folder(folder, pattern=None, neg_pattern=None, fullname=False, fLOG=None):
    """
    Returns the list of files included in a folder and in the subfolder.

    @param          folder      (str) folder
    @param          pattern     (str) if None, get all files, otherwise, it is a regular expression,
                                the filename must verify (with the folder if fullname is True)
    @param          neg_pattern (str) negative pattern
    @param          fullname    (bool) if True, include the subfolder while checking the regex (pattern)
    @param          fLOG        (fct) logging function
    @return                     (list, list), a list of folders, a list of files (the folder is not included the path name)

    .. versionchanged:: 1.7
        Parameter *fLOG* was added.
    """
    if pattern is not None:
        pattern = re.compile(pattern)
    if neg_pattern is not None:
        neg_pattern = re.compile(neg_pattern)

    found = 0
    filter = 0
    negfil = 0
    file, rep = [], {}
    for r, d, f in os.walk(folder):
        for a in f:
            found += 1
            temp = os.path.join(r, a)
            if pattern is not None:
                if fullname:
                    if not pattern.search(temp):
                        filter += 1
                        continue
                else:
                    if not pattern.search(a):
                        filter += 1
                        continue
            if neg_pattern is not None:
                if fullname:
                    if neg_pattern.search(temp):
                        negfil += 1
                        continue
                else:
                    if pattern.search(a):
                        negfil += 1
                        continue
            file.append(temp)
            r = os.path.split(temp)[0]
            rep[r] = None

    if fLOG:
        fLOG("[explore_folder] found={0} not-in={1} not-out={2} in '{3}'".format(
            found, filter, negfil, folder))
    keys = sorted(rep.keys())
    return keys, file


def explore_folder_iterfile(folder, pattern=None, neg_pattern=None, fullname=False):
    """
    Same as @see fn explore_folder but iterates on files.

    included in a folder and in the subfolder
    @param          folder          folder
    @param          pattern         if None, get all files, otherwise, it is a regular expression,
                                    the filename must verify (with the folder is fullname is True)
    @param          neg_pattern     negative pattern to exclude files
    @param          fullname        if True, include the subfolder while checking the regex
    @return                         iterator on files

    .. versionchanged:: 1.4
        Parameter *neg_pattern* was added.
    """
    if pattern is not None:
        pattern = re.compile(pattern)
    if neg_pattern is not None:
        neg_pattern = re.compile(neg_pattern)

    rep = {}
    for r, d, f in os.walk(folder):
        for a in f:
            temp = os.path.join(r, a)
            if pattern is not None:
                if fullname:
                    if not pattern.search(temp):
                        continue
                else:
                    if not pattern.search(a):
                        continue
            if neg_pattern is not None:
                if fullname:
                    if neg_pattern.search(temp):
                        continue
                else:
                    if pattern.search(a):
                        continue
            yield temp
            r = os.path.split(temp)[0]
            rep[r] = None


def explore_folder_iterfile_repo(folder, log=fLOG):
    """
    Returns all files present in folder and added to
    a :epkg:`SVN` or :epkg:`GIT` reposotory.

    @param      folder      folder
    @param      log         log function
    @return                 iterator
    """
    node = FileTreeNode(folder, repository=True, log=log)
    svnfiles = node.get_dict()
    for file in svnfiles:
        yield file


def synchronize_folder(p1: str, p2: str, hash_size=1024 ** 2, repo1=False, repo2=False,
                       size_different=True, no_deletion=False,
                       filter: [str, Callable[[str], str], None]=None,
                       filter_copy: [str, Callable[[str], str], None]=None,
                       avoid_copy=False,
                       operations=None, file_date: str=None, log1=False,
                       copy_1to2=False, fLOG=fLOG):
    """
    Synchronizes two folders (or copy if the second is empty),
    it only copies more recent files.
    It can walk through a :epkg:`git` repository or
    `SVN <https://subversion.apache.org/>`_.

    @param      p1                  (str) first path
    @param      p2                  (str) second path
    @param      hash_size           to check whether or not two files are different
    @param      repo1               assuming the first folder is under SVN or GIT,
                                    it uses pysvn to get the list
                                    of files (avoiding any extra files)
    @param      repo2               assuming the second folder is under SVN or GIT,
                                    it uses pysvn to get the list
                                    of files (avoiding any extra files)
    @param      size_different      if True, a file will be copied only if size are different,
                                    otherwise, it will be copied if the first file is more recent
    @param      no_deletion         if a file is found in the second folder and not in the first one,
                                    if will be removed unless no_deletion is True
    @param      filter              (str) None to accept every file, a string if it is a regular expression,
                                    a function for something more complex: function (fullname) --> True (every file is considered in lower case),
                                    (use :epkg:`*py:re:search`)
    @param      filter_copy         (str) None to accept every file, a string if it is a regular expression,
                                    a function for something more complex: function (fullname) --> True
    @param      avoid_copy          if True, just return the list of files which should be copied but does not do the copy
    @param      operations          if None, this function is called the following way ``operations(op,n1,n2)``
                                    if should return True if the file was updated
    @param      file_date           filename which contains information about when the last sync was done
    @param      log1                @see cl FileTreeNode
    @param      copy_1to2           only copy files from *p1* to *p2*
    @param      fLOG                logging function
    @return                         list of operations done by the function,
                                    list of 3-uple: action, source_file, dest_file

    if ``file_date`` is mentioned, the second folder is not explored. Only
    the modified files will be taken into account (except for the first sync).

    .. exref::
        :title: synchronize two folders

        The following function synchronizes a folder with another one
        on a USB drive or a network drive. To minimize the number of access
        to the other location, it stores the status of the previous
        synchronization in a file (``status_copy.txt`` in the below example).
        Next time, the function goes through the directory and sub-directories
        to synchronize and only propagates the modifications which happened
        since the last modification.
        The function ``filter_copy`` defines what file to synchronize or not.

        ::

            def filter_copy(file):
                return "_don_t_synchronize_" not in file

            synchronize_folder( "c:/mydata",
                                "g:/mybackup",
                                hash_size = 0,
                                filter_copy = filter_copy,
                                file_date = "c:/status_copy.txt")

        The function is able to go through 90.000 files and 90 Gb
        in 12 minutes (for an update).

    .. versionchanged:: 1.1
        Parameter *copy_1to2* was added.

    .. versionchanged:: 1.3
        Parameter *fLOG* was added.
    """

    fLOG("[synchronize_folder] from ", p1)
    fLOG("[synchronize_folder] to   ", p2)

    if file_date is not None and not os.path.exists(file_date):
        with open(file_date, "w", encoding="utf8") as f:
            f.write("")

    def mytrue(v):
        return True

    typstr = str  # unicode#
    if filter is None:
        tfilter = mytrue
    elif isinstance(filter, typstr):
        exp = re.compile(filter)

        def regtrue(be):
            return (True if exp.search(be) else False)

        tfilter = regtrue
    else:
        tfilter = filter

    def pr_filter(root, path, f, d):
        if d:
            return True
        path = path.lower()
        f = f.lower()
        be = os.path.join(path, f)
        return tfilter(be)

    if isinstance(filter_copy, str  # unicode#
                  ):
        rg = re.compile(filter_copy)

        def regtrue2(f):
            return rg.search(f) is not None

        filter_copy = regtrue2

    f1 = p1
    f2 = p2

    fLOG("[synchronize_folder]   exploring f1", f1)
    node1 = FileTreeNode(
        f1, filter=pr_filter, repository=repo1, log=True, log1=log1)
    fLOG("     number of found files (p1)", len(node1), node1.max_date())
    if file_date is not None:
        log1n = 1000 if log1 else None
        status = FilesStatus(file_date, fLOG=fLOG)
        res = list(status.difference(node1, u4=True, nlog=log1n))
    else:
        fLOG("[synchronize_folder]   exploring f2", f2)
        node2 = FileTreeNode(
            f2, filter=pr_filter, repository=repo2, log=True, log1=log1)
        fLOG("[synchronize_folder]     number of found files (p2)",
             len(node2), node2.max_date())
        res = node1.difference(node2, hash_size=hash_size)
        status = None

    action = []
    modif = 0

    fLOG("Starting synchronisation.")
    nbcur = 0
    nbprint = 0
    for op, file, n1, n2 in res:
        nbcur += 1
        if nbprint <= 50 and op not in ("==", '<', '<=', '<+') and (n1 is None or not n1.isdir()):
            fLOG(
                "[synchronize_folder] ... {0}/{1} (current: '{2}' :: {3})".format(nbcur, len(res), file, op))
            nbprint += 1
        if filter_copy is not None and not filter_copy(file):
            continue

        if operations is not None:
            r = operations(op, n1, n2)
            if r and status is not None:
                status.update_copied_file(n1.fullname)
                modif += 1
                if modif % 50 == 0:
                    fLOG(
                        "[synchronize_folder] Processed {0}/{1} (current: '{2}')".format(nbcur, len(res), file))
                    status.save_dates()
        else:

            if op in [">", ">+"]:
                if not n1.isdir():
                    if file_date is not None or not size_different or n2 is None or n1._size != n2._size:
                        if not avoid_copy:
                            n1.copyTo(f2)
                        action.append((">+", n1, f2))
                        if status is not None:
                            status.update_copied_file(n1.fullname)
                            modif += 1
                            if modif % 50 == 0:
                                fLOG(
                                    "[synchronize_folder] Processed {0}/{1} (current: '{2}')".format(nbcur, len(res), file))
                                status.save_dates()
                    else:
                        pass

            elif op in ["<+"]:
                if not copy_1to2:
                    if n2 is None:
                        if not no_deletion:
                            # this case happens when it does not know sideB (sideA is stored in a file)
                            # it needs to remove file, file refers to this side
                            filerel = os.path.relpath(file, start=p1)
                            filerem = os.path.join(p2, filerel)
                            try:
                                ft = FileTreeNode(p2, filerel)
                            except PQHException:
                                ft = None  # probably already removed

                            if ft is not None:
                                action.append((">-", None, ft))
                                if not avoid_copy:
                                    fLOG("- remove ", filerem)
                                    os.remove(filerem)
                                if status is not None:
                                    status.update_copied_file(
                                        file, delete=True)
                                    modif += 1
                                    if modif % 50 == 0:
                                        fLOG(
                                            "[synchronize_folder] Processed {0}/{1} (current: '{2}')".format(nbcur, len(res), file))
                                        status.save_dates()
                            else:
                                fLOG(
                                    "- skip (probably already removed) ", filerem)
                    else:
                        if not n2.isdir() and not no_deletion:
                            if not avoid_copy:
                                n2.remove()
                            action.append((">-", None, n2))
                            if status is not None:
                                status.update_copied_file(
                                    n1.fullname, delete=True)
                                modif += 1
                                if modif % 50 == 0:
                                    fLOG(
                                        "[synchronize_folder] Processed {0}/{1} (current: '{2}')".format(nbcur, len(res), file))
                                    status.save_dates()
            elif n2 is not None and n1._size != n2._size and not n1.isdir():
                fLOG("[synchronize_folder] problem: size are different for file %s (%d != %d) dates (%s,%s) (op %s)" % (
                    file, n1._size, n2._size, n1._date, n2._date, op))
                # n1.copyTo (f2)
                # raise Exception ("size are different for file %s (%d != %d) (op %s)" % (file, n1._size, n2._size, op))

    if status is not None:
        status.save_dates(file_date)

    return action


def remove_folder(top, remove_also_top=True, raise_exception=True):
    """
    Removes everything in folder top.

    @param      top                 path to remove
    @param      remove_also_top     remove also root
    @param      raise_exception     raise an exception if a file cannot be remove
    @return                         list of removed files and folders
                                     --> list of tuple ( (name, "file" or "dir") )

    .. versionchanged:: 0.9
        Parameter *raise_exception* was added.
    """
    if top in ["", "C:", "c:", "C:\\", "c:\\", "d:", "D:", "D:\\", "d:\\"]:
        raise Exception("top is a root (c: for example), this is not safe")

    res = []
    first_root = None
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            t = os.path.join(root, name)
            try:
                os.remove(t)
            except PermissionError as e:
                if raise_exception:
                    raise PermissionError(
                        "unable to remove file {0}".format(t)) from e
                else:
                    remove_also_top = False
                    continue
            res.append((t, "file"))
        for name in dirs:
            t = os.path.join(root, name)
            try:
                os.rmdir(t)
            except OSError as e:
                if raise_exception:
                    raise OSError(
                        "unable to remove folder {0}".format(t)) from e
                else:
                    remove_also_top = False
                    continue
            res.append((t, "dir"))
        if first_root is None:
            first_root = root

    if first_root is not None and remove_also_top:
        res.append((root, "dir"))
        os.rmdir(root)

    return res


def has_been_updated(source, dest):
    """
    It assumes ``dest`` is a copy of ``source``, it wants to know
    if the copy is up to date or not.

    @param      source      filename
    @param      dest        copy
    @return                 True,reason or False,None
    """
    if not os.path.exists(dest):
        return True, "new"

    st1 = os.stat(source)
    st2 = os.stat(dest)
    if st1.st_size != st2.st_size:
        return True, "size"

    d1 = st1.st_mtime
    d2 = st2.st_mtime
    if d1 > d2:
        return True, "date"

    c1 = checksum_md5(source)
    c2 = checksum_md5(dest)

    if c1 != c2:
        return True, "md5"

    return False, None


def walk(top, onerror=None, followlinks=False, neg_filter=None):
    """
    Does the same as :epkg:`*py:os:walk`
    plus do not go through a sub-folder if this one is big. Folders such build or Debug or Release
    may not need to be dug into.

    @param      top             folder
    @param      onerror         see :epkg:`*py:os:walk`
    @param      followlinks     see :epkg:`*py:os:walk`
    @param      neg_filter      filtering, a string, every folder verifying the filter will be excluded
                                (file pattern, not a regular expression pattern)
    @return                     see :epkg:`*py:os:walk`
    """
    if neg_filter is None:
        for root, dirs, files in os.walk(top=top, onerror=onerror, followlinks=followlinks):
            yield root, dirs, files
    else:
        typstr = str  # unicode #
        f = not isinstance(neg_filter, typstr)
        for root, dirs, files in os.walk(top, onerror=onerror, followlinks=followlinks):
            rem = []
            for i, d in enumerate(dirs):
                if (f and neg_filter(d)) or (not f and fnmatch.fnmatch(d, neg_filter)):
                    rem.append(i)
            if rem:
                rem.reverse()
                for i in rem:
                    del dirs[i]

            yield root, dirs, files
