#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Synchronize changed CocosStudio resources to the game resource tree.

The tool supports two change-discovery modes:

* ``revision``: use ``svn diff --summarize --xml -c REV`` to select the files
  changed by one SVN revision, then copy the files from the current source
  working copy.
* ``local``: use ``svn status --xml`` to select local working-copy changes.
  Unversioned files inside the configured directories are included as adds.

Only the configured source directories are considered.  This is an
incremental synchronizer: target-only files are never removed unless their
relative path is explicitly reported as a deletion by SVN.

The implementation uses only the Python standard library and is compatible
with Python 2.7 and Python 3.
"""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import errno
import hashlib
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_ROOT = r"D:\a2\assets\branches\dragon_ball_hero\cocos_studio\cocosstudio"
TARGET_ROOT = r"D:\a2\client\dragon_ball_hero\res"

# Add future CocosStudio resource directories here.  The target uses the same
# relative directory names below TARGET_ROOT.
SYNC_DIRS = ("bg", "sprite")

LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
HASH_CHUNK_SIZE = 1024 * 1024

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


try:
    text_type = unicode
except NameError:
    text_type = str


def as_unicode(value):
    """Convert Python 2 byte strings to UTF-8 text for log/console output."""

    if isinstance(value, text_type):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return text_type(value)


class ConfigurationError(ValueError):
    """Raised when a configured path or sync scope is unsafe or unusable."""


class SyncError(RuntimeError):
    """Raised when SVN output cannot be obtained or parsed."""


class Change(object):
    """A source-side change selected for synchronization."""

    def __init__(self, action, relative_path, detail=""):
        self.action = action
        self.relative_path = relative_path
        self.detail = detail


class ChangeCollection(object):
    """Changes and non-recoverable discovery errors from one scan."""

    def __init__(self, changes=None, errors=None):
        self.changes = changes or []
        self.errors = errors or []


class Operation(object):
    """A concrete target operation after comparing source and target."""

    def __init__(self, action, relative_path, source_path=None, target_path=None):
        self.action = action
        self.relative_path = relative_path
        self.source_path = source_path
        self.target_path = target_path


class SyncPlan(object):
    """Planned operations and errors; no filesystem changes are made here."""

    def __init__(self):
        self.operations = []
        self.errors = []
        self.unchanged_count = 0
        self.missing_delete_count = 0


class RunResult(object):
    """Result returned by :func:`run_sync`."""

    def __init__(self, status, exit_code, log_path, counts):
        self.status = status
        self.exit_code = exit_code
        self.log_path = log_path
        self.counts = counts


def display_path(path):
    return path


def display_relative_path(path):
    return as_unicode(path).replace("\\", "/")


def normalized_relative_path(path):
    return display_relative_path(path).lower()


def canonical_path(path):
    return os.path.normcase(os.path.abspath(path)).rstrip("\\/").lower()


def is_same_or_child(path, parent):
    path = canonical_path(path)
    parent = canonical_path(parent)
    return path == parent or path.startswith(parent + os.sep)


def console_print(message, stream=None):
    """Print text on Python 2/3 consoles with an encoding fallback."""

    if stream is None:
        stream = sys.stdout
    if not isinstance(message, text_type):
        message = text_type(message)

    try:
        stream.write(message)
        stream.write(u"\n")
    except Exception:
        encoding = getattr(stream, "encoding", None) or "utf-8"
        data = message.encode(encoding, "replace")
        stream.write(data)
        stream.write("\n")
    try:
        stream.flush()
    except Exception:
        pass


def _decode_output(value):
    if value is None:
        return u""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def run_svn(command):
    """Run an SVN command and return decoded stdout."""

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as error:
        raise SyncError("无法启动 svn 命令: {0}".format(error))

    stdout_data, stderr_data = process.communicate()
    stdout_text = _decode_output(stdout_data)
    stderr_text = _decode_output(stderr_data)
    if process.returncode != 0:
        raise SyncError(
            "svn 命令执行失败。\n命令: {0}\n退出码: {1}\nstderr: {2}".format(
                command,
                process.returncode,
                stderr_text.strip(),
            )
        )
    return stdout_text


def _safe_relative_path(path):
    """Normalize a relative path and reject absolute/traversal paths."""

    if path is None:
        return ""
    path = as_unicode(path).strip().replace("\\", "/")
    if not path:
        return ""

    # A repository path may be absolute while a local target path must not be.
    # Repository paths are converted before reaching this helper.
    if path.startswith("/") or path.startswith("\\"):
        raise ConfigurationError("不安全的相对路径: {0}".format(path))
    if len(path) >= 2 and path[1] == ":":
        raise ConfigurationError("不安全的相对路径: {0}".format(path))

    parts = []
    for part in path.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            raise ConfigurationError("不安全的相对路径: {0}".format(path))
        parts.append(part)
    return "/".join(parts)


def normalize_sync_dirs(sync_dirs):
    """Validate and normalize configured paths relative to both roots."""

    if not sync_dirs:
        raise ConfigurationError("至少需要一个同步目录")

    result = []
    seen = set()
    for sync_dir in sync_dirs:
        normalized = _safe_relative_path(sync_dir)
        if not normalized:
            raise ConfigurationError("同步目录不能为空")
        key = normalized_relative_path(normalized)
        if key in seen:
            raise ConfigurationError("重复的同步目录: {0}".format(normalized))
        seen.add(key)
        result.append(normalized)
    return result


def _source_relative_path(raw_path, source_root):
    """Convert local or repository-style SVN paths to source-root-relative."""

    raw = _decode_output(raw_path).strip().replace("\\", "/")
    if not raw:
        return ""

    source_root = os.path.abspath(source_root)
    try:
        local_candidate = os.path.abspath(raw)
        if is_same_or_child(local_candidate, source_root):
            relative = os.path.relpath(local_candidate, source_root)
            return _safe_relative_path(relative)
    except (OSError, ValueError):
        # The value can be a repository path or URL rather than a local path.
        pass

    parts = [part for part in raw.split("/") if part]
    source_base = os.path.basename(source_root.rstrip("\\/"))
    source_base_key = source_base.lower()
    for index in range(len(parts) - 1, -1, -1):
        if parts[index].lower() == source_base_key:
            return _safe_relative_path("/".join(parts[index + 1 :]))

    # Some SVN output formats already provide a relative path.
    return _safe_relative_path(raw)


def _join_root_relative(root, relative_path):
    relative_path = _safe_relative_path(relative_path)
    return os.path.join(root, relative_path.replace("/", os.sep))


def _is_in_sync_scope(relative_path, sync_dirs):
    key = normalized_relative_path(relative_path)
    for sync_dir in sync_dirs:
        scope_key = normalized_relative_path(sync_dir)
        if key == scope_key or key.startswith(scope_key + "/"):
            return True
    return False


def index_files(root):
    """Index regular files below *root* by case-insensitive relative path."""

    files = {}
    if not os.path.exists(root):
        return files
    if not os.path.isdir(root):
        raise ConfigurationError("不是目录: {0}".format(display_path(root)))

    for base, directories, filenames in os.walk(root):
        directories[:] = [
            directory
            for directory in directories
            if not os.path.islink(os.path.join(base, directory))
        ]
        for filename in filenames:
            path = os.path.join(base, filename)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            relative_path = os.path.relpath(path, root)
            key = normalized_relative_path(relative_path)
            existing = files.get(key)
            if existing is not None and existing != relative_path:
                raise ConfigurationError(
                    "目录中存在大小写不敏感的路径冲突: {0} 与 {1}".format(
                        display_relative_path(existing),
                        display_relative_path(relative_path),
                    )
                )
            files[key] = relative_path
    return files


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def has_symlink_between(path, root):
    """Return whether *path* or one of its ancestors is a symlink."""

    current = os.path.abspath(path)
    root = os.path.abspath(root)
    while True:
        if os.path.islink(current):
            return True
        if canonical_path(current) == canonical_path(root):
            return False
        parent = os.path.dirname(current)
        if parent == current or not is_same_or_child(parent, root):
            return False
        current = parent


def validate_configuration(source_root, target_root, sync_dirs):
    source_root = os.path.abspath(source_root)
    target_root = os.path.abspath(target_root)
    sync_dirs = normalize_sync_dirs(sync_dirs)

    if not os.path.exists(source_root):
        raise ConfigurationError("源目录不存在: {0}".format(display_path(source_root)))
    if not os.path.isdir(source_root):
        raise ConfigurationError("源路径不是目录: {0}".format(display_path(source_root)))
    if is_same_or_child(source_root, target_root) or is_same_or_child(target_root, source_root):
        raise ConfigurationError("源目录和目标目录不能互相包含: {0}".format(display_path(target_root)))

    for sync_dir in sync_dirs:
        source_scope = _join_root_relative(source_root, sync_dir)
        if not os.path.exists(source_scope):
            raise ConfigurationError("源同步目录不存在: {0}".format(display_path(source_scope)))
        if not os.path.isdir(source_scope):
            raise ConfigurationError("源同步路径不是目录: {0}".format(display_path(source_scope)))

    return source_root, target_root, sync_dirs


def _xml_root(xml_text):
    xml_text = _decode_output(xml_text)
    if isinstance(xml_text, text_type):
        xml_text = xml_text.encode("utf-8")
    try:
        return ET.fromstring(xml_text)
    except Exception as error:
        raise SyncError("无法解析 svn XML 输出: {0}".format(error))


def _add_change(change_map, action, relative_path, detail=""):
    """Add or merge a file change, keeping the final action for duplicates."""

    action = str(action).upper()
    if action not in ("ADD", "MODIFIED", "DELETE"):
        return
    relative_path = _safe_relative_path(relative_path)
    if not relative_path:
        return

    key = normalized_relative_path(relative_path)
    priority = {"ADD": 1, "MODIFIED": 2, "DELETE": 3}
    existing = change_map.get(key)
    if existing is None or priority[action] >= priority[existing.action]:
        change_map[key] = Change(action, relative_path, detail)


def _add_directory_files(change_map, root, directory_relative_path, action, detail=""):
    """Expand a directory change into regular file changes."""

    directory_path = _join_root_relative(root, directory_relative_path)
    if not os.path.isdir(directory_path):
        return
    files = index_files(directory_path)
    for child_relative in files.values():
        combined = _safe_relative_path(
            display_relative_path(os.path.join(directory_relative_path, child_relative))
        )
        _add_change(change_map, action, combined, detail)


def _sorted_changes(change_map):
    return sorted(
        change_map.values(),
        key=lambda change: normalized_relative_path(change.relative_path),
    )


def collect_revision_changes(
    source_root,
    target_root,
    sync_dirs,
    revision,
    run_svn_fn=run_svn,
):
    """Collect file changes from one SVN revision."""

    try:
        revision_number = int(str(revision))
    except (TypeError, ValueError):
        raise ConfigurationError("revision 必须是正整数: {0}".format(revision))
    if revision_number <= 0:
        raise ConfigurationError("revision 必须是正整数: {0}".format(revision))

    source_scopes = [
        _join_root_relative(source_root, sync_dir) for sync_dir in sync_dirs
    ]
    command = ["svn", "diff", "--summarize", "--xml", "-c", str(revision_number)]
    command.extend(source_scopes)
    xml_text = run_svn_fn(command)
    root = _xml_root(xml_text)

    change_map = {}
    for path_node in root.findall(".//paths/path"):
        raw_path = path_node.text or ""
        relative_path = _source_relative_path(raw_path, source_root)
        if not relative_path or not _is_in_sync_scope(relative_path, sync_dirs):
            continue

        item = (path_node.attrib.get("item") or "").strip().lower()
        kind = (path_node.attrib.get("kind") or "file").strip().lower()
        action = {
            "added": "ADD",
            "modified": "MODIFIED",
            "replaced": "MODIFIED",
            "deleted": "DELETE",
        }.get(item)
        if action is None:
            continue

        detail = "revision {0} ({1})".format(revision_number, item)
        source_path = _join_root_relative(source_root, relative_path)
        if kind == "dir" or os.path.isdir(source_path):
            if action == "DELETE":
                _add_directory_files(
                    change_map,
                    target_root,
                    relative_path,
                    action,
                    detail,
                )
            elif action == "ADD":
                _add_directory_files(
                    change_map,
                    source_root,
                    relative_path,
                    action,
                    detail,
                )
            # A property-only directory modification must not cause a whole
            # directory copy; child file entries, when relevant, are reported
            # separately by svn diff.
            continue

        _add_change(change_map, action, relative_path, detail)

    return ChangeCollection(changes=_sorted_changes(change_map))


def _status_action(item, props):
    item = str(item or "").strip().lower()
    props = str(props or "").strip().lower()
    if item in ("added", "unversioned"):
        return "ADD"
    if item in ("modified", "replaced"):
        return "MODIFIED"
    if item in ("deleted", "missing"):
        return "DELETE"
    if item == "normal" and props == "modified":
        return "MODIFIED"
    return None


def collect_local_changes(
    source_root,
    target_root,
    sync_dirs,
    run_svn_fn=run_svn,
):
    """Collect local SVN working-copy changes, including unversioned files."""

    source_scopes = [
        _join_root_relative(source_root, sync_dir) for sync_dir in sync_dirs
    ]
    command = ["svn", "status", "--xml", "--depth", "infinity", "--no-ignore"]
    command.extend(source_scopes)
    xml_text = run_svn_fn(command)
    root = _xml_root(xml_text)

    change_map = {}
    errors = []
    for entry in root.findall(".//entry"):
        raw_path = entry.attrib.get("path") or ""
        relative_path = _source_relative_path(raw_path, source_root)
        if not relative_path or not _is_in_sync_scope(relative_path, sync_dirs):
            continue

        wc_status = entry.find("wc-status")
        if wc_status is None:
            continue
        item = wc_status.attrib.get("item") or ""
        props = wc_status.attrib.get("props") or ""
        action = _status_action(item, props)
        if action is None:
            if str(item).strip().lower() in (
                "conflicted",
                "obstructed",
                "incomplete",
            ):
                errors.append(
                    "本地 SVN 状态无法安全同步: {0} ({1})".format(
                        relative_path,
                        item,
                    )
                )
            # ignored/normal/external statuses do not represent an image file
            # that should be copied by this tool.
            continue

        detail = "local status {0}".format(item)
        source_path = _join_root_relative(source_root, relative_path)
        if os.path.isdir(source_path):
            if action == "DELETE":
                _add_directory_files(
                    change_map,
                    target_root,
                    relative_path,
                    action,
                    detail,
                )
            else:
                _add_directory_files(
                    change_map,
                    source_root,
                    relative_path,
                    action,
                    detail,
                )
            continue

        _add_change(change_map, action, relative_path, detail)

    return ChangeCollection(changes=_sorted_changes(change_map), errors=errors)


def build_sync_plan(changes, source_root, target_root):
    """Compare selected files and build operations without changing files."""

    plan = SyncPlan()
    for change in changes:
        source_path = _join_root_relative(source_root, change.relative_path)
        target_path = _join_root_relative(target_root, change.relative_path)

        if change.action == "DELETE":
            if not os.path.exists(target_path) and not os.path.islink(target_path):
                plan.missing_delete_count += 1
                continue
            if os.path.isdir(target_path) and not os.path.islink(target_path):
                plan.errors.append(
                    "目标删除路径是目录，拒绝递归删除: {0}".format(
                        display_path(target_path)
                    )
                )
                continue
            plan.operations.append(
                Operation("DELETE", change.relative_path, target_path=target_path)
            )
            continue

        if (
            os.path.islink(source_path)
            or not os.path.exists(source_path)
            or not os.path.isfile(source_path)
        ):
            plan.errors.append(
                "源文件不存在或不是普通文件: {0} ({1})".format(
                    display_path(source_path),
                    change.action,
                )
            )
            continue
        if has_symlink_between(target_path, target_root):
            plan.errors.append(
                "目标路径或其父目录是符号链接，拒绝覆盖: {0}".format(
                    display_path(target_path)
                )
            )
            continue
        if os.path.isdir(target_path) and not os.path.islink(target_path):
            plan.errors.append(
                "目标路径是目录，拒绝覆盖: {0}".format(display_path(target_path))
            )
            continue

        if os.path.isfile(target_path) and sha256_file(source_path) == sha256_file(target_path):
            plan.unchanged_count += 1
            continue

        plan.operations.append(
            Operation(
                change.action,
                change.relative_path,
                source_path=source_path,
                target_path=target_path,
            )
        )

    plan.operations.sort(
        key=lambda operation: (
            0 if operation.action == "DELETE" else 1,
            normalized_relative_path(operation.relative_path),
        )
    )
    return plan


def create_log_path(log_dir):
    try:
        os.makedirs(log_dir)
    except OSError as error:
        if error.errno != errno.EEXIST or not os.path.isdir(log_dir):
            raise

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = os.path.join(log_dir, "sync_{}.log".format(timestamp))
    suffix = 1
    while os.path.exists(candidate):
        candidate = os.path.join(
            log_dir,
            "sync_{}_{}.log".format(timestamp, suffix),
        )
        suffix += 1
    return candidate


def write_log_line(log_file, line):
    log_file.write(as_unicode(line) + u"\n")
    log_file.flush()


def apply_operation(operation):
    if operation.action == "DELETE":
        if not os.path.exists(operation.target_path) and not os.path.islink(operation.target_path):
            return
        if os.path.isdir(operation.target_path) and not os.path.islink(operation.target_path):
            raise OSError("目标删除路径是目录: {0}".format(operation.target_path))
        os.remove(operation.target_path)
        return

    parent = os.path.dirname(operation.target_path)
    if parent and not os.path.isdir(parent):
        try:
            os.makedirs(parent)
        except OSError as error:
            if error.errno != errno.EEXIST or not os.path.isdir(parent):
                raise
    shutil.copy2(operation.source_path, operation.target_path)


def _new_counts():
    return {
        "ADD": 0,
        "MODIFIED": 0,
        "DELETE": 0,
        "UNCHANGED": 0,
        "ERROR": 0,
    }


def run_sync(
    source_root=SOURCE_ROOT,
    target_root=TARGET_ROOT,
    sync_dirs=SYNC_DIRS,
    mode="local",
    revision=None,
    log_dir=LOG_DIR,
    dry_run=False,
    run_svn_fn=run_svn,
):
    """Discover, plan and apply one incremental synchronization."""

    if mode not in ("local", "revision"):
        raise ValueError("不支持的同步模式: {0}".format(mode))
    source_root, target_root, sync_dirs = validate_configuration(
        source_root,
        target_root,
        sync_dirs,
    )
    if mode == "revision" and revision is None:
        raise ConfigurationError("revision 模式必须提供 --revision")

    log_path = create_log_path(log_dir)
    counts = _new_counts()

    with codecs.open(log_path, "w", encoding="utf-8") as log_file:
        write_log_line(log_file, u"cocosstudio image synchronization log")
        write_log_line(log_file, u"started: {0}".format(datetime.now().isoformat()))
        write_log_line(log_file, u"mode: {0}".format(mode))
        if mode == "revision":
            write_log_line(log_file, u"revision: {0}".format(revision))
        write_log_line(log_file, u"dry_run: {0}".format(bool(dry_run)))
        write_log_line(log_file, u"source: {0}".format(display_path(source_root)))
        write_log_line(log_file, u"target: {0}".format(display_path(target_root)))
        write_log_line(log_file, u"sync_dirs: {0}".format(", ".join(sync_dirs)))

        try:
            if mode == "revision":
                collection = collect_revision_changes(
                    source_root,
                    target_root,
                    sync_dirs,
                    revision,
                    run_svn_fn=run_svn_fn,
                )
            else:
                collection = collect_local_changes(
                    source_root,
                    target_root,
                    sync_dirs,
                    run_svn_fn=run_svn_fn,
                )
        except (ConfigurationError, OSError, SyncError, ValueError) as error:
            counts["ERROR"] += 1
            write_log_line(
                log_file,
                u"[ERROR] change discovery - {0}".format(as_unicode(error)),
            )
            write_log_line(log_file, u"status: FAILED")
            return RunResult("FAILED", EXIT_FAILURE, log_path, counts)

        for error in collection.errors:
            counts["ERROR"] += 1
            write_log_line(log_file, u"[ERROR] {0}".format(as_unicode(error)))
        if collection.errors:
            write_log_line(log_file, u"status: FAILED")
            return RunResult("FAILED", EXIT_FAILURE, log_path, counts)

        write_log_line(log_file, u"detected_changes: {0}".format(len(collection.changes)))
        for change in collection.changes:
            write_log_line(
                log_file,
                u"[DETECTED {0}] {1} ({2})".format(
                    change.action,
                    display_relative_path(change.relative_path),
                    change.detail,
                ),
            )

        try:
            plan = build_sync_plan(collection.changes, source_root, target_root)
        except (ConfigurationError, OSError) as error:
            counts["ERROR"] += 1
            write_log_line(
                log_file,
                u"[ERROR] planning - {0}".format(as_unicode(error)),
            )
            write_log_line(log_file, u"status: FAILED")
            return RunResult("FAILED", EXIT_FAILURE, log_path, counts)

        for error in plan.errors:
            counts["ERROR"] += 1
            write_log_line(
                log_file,
                u"[ERROR] planning - {0}".format(as_unicode(error)),
            )
        counts["UNCHANGED"] = plan.unchanged_count + plan.missing_delete_count
        if plan.errors:
            write_log_line(log_file, u"status: FAILED")
            return RunResult("FAILED", EXIT_FAILURE, log_path, counts)

        for operation in plan.operations:
            if dry_run:
                write_log_line(
                    log_file,
                    u"[dry-run {0}] {1}".format(
                        operation.action,
                        display_relative_path(operation.relative_path),
                    ),
                )
                counts[operation.action] += 1
                continue

            try:
                apply_operation(operation)
            except OSError as error:
                counts["ERROR"] += 1
                write_log_line(
                    log_file,
                    u"[ERROR] {0}: {1} - {2}".format(
                        operation.action,
                        display_relative_path(operation.relative_path),
                        as_unicode(error),
                    ),
                )
                continue

            counts[operation.action] += 1
            write_log_line(
                log_file,
                u"[{0}] {1}".format(
                    operation.action,
                    display_relative_path(operation.relative_path),
                ),
            )

        write_log_line(log_file, u"summary:")
        for action in ("ADD", "MODIFIED", "DELETE", "UNCHANGED", "ERROR"):
            write_log_line(log_file, u"  {0}: {1}".format(action.lower(), counts[action]))
        status = "SUCCESS" if counts["ERROR"] == 0 else "FAILED"
        write_log_line(log_file, u"status: {0}".format(status))

    return RunResult(
        status,
        EXIT_SUCCESS if counts["ERROR"] == 0 else EXIT_FAILURE,
        log_path,
        counts,
    )


def _add_common_arguments(parser):
    parser.add_argument(
        "--source",
        default=SOURCE_ROOT,
        help="源 cocosstudio 根目录，默认: {0}".format(SOURCE_ROOT),
    )
    parser.add_argument(
        "--target",
        default=TARGET_ROOT,
        help="目标 res 根目录，默认: {0}".format(TARGET_ROOT),
    )
    parser.add_argument(
        "--sync-dir",
        dest="sync_dirs",
        action="append",
        help="同步目录，可重复传入；默认: {0}".format(", ".join(SYNC_DIRS)),
    )
    parser.add_argument(
        "--log-dir",
        default=LOG_DIR,
        help="日志目录，默认: {0}".format(LOG_DIR),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示并记录操作，不修改目标文件",
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="CocosStudio 图片 SVN 增量同步工具")
    subparsers = parser.add_subparsers(dest="mode")

    revision_parser = subparsers.add_parser(
        "revision",
        help="同步指定 SVN 提交中的变更",
    )
    revision_parser.add_argument(
        "--revision",
        required=True,
        help="单个 SVN revision，例如 83672",
    )
    _add_common_arguments(revision_parser)

    local_parser = subparsers.add_parser(
        "local",
        help="同步当前 working copy 的本地变更",
    )
    _add_common_arguments(local_parser)

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not args.mode:
        parse_args(["--help"])
        return EXIT_FAILURE

    sync_dirs = args.sync_dirs or SYNC_DIRS
    try:
        result = run_sync(
            source_root=args.source,
            target_root=args.target,
            sync_dirs=sync_dirs,
            mode=args.mode,
            revision=getattr(args, "revision", None),
            log_dir=args.log_dir,
            dry_run=bool(args.dry_run),
        )
    except (ConfigurationError, OSError, ValueError) as error:
        console_print(u"同步失败: {0}".format(as_unicode(error)), stream=sys.stderr)
        return EXIT_FAILURE

    console_print(
        u"同步{0}: add={1}, modified={2}, delete={3}, unchanged={4}, errors={5}。日志: {6}".format(
            u"完成" if result.status == "SUCCESS" else u"失败",
            result.counts["ADD"],
            result.counts["MODIFIED"],
            result.counts["DELETE"],
            result.counts["UNCHANGED"],
            result.counts["ERROR"],
            display_path(result.log_path),
        )
    )
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
