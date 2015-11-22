"""
@brief      test log(time=2s)
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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.filehelper import encrypt_stream, decrypt_stream, EncryptedBackup, FileTreeNode, TransferAPIFile
from src.pyquickhelper.filehelper.transfer_api import MockTransferAPI

if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO as StreamIO
else:
    from io import BytesIO as StreamIO


class TestBackupFiles(unittest.TestCase):

    def test_backup(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Crypto
            algo = "AES"
        except ImportError:
            algo = "fernet"

        temp = get_temp_folder(__file__, "temp_backup_files")

        root = os.path.normpath(os.path.join(temp, ".."))
        fLOG(root)

        api = MockTransferAPI()
        ft = FileTreeNode(root, filter=".*[.]py", repository=False)
        enc = EncryptedBackup(
            key="unit" * 8,
            file_tree_node=ft,
            transfer_api=api,
            file_status=os.path.join(temp, "status.txt"),
            file_map=os.path.join(temp, "mapping.txt"),
            root_local=os.path.join(temp, "..", ".."),
            threshold_size=2000,
            fLOG=fLOG,
            algo=algo)

        done, issue = enc.start_transfering()
        assert len(done) > 0
        assert len(issue) == 0

        for k, v in sorted(enc.Mapping.items()):
            fLOG(k, len(v.pieces), v)

        enc.load_mapping()
        outfile = os.path.join(temp, "backed_test_backup_file.py")
        fpth = "ut_filehelper\\test_backup_file.py"
        if not sys.platform.startswith("win"):
            fpth = fpth.replace("\\", "/")
        s = enc.retrieve(fpth, filename=outfile)

        with open(outfile, "r") as f:
            c2 = f.read()
        with open(__file__.replace(".pyc", ".py"), "r") as f:
            c1 = f.read()
        self.assertEqual(c1, c2)

    def test_backup_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        try:
            import Crypto
            algo = "AES"
        except ImportError:
            algo = "fernet"

        temp = get_temp_folder(__file__, "temp_backup_files_file")

        root = os.path.normpath(os.path.join(temp, ".."))
        fLOG(root)

        api = TransferAPIFile(os.path.join(temp, "backup"))
        ft = FileTreeNode(root, filter=".*[.]py", repository=False)
        enc = EncryptedBackup(
            key="unit" * 8,
            file_tree_node=ft,
            transfer_api=api,
            file_status=os.path.join(temp, "status.txt"),
            file_map=os.path.join(temp, "mapping.txt"),
            root_local=os.path.join(temp, "..", ".."),
            threshold_size=2000,
            fLOG=fLOG,
            algo=algo)

        done, issue = enc.start_transfering()
        assert len(done) > 0
        assert len(issue) == 0

        for k, v in sorted(enc.Mapping.items()):
            fLOG(k, len(v.pieces), v)

        enc.load_mapping()
        outfile = os.path.join(temp, "backed_test_backup_file.py")
        fpth = "ut_filehelper\\test_backup_file.py"
        if not sys.platform.startswith("win"):
            fpth = fpth.replace("\\", "/")
        s = enc.retrieve(fpth, filename=outfile)

        with open(outfile, "r") as f:
            c2 = f.read()
        with open(__file__.replace(".pyc", ".py"), "r") as f:
            c1 = f.read()
        self.assertEqual(c1, c2)

if __name__ == "__main__":
    unittest.main()