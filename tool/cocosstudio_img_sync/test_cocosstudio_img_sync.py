# -*- coding: utf-8 -*-

from __future__ import print_function

import codecs
import os
import shutil
import tempfile
import unittest

import cocosstudio_img_sync as sync


class CocosStudioImageSyncTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.source = os.path.join(self.root, "source")
        self.target = os.path.join(self.root, "target")
        self.logs = os.path.join(self.root, "logs")
        os.makedirs(os.path.join(self.source, "bg"))
        os.makedirs(os.path.join(self.source, "sprite"))
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

    def runner_returning(self, xml_text):
        calls = []

        def runner(command):
            calls.append(command)
            return xml_text

        runner.calls = calls
        return runner

    def test_revision_sync_copies_only_selected_changes_and_deletes_removed_file(self):
        changed = self.path(self.source, "bg", "changed.jpg")
        added = self.path(self.source, "sprite", "new.png")
        removed = self.path(self.source, "bg", "removed.jpg")
        self.write_file(changed, b"new content")
        self.write_file(added, b"new image")
        self.write_file(self.path(self.target, "bg", "changed.jpg"), b"old content")
        self.write_file(self.path(self.target, "bg", "removed.jpg"), b"remove me")
        self.write_file(self.path(self.target, "bg", "target_only.jpg"), b"keep me")

        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<diff><paths>
  <path item="modified" kind="file">{changed}</path>
  <path item="added" kind="file">{added}</path>
  <path item="deleted" kind="file">{removed}</path>
  <path item="modified" kind="file">{outside}</path>
