#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Synchronize the page_hero resource directory to configured targets.

Edit the configuration section below to change the source, targets, or log
directory. The script supports Python 2.7 and Python 3 standard libraries.
"""

from __future__ import print_function

import argparse
import codecs
import errno
import hashlib
import os
import shutil
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# User configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# The source is relative to this script, so the current command-line working
# directory does not affect which resources are synchronized.
SOURCE_DIR = os.path.join(SCRIPT_DIR, "img", "page_hero")

TARGET_DIRS = [
    r"D:\a2\h5_copy\assets\res\ui\page_hero",
    r"D:\a2\assets\branches\dragon_ball_hero\cocos_studio\cocosstudio\sprite\page_hero",
    r"D:\a2\client\dragon_ball_hero\res\sprite\page_hero",
]

LOG_DIR = os.path.join(SCRIPT_DIR, "logs")

HASH_CHUNK_SIZE = 1024 * 1024
MODES = ("full", "incremental")
ACTION_NAMES = ("ADD", "MODIFIED", "DELETE")
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ABORTED = 2


try:
    text_type = unicode
except NameError:
    text_type = str


class ConfigurationError(ValueError):
    """Raised when a configured path is not safe or usable."""


class Change(object):
    """A planned file operation for one target directory."""

    def __init__(self, action, target_dir, relative_path, source_path=None, target_path=None):
        self.action = action
        self.target_dir = target_dir
        self.relative_path = relative_path
        self.source_path = source_path
        self.target_path = target_path


class TargetPlan(object):
    """All planned operations and planning errors for one target."""

    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.changes = []
        self.errors = []
        self.unchanged_count = 0


class RunResult(object):
    """The result returned by run_sync."""

    def __init__(self, status, exit_code, log_path, counts):
        self.status = status
        self.exit_code = exit_code
        self.log_path = log_path
        self.counts = counts


def display_path(path):
    return path


def console_print(message, stream=None):
    """Print text on Python 2/3 consoles with an encoding fallback."""

    if stream is None:
        stream = sys.stdout
    if sys.version_info[0] >= 3:
        stream.write(message + "\n")
    else:
        if not isinstance(message, text_type):
            message = text_type(message)
        encoding = getattr(stream, "encoding", None) or "utf-8"
        try:
            encoded_message = message.encode(encoding)
        except UnicodeEncodeError:
            encoded_message = message.encode("utf-8")
        stream.write(encoded_message + "\n")
    stream.flush()


def console_input(prompt, input_fn=None):
    """Read a console answer while allowing tests to inject input."""

    if input_fn is not None:
        return input_fn(prompt)
    try:
        input_fn = raw_input
    except NameError:
        input_fn = input
    if sys.version_info[0] < 3:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        try:
            prompt = prompt.encode(encoding)
        except UnicodeEncodeError:
            prompt = prompt.encode("utf-8")
    return input_fn(prompt)


def display_relative_path(path):
    return path.replace("\\", "/")


def normalized_relative_path(path):
    """Return a Windows-friendly, case-insensitive relative-path key."""

    return display_relative_path(path).lower()


def canonical_path(path):
    """Normalize a path for overlap and duplicate checks."""

    return os.path.normcase(os.path.abspath(path)).rstrip("\\/").lower()


def is_same_or_child(path, parent):
    path = canonical_path(path)
    parent = canonical_path(parent)
    return path == parent or path.startswith(parent + os.sep)


def index_files(root):
    """Index regular files below root by case-insensitive relative path."""

    files = {}
    if not os.path.exists(root):
        return files

    if not os.path.isdir(root):
        raise ConfigurationError("not a directory: {}".format(display_path(root)))

    for base, directories, filenames in os.walk(root):
        # Do not follow directory symlinks during a recursive resource scan.
        directories[:] = [directory for directory in directories
                           if not os.path.islink(os.path.join(base, directory))]
        for filename in filenames:
            path = os.path.join(base, filename)
            if os.path.islink(path) or not os.path.isfile(path):
                continue

            relative_path = os.path.relpath(path, root)
            key = normalized_relative_path(relative_path)
            existing = files.get(key)
            if existing is not None and existing != relative_path:
                raise ConfigurationError(
                    "case-insensitive path collision in {}: {} and {}".format(
                        display_path(root),
                        display_relative_path(existing),
                        display_relative_path(relative_path),
                    )
                )
            files[key] = relative_path

    return files


def sha256_file(path):
    """Calculate a file SHA-256 digest without loading it all at once."""

    digest = hashlib.sha256()
    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def validate_configuration(source_dir, target_dirs):
    """Validate paths before synchronization can modify files."""

    source_dir = os.path.abspath(source_dir)
    if not os.path.exists(source_dir):
        raise ConfigurationError("source directory does not exist: {}".format(display_path(source_dir)))
    if not os.path.isdir(source_dir):
        raise ConfigurationError("source path is not a directory: {}".format(display_path(source_dir)))
    if not target_dirs:
        raise ConfigurationError("at least one target directory is required")

    resolved_targets = []
    resolved_target_keys = set()
    for target_dir in target_dirs:
        resolved_target = os.path.abspath(target_dir)
        target_key = canonical_path(resolved_target)
        if target_key in resolved_target_keys:
            raise ConfigurationError("duplicate target directory: {}".format(display_path(resolved_target)))

        # A source/target overlap could make a recursive sync read or delete
        # resources outside the intended target. Reject it explicitly.
        if (is_same_or_child(resolved_target, source_dir)
                or is_same_or_child(source_dir, resolved_target)):
            raise ConfigurationError(
                "source and target directories must not overlap: {}".format(
                    display_path(resolved_target)
                )
            )
        resolved_targets.append(resolved_target)
        resolved_target_keys.add(target_key)


def build_target_plan(source_dir, source_files, target_dir, mode):
    """Build a target plan without copying or deleting anything."""

    if mode not in MODES:
        raise ValueError("unsupported mode: {}".format(mode))

    plan = TargetPlan(target_dir)
    try:
        target_files = index_files(target_dir)
    except (ConfigurationError, OSError) as error:
        plan.errors.append(str(error))
        return plan

    for key in sorted(source_files):
        source_relative = source_files[key]
        source_path = os.path.join(source_dir, source_relative)
        target_relative = target_files.get(key, source_relative)
        target_path = os.path.join(target_dir, target_relative)

        if key not in target_files:
            if (os.path.exists(target_path)
                    and not os.path.isfile(target_path)
                    and not (mode == "full" and os.path.isdir(target_path))):
                plan.errors.append(
                    "target path is not a file: {}".format(display_path(target_path))
                )
                continue
            plan.changes.append(Change(
                "ADD", target_dir, source_relative, source_path, target_path
            ))
            continue

        try:
            source_hash = sha256_file(source_path)
            target_hash = sha256_file(target_path)
        except OSError as error:
            plan.errors.append(
                "cannot compare {}: {}".format(display_path(target_path), error)
            )
            continue

        if source_hash == target_hash:
            plan.unchanged_count += 1
        else:
            plan.changes.append(Change(
                "MODIFIED", target_dir, source_relative, source_path, target_path
            ))

    if mode == "full":
        for key in sorted(target_files):
            if key in source_files:
                continue
            target_relative = target_files[key]
            plan.changes.append(Change(
                "DELETE", target_dir, target_relative,
                target_path=os.path.join(target_dir, target_relative),
            ))

    plan.changes.sort(
        key=lambda change: (change.action, normalized_relative_path(change.relative_path))
    )
    return plan


def create_log_path(log_dir):
    """Create a unique timestamped log path and its parent directory."""

    try:
        os.makedirs(log_dir)
    except OSError as error:
        if error.errno != errno.EEXIST or not os.path.isdir(log_dir):
            raise

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = os.path.join(log_dir, "sync_{}.log".format(timestamp))
    suffix = 1
    while os.path.exists(candidate):
        candidate = os.path.join(log_dir, "sync_{}_{}.log".format(timestamp, suffix))
        suffix += 1
    return candidate


def confirm_deletions(changes, input_fn):
    """Ask for explicit confirmation before a full-sync deletion."""

    deletions = [change for change in changes if change.action == "DELETE"]
    if not deletions:
        return True

    console_print(u"全量同步将删除以下目标文件：")
    for change in deletions:
        console_print(u"  {}: {}".format(
            display_path(change.target_dir),
            display_relative_path(change.relative_path),
        ))
    try:
        answer = console_input(u"确认删除这些文件？[y/N]: ", input_fn).strip().lower()
    except (EOFError, KeyboardInterrupt):
        console_print(u"未收到确认，已取消全量同步删除。")
        return False
    return answer in ("y", "yes")


def prune_empty_directories(root):
    """Remove empty child directories after a full synchronization."""

    if not os.path.exists(root) or not os.path.isdir(root):
        return

    paths = []
    for base, directories, filenames in os.walk(root, topdown=False):
        for directory in directories:
            path = os.path.join(base, directory)
            if not os.path.islink(path):
                paths.append(path)

    for path in paths:
        try:
            os.rmdir(path)
        except OSError:
            # Non-empty directories are harmless and require no action.
            continue


def apply_change(change):
    """Apply one planned file change."""

    if change.action == "DELETE":
        if change.target_path is None:
            raise OSError("delete operation has no target path")
        os.remove(change.target_path)
        return

    if change.source_path is None or change.target_path is None:
        raise OSError("copy operation has incomplete paths")
    parent = os.path.dirname(change.target_path)
    if parent and not os.path.isdir(parent):
        try:
            os.makedirs(parent)
        except OSError as error:
            if error.errno != errno.EEXIST or not os.path.isdir(parent):
                raise
    shutil.copy2(change.source_path, change.target_path)


def write_log_line(log_file, line):
    log_file.write(line + u"\n")
    log_file.flush()


def run_sync(source_dir, target_dirs, mode, log_dir, assume_yes=False, input_fn=None):
    """Run one synchronization and return its status and log path."""

    if mode not in MODES:
        raise ValueError("unsupported mode: {}".format(mode))

    source_dir = os.path.abspath(source_dir)
    target_dirs = [os.path.abspath(target_dir) for target_dir in target_dirs]
    validate_configuration(source_dir, target_dirs)

    log_path = create_log_path(log_dir)
    counts = dict((action, 0) for action in ACTION_NAMES)
    error_count = 0

    with codecs.open(log_path, "w", encoding="utf-8") as log_file:
        write_log_line(log_file, u"page_hero synchronization log")
        write_log_line(log_file, u"started: {}".format(datetime.now().isoformat()))
        write_log_line(log_file, u"mode: {}".format(mode))
        write_log_line(log_file, u"source: {}".format(display_path(source_dir)))
        write_log_line(log_file, u"targets:")
        for target_dir in target_dirs:
            write_log_line(log_file, u"  - {}".format(display_path(target_dir)))

        try:
            source_files = index_files(source_dir)
        except (ConfigurationError, OSError) as error:
            error_count += 1
            write_log_line(log_file, u"[ERROR] source scan - {}".format(error))
            write_log_line(log_file, u"status: FAILED")
            return RunResult("FAILED", EXIT_FAILURE, log_path, counts)

        plans = []
        for target_dir in target_dirs:
            plan = build_target_plan(source_dir, source_files, target_dir, mode)
            plans.append(plan)
            write_log_line(log_file, u"")
            write_log_line(log_file, u"target: {}".format(display_path(target_dir)))
            for error in plan.errors:
                error_count += 1
                write_log_line(log_file, u"[ERROR] planning - {}".format(error))

        all_changes = [
            change
            for plan in plans
            if not plan.errors
            for change in plan.changes
        ]
        deletion_changes = [
            change for change in all_changes if change.action == "DELETE"
        ]
        if mode == "full" and deletion_changes and not assume_yes:
            if not confirm_deletions(deletion_changes, input_fn):
                for change in deletion_changes:
                    write_log_line(log_file, u"[PENDING_DELETE] {}: {}".format(
                        display_path(change.target_dir),
                        display_relative_path(change.relative_path),
                    ))
                write_log_line(log_file, u"status: ABORTED")
                return RunResult("ABORTED", EXIT_ABORTED, log_path, counts)

        for plan in plans:
            if plan.errors:
                continue
            if not os.path.exists(plan.target_dir):
                try:
                    os.makedirs(plan.target_dir)
                except OSError as error:
                    if error.errno != errno.EEXIST or not os.path.isdir(plan.target_dir):
                        error_count += 1
                        write_log_line(log_file, u"[ERROR] create target {} - {}".format(
                            display_path(plan.target_dir), error
                        ))
                        continue

            # In full mode, delete target-only files before copying. This also
            # resolves file/directory conflicts such as source ``foo`` versus
            # target ``foo\old.png``.
            ordered_changes = []
            for action in ("DELETE", "ADD", "MODIFIED"):
                ordered_changes.extend(
                    change for change in plan.changes if change.action == action
                )
            for change in ordered_changes:
                try:
                    apply_change(change)
                except OSError as error:
                    error_count += 1
                    write_log_line(log_file, u"[ERROR] {}: {} - {}".format(
                        change.action,
                        display_relative_path(change.relative_path),
                        error,
                    ))
                    continue

                counts[change.action] += 1
                write_log_line(log_file, u"[{}] {}: {}".format(
                    change.action,
                    display_path(change.target_dir),
                    display_relative_path(change.relative_path),
                ))

                if mode == "full" and change.action == "DELETE":
                    # A directory may become empty after its last extra file
                    # is removed, allowing a subsequent ADD to use the same
                    # path as a source file.
                    prune_empty_directories(plan.target_dir)

            if mode == "full":
                prune_empty_directories(plan.target_dir)

        write_log_line(log_file, u"")
        write_log_line(log_file, u"summary:")
        write_log_line(log_file, u"  add: {}".format(counts["ADD"]))
        write_log_line(log_file, u"  modified: {}".format(counts["MODIFIED"]))
        write_log_line(log_file, u"  delete: {}".format(counts["DELETE"]))
        write_log_line(log_file, u"  errors: {}".format(error_count))
        status = "SUCCESS" if error_count == 0 else "FAILED"
        write_log_line(log_file, u"status: {}".format(status))

    return RunResult(
        status,
        EXIT_SUCCESS if error_count == 0 else EXIT_FAILURE,
        log_path,
        counts,
    )


def choose_mode(input_fn=None):
    """Read the synchronization mode from the interactive menu."""

    console_print(u"请选择同步模式：")
    console_print(u"  1. 全量同步（删除目标目录中多余文件）")
    console_print(u"  2. 增量同步（只新增和覆盖修改文件）")
    while True:
        choice = console_input(u"请输入 1 或 2: ", input_fn).strip()
        if choice == "1":
            return "full"
        if choice == "2":
            return "incremental"
        console_print(u"输入无效，请重新选择。")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Synchronize page_hero resources to configured target directories."
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        help="sync mode; omit it to use the interactive menu",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the full-sync deletion confirmation",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        mode = args.mode or choose_mode()
        result = run_sync(
            source_dir=SOURCE_DIR,
            target_dirs=TARGET_DIRS,
            mode=mode,
            log_dir=LOG_DIR,
            assume_yes=args.yes,
        )
    except (ConfigurationError, OSError, ValueError) as error:
        console_print(u"同步失败：{}".format(error), stream=sys.stderr)
        return EXIT_FAILURE
    except KeyboardInterrupt:
        console_print(u"\n已取消同步。", stream=sys.stderr)
        return EXIT_ABORTED

    console_print(u"同步{}：add={}, modified={}, delete={}。日志：{}".format(
        u"完成" if result.status == "SUCCESS" else u"未完全成功",
        result.counts["ADD"],
        result.counts["MODIFIED"],
        result.counts["DELETE"],
        display_path(result.log_path),
    ))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
