# -*- coding: utf-8 -*-

import codecs
import os
import shutil
import tempfile
import unittest

import img_sync


class ImageSyncTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.source = os.path.join(self.root, "source")
        self.target = os.path.join(self.root, "target")
        self.logs = os.path.join(self.root, "logs")
        os.makedirs(self.source)
        os.makedirs(self.target)

    def tearDown(self):
        shutil.rmtree(self.root)

    def path(self, *parts):
        return os.path.join(*parts)

    def write_file(self, path, content):
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
        with open(path, "wb") as file_handle:
            file_handle.write(content)

    def read_file(self, path):
        with open(path, "rb") as file_handle:
            return file_handle.read()

    def read_log(self, path):
        with codecs.open(path, "r", encoding="utf-8") as log_file:
            return log_file.read()

    def test_incremental_adds_modifications_and_keeps_target_only_files(self):
        self.write_file(self.path(self.source, "new.png"), b"new")
        self.write_file(self.path(self.source, "nested", "changed.png"), b"source")
        self.write_file(self.path(self.target, "nested", "changed.png"), b"old")
        self.write_file(self.path(self.target, "target_only.png"), b"keep")

        result = img_sync.run_sync(
            self.source, [self.target], "incremental", self.logs, assume_yes=True
        )

        self.assertEqual(result.exit_code, img_sync.EXIT_SUCCESS)
        self.assertEqual(result.counts, {"ADD": 1, "MODIFIED": 1, "DELETE": 0})
        self.assertEqual(self.read_file(self.path(self.target, "new.png")), b"new")
        self.assertEqual(
            self.read_file(self.path(self.target, "nested", "changed.png")), b"source"
        )
        self.assertEqual(
            self.read_file(self.path(self.target, "target_only.png")), b"keep"
        )
        log_text = self.read_log(result.log_path)
        self.assertIn("[ADD]", log_text)
        self.assertIn("[MODIFIED]", log_text)
        self.assertNotIn("[DELETE]", log_text)

    def test_full_removes_extra_files_and_preserves_source_tree(self):
        self.write_file(self.path(self.source, "keep.png"), b"keep")
        self.write_file(self.path(self.source, "nested", "changed.png"), b"source")
        self.write_file(self.path(self.target, "keep.png"), b"keep")
        self.write_file(self.path(self.target, "nested", "changed.png"), b"old")
        self.write_file(self.path(self.target, "obsolete.png"), b"remove")
        self.write_file(self.path(self.target, "obsolete", "old.png"), b"remove")

        result = img_sync.run_sync(
            self.source, [self.target], "full", self.logs, assume_yes=True
        )

        self.assertEqual(result.exit_code, img_sync.EXIT_SUCCESS)
        self.assertEqual(result.counts, {"ADD": 0, "MODIFIED": 1, "DELETE": 2})
        self.assertFalse(os.path.exists(self.path(self.target, "obsolete.png")))
        self.assertFalse(os.path.exists(self.path(self.target, "obsolete")))
        self.assertEqual(
            self.read_file(self.path(self.target, "nested", "changed.png")), b"source"
        )
        log_text = self.read_log(result.log_path)
        self.assertIn("[DELETE]", log_text)
        self.assertIn("obsolete/old.png", log_text)

    def test_declining_full_sync_does_not_modify_files(self):
        self.write_file(self.path(self.source, "new.png"), b"new")
        self.write_file(self.path(self.target, "obsolete.png"), b"remove")

        result = img_sync.run_sync(
            self.source,
            [self.target],
            "full",
            self.logs,
            input_fn=lambda unused_prompt: "n",
        )

        self.assertEqual(result.exit_code, img_sync.EXIT_ABORTED)
        self.assertFalse(os.path.exists(self.path(self.target, "new.png")))
        self.assertTrue(os.path.exists(self.path(self.target, "obsolete.png")))
        log_text = self.read_log(result.log_path)
        self.assertIn("[PENDING_DELETE]", log_text)
        self.assertIn("status: ABORTED", log_text)

    def test_missing_target_is_created(self):
        target = self.path(self.root, "missing-target")
        self.write_file(self.path(self.source, "image.png"), b"image")

        result = img_sync.run_sync(
            self.source, [target], "incremental", self.logs, assume_yes=True
        )

        self.assertEqual(result.exit_code, img_sync.EXIT_SUCCESS)
        self.assertEqual(self.read_file(self.path(target, "image.png")), b"image")

    def test_source_and_target_overlap_is_rejected(self):
        with self.assertRaises(img_sync.ConfigurationError):
            img_sync.run_sync(
                self.source,
                [self.path(self.source, "nested-target")],
                "incremental",
                self.logs,
                assume_yes=True,
            )

    def test_full_resolves_file_directory_conflict(self):
        self.write_file(self.path(self.source, "foo"), b"source-file")
        self.write_file(self.path(self.target, "foo", "old.png"), b"obsolete")

        result = img_sync.run_sync(
            self.source, [self.target], "full", self.logs, assume_yes=True
        )

        self.assertEqual(result.exit_code, img_sync.EXIT_SUCCESS)
        self.assertEqual(self.read_file(self.path(self.target, "foo")), b"source-file")
        self.assertEqual(result.counts, {"ADD": 1, "MODIFIED": 0, "DELETE": 1})


if __name__ == "__main__":
    unittest.main()