</paths></diff>""".format(
            changed=changed,
            added=added,
            removed=removed,
            outside=self.path(self.source, "csb", "not_an_image.udf"),
        )
        runner = self.runner_returning(xml_text)

        result = sync.run_sync(
            source_root=self.source,
            target_root=self.target,
            sync_dirs=("bg", "sprite"),
            mode="revision",
            revision="83672",
            log_dir=self.logs,
            run_svn_fn=runner,
        )

        self.assertEqual(result.exit_code, sync.EXIT_SUCCESS)
        self.assertEqual(result.counts["ADD"], 1)
        self.assertEqual(result.counts["MODIFIED"], 1)
        self.assertEqual(result.counts["DELETE"], 1)
        self.assertEqual(self.read_file(self.path(self.target, "bg", "changed.jpg")), b"new content")
        self.assertEqual(self.read_file(self.path(self.target, "sprite", "new.png")), b"new image")
        self.assertFalse(os.path.exists(self.path(self.target, "bg", "removed.jpg")))
        self.assertEqual(self.read_file(self.path(self.target, "bg", "target_only.jpg")), b"keep me")
        self.assertIn("-c", runner.calls[0])
        self.assertIn("83672", runner.calls[0])
        self.assertIn("[DELETE] bg/removed.jpg", self.read_log(result.log_path))

    def test_local_mode_includes_unversioned_file_and_handles_missing_file(self):
        changed = self.path(self.source, "bg", "changed.png")
        unversioned = self.path(self.source, "bg", "social_bg.jpg")
        missing = self.path(self.source, "sprite", "deleted.png")
        self.write_file(changed, b"changed")
        self.write_file(unversioned, b"unversioned")
        self.write_file(self.path(self.target, "bg", "changed.png"), b"old")
        self.write_file(self.path(self.target, "sprite", "deleted.png"), b"delete")

        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<status>
  <target path="{root}">
    <entry path="{changed}"><wc-status item="modified" props="none" /></entry>
    <entry path="{unversioned}"><wc-status item="unversioned" props="none" /></entry>
    <entry path="{missing}"><wc-status item="missing" props="none" /></entry>
    <entry path="{ignored}"><wc-status item="ignored" props="none" /></entry>
    <entry path="{outside}"><wc-status item="modified" props="none" /></entry>
  </target>
</status>""".format(
            root=self.source,
            changed=changed,
            unversioned=unversioned,
            missing=missing,
            ignored=self.path(self.source, "bg", "ignored.tmp"),
            outside=self.path(self.source, "csb", "scene.udf"),
        )
        runner = self.runner_returning(xml_text)

        result = sync.run_sync(
            source_root=self.source,
            target_root=self.target,
            sync_dirs=("bg", "sprite"),
            mode="local",
            log_dir=self.logs,
            run_svn_fn=runner,
        )

        self.assertEqual(result.exit_code, sync.EXIT_SUCCESS)
        self.assertEqual(result.counts["ADD"], 1)
        self.assertEqual(result.counts["MODIFIED"], 1)
        self.assertEqual(result.counts["DELETE"], 1)
        self.assertEqual(self.read_file(self.path(self.target, "bg", "social_bg.jpg")), b"unversioned")
        self.assertEqual(self.read_file(self.path(self.target, "bg", "changed.png")), b"changed")
        self.assertFalse(os.path.exists(self.path(self.target, "sprite", "deleted.png")))
        self.assertEqual(runner.calls[0][1], "status")

    def test_dry_run_does_not_modify_target(self):
        source_file = self.path(self.source, "bg", "new.png")
        target_file = self.path(self.target, "bg", "new.png")
        self.write_file(source_file, b"new")
        self.write_file(target_file, b"old")

        xml_text = """<status><target path="{root}">
  <entry path="{source}"><wc-status item="modified" props="none" /></entry>
</target></status>""".format(root=self.source, source=source_file)
        result = sync.run_sync(
            source_root=self.source,
            target_root=self.target,
            sync_dirs=("bg", "sprite"),
            mode="local",
            log_dir=self.logs,
            dry_run=True,
            run_svn_fn=self.runner_returning(xml_text),
        )

        self.assertEqual(result.exit_code, sync.EXIT_SUCCESS)
        self.assertEqual(self.read_file(target_file), b"old")
        self.assertIn("[dry-run MODIFIED] bg/new.png", self.read_log(result.log_path))

    def test_equal_target_file_is_not_copied(self):
        source_file = self.path(self.source, "bg", "same.png")
        target_file = self.path(self.target, "bg", "same.png")
        self.write_file(source_file, b"same")
        self.write_file(target_file, b"same")
        xml_text = """<status><target path="{root}">
  <entry path="{source}"><wc-status item="modified" props="none" /></entry>
</target></status>""".format(root=self.source, source=source_file)

        result = sync.run_sync(
            source_root=self.source,
            target_root=self.target,
            sync_dirs=("bg", "sprite"),
            mode="local",
            log_dir=self.logs,
            run_svn_fn=self.runner_returning(xml_text),
        )

        self.assertEqual(result.exit_code, sync.EXIT_SUCCESS)
        self.assertEqual(result.counts["UNCHANGED"], 1)
        self.assertEqual(result.counts["MODIFIED"], 0)

    def test_conflicting_target_directory_blocks_sync_without_modification(self):
        source_file = self.path(self.source, "bg", "conflict.png")
        target_path = self.path(self.target, "bg", "conflict.png")
        self.write_file(source_file, b"source")
        self.write_file(self.path(target_path, "old.txt"), b"keep")
        xml_text = """<status><target path="{root}">
  <entry path="{source}"><wc-status item="modified" props="none" /></entry>
</target></status>""".format(root=self.source, source=source_file)

        result = sync.run_sync(
            source_root=self.source,
            target_root=self.target,
            sync_dirs=("bg", "sprite"),
            mode="local",
            log_dir=self.logs,
            run_svn_fn=self.runner_returning(xml_text),
        )

        self.assertEqual(result.exit_code, sync.EXIT_FAILURE)
        self.assertTrue(os.path.isdir(target_path))
        self.assertEqual(self.read_file(self.path(target_path, "old.txt")), b"keep")

    def test_repository_style_svn_path_is_normalized(self):
        source_root = r"D:\workspace\cocosstudio"
        repository_path = "/assets/branches/dragon_ball_hero/cocosstudio/bg/a.png"
        self.assertEqual(
            sync._source_relative_path(repository_path, source_root),
            "bg/a.png",
        )

    def test_source_and_target_overlap_is_rejected(self):
        with self.assertRaises(sync.ConfigurationError):
            sync.validate_configuration(
                self.source,
                self.path(self.source, "target"),
                ("bg", "sprite"),
            )


if __name__ == "__main__":
    unittest.main()
