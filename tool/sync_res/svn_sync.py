#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVN 资源同步工具

功能：
1) 导出指定时间段 SVN 变更（JSON）
2) 读取 JSON，将变更应用到目标目录（可选删除、支持干运行）

重要假设：
同步时“从源目录当前工作区内容拷贝”。因此源 working copy 需要已经包含
end_date 对应时间段内变更后的最终文件状态。
"""

from __future__ import unicode_literals

import argparse
import datetime
import codecs
import io
import json
import os
import shutil
import subprocess
import sys
from collections import OrderedDict
import xml.etree.ElementTree as ET


DEFAULT_SOURCE_PATH = r"D:\a2\assets\branches\dragon_ball_trunk\cocos_studio"
DEFAULT_SYNC_TARGET_PATH = r"D:\a2\assets\branches\dragon_ball_abroad_trunk\cocos_studio"

# Python2：用这个统一判断“unicode 字符串”
try:
    unicode_type = unicode
except NameError:
    unicode_type = str

# Python2 在某些环境下 sys.stdout/sys.stderr 编码可能是 ascii，
# 导致 argparse 输出中文 help 时抛 UnicodeEncodeError。
try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)
except Exception:
    pass


def _parse_ymd(s):
    # 只接受 YYYY-MM-DD，避免歧义
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def _format_utc_datetime(s):
    """
    svn log --xml 的 date 通常类似：
    2026-03-20T14:30:00.123456Z 或 2026-03-20T14:30:00Z
    """
    if not s:
        return ""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1]

    fmts = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]
    dt = None
    for fmt in fmts:
        try:
            dt = datetime.datetime.strptime(s, fmt)
            break
        except ValueError:
            pass
    if dt is None:
        return s
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _normalize_rel_path(rel_path, source_root_path):
    """
    将 svn log 里的路径规范成“相对路径”（去掉可能出现的源目录名等前缀）。
    """
    if not rel_path:
        return ""
    rel_path = rel_path.replace("\\", "/").lstrip("/")

    source_base = os.path.basename(source_root_path.rstrip("/\\"))
    parts = rel_path.split("/")
    if source_base and source_base in parts:
        idx = parts.index(source_base)
        rel_path = "/".join(parts[idx + 1 :])
    return rel_path


def _join_root_rel(root, rel):
    rel = rel.replace("/", os.sep).replace("\\", os.sep)
    return os.path.join(root, rel)


def _strip_root_prefix_overlap(root, rel_path):
    """
    当 target_root 本身已经是某个目录（如 cocos_studio），而 rel_path 又以该目录名开头时，
    会导致拼接重复：target_root/cocos_studio/... -> target_root/cocos_studio/cocos_studio/...
    这里自动去掉重复前缀，避免重复目录层级。
    """
    rel = str(rel_path or "").replace("\\", "/").lstrip("/")
    if not rel:
        return rel
    root_base = os.path.basename(str(root or "").rstrip("/\\")).lower()
    if not root_base:
        return rel
    rel_lower = rel.lower()
    prefix = root_base + "/"
    if rel_lower.startswith(prefix):
        return rel[len(prefix) :]
    return rel


def _run_svn(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if out is None:
        out = b""
    if err is None:
        err = b""

    try:
        out_text = out.decode("utf-8", "replace")
    except Exception:
        out_text = out

    try:
        err_text = err.decode("utf-8", "replace")
    except Exception:
        err_text = err

    if proc.returncode != 0:
        raise RuntimeError(
            "svn 命令执行失败。\n"
            "命令: {0}\n退出码: {1}\nstderr: {2}".format(cmd, proc.returncode, err_text.strip())
        )

    return out_text


class SvnSyncTool(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def export_log(self, start_date, end_date, output_json):
        _parse_ymd(start_date)
        _parse_ymd(end_date)

        # svn 支持用 {YYYY-MM-DD}:{YYYY-MM-DD} 做 revision range
        rev_range = "{{{0}}}:{{{1}}}".format(start_date, end_date)
        # -v 会让 xml 里包含 paths/path（对应文件级变更），否则可能只剩提交信息
        cmd = ["svn", "log", "--xml", "-v", "-r", rev_range, self.source_path]
        xml_text = _run_svn(cmd)

        # Python2 + ElementTree 在某些环境下会把 unicode 错当 ascii，
        # 这里强制以 UTF-8 bytes 解析，避免 UnicodeEncodeError。
        if isinstance(xml_text, unicode_type):
            xml_bytes = xml_text.encode("utf-8")
        else:
            xml_bytes = xml_text
        root = ET.fromstring(xml_bytes)
        logentries = root.findall(".//logentry")

        # 按文件聚合：file_path -> history(按 revision 之后再排序)
        file_histories = {}

        for entry in logentries:
            rev_str = entry.attrib.get("revision", "")
            try:
                revision = int(rev_str) if rev_str else -1
            except ValueError:
                revision = -1

            author = (entry.findtext("author") or "").strip()
            date_raw = entry.findtext("date") or ""
            date = _format_utc_datetime(date_raw)
            msg = entry.findtext("msg") or ""
            msg = msg.strip("\n")

            for p in entry.findall(".//paths/path"):
                action = (p.attrib.get("action") or "").strip().upper()
                if action not in ("A", "M", "D"):
                    continue

                rel = _normalize_rel_path(p.text or "", self.source_path)
                if not rel:
                    continue

                event = {
                    "revision": revision,
                    "date": date,
                    "author": author,
                    "action": action,
                    "message": msg,
                }
                if rel not in file_histories:
                    file_histories[rel] = []
                file_histories[rel].append(event)

        added_list = []
        modified_list = []
        deleted_list = []

        for file_path, history in file_histories.items():
            # 以时间顺序确定首次/末次 action
            history_sorted = sorted(
                history,
                key=lambda e: (e.get("revision", -1), e.get("date", ""), e.get("action", ""), e.get("message", "")),
            )
            if not history_sorted:
                continue

            first_action = (history_sorted[0].get("action") or "").strip().upper()
            last_action = (history_sorted[-1].get("action") or "").strip().upper()

            if last_action == "D":
                deleted_list.append(
                    {
                        "file_path": file_path,
                        "final_state": "deleted",
                        "history": history_sorted,
                    }
                )
            elif first_action == "A":
                added_list.append(
                    {
                        "file_path": file_path,
                        "final_state": "added",
                        "history": history_sorted,
                    }
                )
            elif first_action == "M":
                modified_list.append(
                    {
                        "file_path": file_path,
                        "final_state": "modified",
                        "history": history_sorted,
                    }
                )
            else:
                # 兜底：如果首次不是 A/M，按末次归类（避免丢失）
                if last_action == "A":
                    added_list.append(
                        {
                            "file_path": file_path,
                            "final_state": "added",
                            "history": history_sorted,
                        }
                    )
                else:
                    modified_list.append(
                        {
                            "file_path": file_path,
                            "final_state": "modified",
                            "history": history_sorted,
                        }
                    )

        def _file_ext_sort_key(file_path):
            # 扩展名：取最后一个 '.' 后的部分；没有扩展名则为空
            p = str(file_path).replace("\\", "/")
            base = p.rsplit("/", 1)[-1]
            dot = base.rfind(".")
            if 0 < dot < (len(base) - 1):
                ext = base[dot + 1 :].lower()
            else:
                ext = ""
            # 同扩展名按字母序（按完整 file_path）
            return (ext, p)

        added_files_sorted = sorted(
            [item.get("file_path", "") for item in added_list],
            key=_file_ext_sort_key,
        )
        modified_files_sorted = sorted(
            [item.get("file_path", "") for item in modified_list],
            key=_file_ext_sort_key,
        )
        deleted_files_sorted = sorted(
            [item.get("file_path", "") for item in deleted_list],
            key=_file_ext_sort_key,
        )

        payload = OrderedDict()
        payload["query_range"] = {
            "start_date": start_date,
            "end_date": end_date,
            "source_path": self.source_path,
        }
        payload["summary"] = {
            "total_files": len(file_histories),
            "files_added": len(added_list),
            "files_modified": len(modified_list),
            "files_deleted": len(deleted_list),
        }
        payload["summary"]["file_state_overview"] = {
            "added": added_files_sorted,
            "modified": modified_files_sorted,
            "deleted": deleted_files_sorted,
        }
        payload["added"] = added_list
        payload["modified"] = modified_list
        payload["deleted"] = deleted_list

        # Python2：避免 json.dump 在 TextIO 下写入 bytes 导致 TypeError
        json_text = json.dumps(payload, ensure_ascii=False, indent=2)
        # 若输出路径带目录（如 logs/xxx.json），自动创建目录
        out_dir = os.path.dirname(output_json)
        if out_dir and (not os.path.exists(out_dir)):
            os.makedirs(out_dir)
        with io.open(output_json, "wb") as f:
            if isinstance(json_text, unicode_type):
                f.write(json_text.encode("utf-8"))
            else:
                f.write(json_text)
        return payload

    def sync_from_json(
        self,
        input_json,
        target_path,
        dry_run=False,
        sync_delete=False,
        source_override=None,
        copy_added_csd=False,
    ):
        with io.open(input_json, "r", encoding="utf-8") as f:
            payload = json.load(f)

        source_path = source_override or payload.get("query_range", {}).get("source_path", self.source_path)
        # 新版：按文件组织（added/modified/deleted）
        added_list = payload.get("added", None)
        modified_list = payload.get("modified", None)
        deleted_list = payload.get("deleted", None)

        if not os.path.exists(target_path):
            if dry_run:
                print("[dry-run] 目标目录不存在，将创建: {0}".format(target_path))
            else:
                os.makedirs(target_path)

        if added_list is not None and modified_list is not None and deleted_list is not None:
            added_list = added_list or []
            modified_list = modified_list or []
            deleted_list = deleted_list or []

            # 新增的 .csd 默认不拷贝（可通过 --copy-added-csd 开启）
            if copy_added_csd:
                added_filtered = added_list
            else:
                added_filtered = []
                for item in added_list:
                    fp = str(item.get("file_path", "")).lower()
                    if fp.endswith(".csd"):
                        continue
                    added_filtered.append(item)

            to_copy = added_filtered + modified_list
            total_copy = len(to_copy)
            for idx, item in enumerate(to_copy):
                file_path = str(item.get("file_path", "")).replace("\\", "/").lstrip("/")
                final_state = str(item.get("final_state", "")).strip().lower()

                src = _join_root_rel(source_path, file_path)
                dst_rel = _strip_root_prefix_overlap(target_path, file_path)
                dst = _join_root_rel(target_path, dst_rel)

                if dry_run:
                    print(
                        "[dry-run] ({0}/{1}) COPY {2} (final_state={3})".format(
                            idx + 1, total_copy, file_path, final_state
                        )
                    )
                    continue

                dst_dir = os.path.dirname(dst)
                if dst_dir and (not os.path.exists(dst_dir)):
                    os.makedirs(dst_dir)

                if not os.path.exists(src):
                    print("[warn] 源文件不存在，跳过: {0} (final_state={1})".format(src, final_state))
                    continue

                # SVN 日志在 --verbose(-v) 下可能也会输出“目录项”（如 cocosstudio/.../ticket_discount），
                # 此时不要用 copy2 当成文件拷贝，改为只创建目录结构即可。
                if os.path.isdir(src):
                    if dry_run:
                        print("[dry-run] ({0}/{1}) MKDIR {2}".format(idx + 1, total_copy, dst))
                    else:
                        if not os.path.exists(dst):
                            os.makedirs(dst)
                    continue

                shutil.copy2(src, dst)

            if not sync_delete:
                # 只提示，不实际删除
                for item in deleted_list:
                    file_path = str(item.get("file_path", "")).replace("\\", "/").lstrip("/")
                    print("[skip] deleted 不同步删除（需要加 --sync-delete）: {0}".format(file_path))
                return

            total_del = len(deleted_list)
            for idx, item in enumerate(deleted_list):
                file_path = str(item.get("file_path", "")).replace("\\", "/").lstrip("/")
                src = None
                dst_rel = _strip_root_prefix_overlap(target_path, file_path)
                dst = _join_root_rel(target_path, dst_rel)
                if dry_run:
                    print("[dry-run] ({0}/{1}) DELETE {2}".format(idx + 1, total_del, file_path))
                    continue

                if not os.path.exists(dst):
                    continue
                if os.path.isfile(dst) or os.path.islink(dst):
                    os.remove(dst)
                elif os.path.isdir(dst):
                    shutil.rmtree(dst)
            return

        # 兼容旧版格式：按 changes（A/M/D）逐条执行
        changes = payload.get("changes", [])

        def _rev(c):
            try:
                return int(c.get("revision", -1))
            except Exception:
                return -1

        changes_sorted = sorted(changes, key=lambda c: (_rev(c), str(c.get("file_path", ""))))
        total = len(changes_sorted)
        for idx, c in enumerate(changes_sorted):
            file_path = str(c.get("file_path", "")).replace("\\", "/").lstrip("/")
            change_type = str(c.get("change_type", "")).strip().upper()
            revision = c.get("revision", "")
            author = c.get("author", "")
            date = c.get("date", "")

            src = _join_root_rel(source_path, file_path)
            dst = _join_root_rel(target_path, file_path)

            if change_type in ("A", "M"):
                if dry_run:
                    print(
                        "[dry-run] ({0}/{1}) COPY {2} ({3}) rev={4} author={5} date={6}".format(
                            idx + 1, total, file_path, change_type, revision, author, date
                        )
                    )
                    continue

                dst_dir = os.path.dirname(dst)
                if dst_dir and (not os.path.exists(dst_dir)):
                    os.makedirs(dst_dir)

                if not os.path.exists(src):
                    print("[warn] 源文件不存在，跳过: {0} (来自 {1} rev={2})".format(src, file_path, revision))
                    continue

                shutil.copy2(src, dst)
                continue

            if change_type == "D":
                if not sync_delete:
                    print("[skip] D 不同步删除（需要加 --sync-delete）: {0} rev={1}".format(file_path, revision))
                    continue

                if dry_run:
                    print(
                        "[dry-run] ({0}/{1}) DELETE {2} rev={3} author={4} date={5}".format(
                            idx + 1, total, file_path, revision, author, date
                        )
                    )
                    continue

                if not os.path.exists(dst):
                    continue

                if os.path.isfile(dst) or os.path.islink(dst):
                    os.remove(dst)
                elif os.path.isdir(dst):
                    shutil.rmtree(dst)
                continue

            print("[skip] 未识别变更类型，跳过: {0} type={1} rev={2}".format(file_path, change_type, revision))


def main(argv=None):
    parser = argparse.ArgumentParser(description="SVN 变更导出与文件同步工具（按日期范围）")
    sub = parser.add_subparsers(dest="cmd")

    p_log = sub.add_parser("log", help="导出指定时间段 SVN 变更 JSON")
    p_log.add_argument("--start", required=True, help="起始日期 YYYY-MM-DD")
    p_log.add_argument("--end", required=True, help="结束日期 YYYY-MM-DD")
    p_log.add_argument(
        "--source",
        default=DEFAULT_SOURCE_PATH,
        help="源工程路径（SVN working copy 或本地可访问路径）。默认: {0}".format(DEFAULT_SOURCE_PATH),
    )
    p_log.add_argument("--output", required=True, help="输出 JSON 文件路径")

    p_sync = sub.add_parser("sync", help="读取 JSON 并同步到目标目录")
    p_sync.add_argument("--input", required=True, help="输入 changes.json 路径")
    p_sync.add_argument(
        "--target",
        required=False,
        default=DEFAULT_SYNC_TARGET_PATH,
        help="目标工程目录（可覆盖代码配置）。默认: {0}".format(DEFAULT_SYNC_TARGET_PATH),
    )
    p_sync.add_argument("--source", default=None, help="覆盖 JSON 里的 source_path（可选）")
    p_sync.add_argument("--sync-delete", action="store_true", help="包含删除操作（默认不删除）")
    p_sync.add_argument("--dry-run", action="store_true", help="干运行：只输出将执行的操作，不实际写文件")
    p_sync.add_argument(
        "--copy-added-csd",
        action="store_true",
        help="拷贝新增的 .csd 文件（默认不拷贝新增的 .csd）",
    )

    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1

    if args.cmd == "log":
        tool = SvnSyncTool(args.source)
        tool.export_log(start_date=args.start, end_date=args.end, output_json=args.output)
        print("导出完成: {0}".format(args.output))
        return 0

    if args.cmd == "sync":
        tool = SvnSyncTool(args.source or DEFAULT_SOURCE_PATH)
        tool.sync_from_json(
            input_json=args.input,
            target_path=args.target,
            dry_run=bool(args.dry_run),
            sync_delete=bool(args.sync_delete),
            source_override=args.source,
            copy_added_csd=bool(args.copy_added_csd),
        )
        print("同步处理完成")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVN 资源同步工具

1) 导出指定时间段 SVN 变更（JSON）
2) 读取 JSON，将变更应用到目标目录（可选删除、支持干运行）

说明（重要）：
同步时是“以源目录当前工作区内容为准”拷贝文件，因此要求源 working copy
已经包含了 end_date 对应时间段内的最终文件状态。
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


DEFAULT_SOURCE_PATH = r"D:\a2\assets\branches\dragon_ball_release_26_02_11"


def _parse_ymd(s):
    # 只接受 YYYY-MM-DD，避免歧义
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def _format_utc_datetime(s):
    """
    svn log --xml 的 date 通常类似：
    2026-03-20T14:30:00.123456Z 或 2026-03-20T14:30:00Z
    """
    if not s:
        return ""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1]
    # 先尝试带微秒，再尝试不带微秒
    fmts = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]
    dt = None
    for fmt in fmts:
        try:
            dt = datetime.datetime.strptime(s, fmt)
            break
        except ValueError:
            pass
    if dt is None:
        # 兜底：不保证可解析
        return s
    # 假设 svn 输出是 UTC（因为我们去掉了 Z）
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _normalize_rel_path(rel_path, source_root_path):
    """
    将 svn log 里的路径规范成“相对路径”（去掉可能出现的源目录名等前缀）。
    """
    if not rel_path:
        return ""
    rel_path = rel_path.replace("\\", "/").lstrip("/")

    source_base = os.path.basename(source_root_path.rstrip("/\\"))
    parts = rel_path.split("/")
    if source_base and source_base in parts:
        idx = parts.index(source_base)
        rel_path = "/".join(parts[idx + 1 :])
    return rel_path


def _join_root_rel(root, rel):
    rel = rel.replace("/", os.sep).replace("\\", os.sep)
    return os.path.join(root, rel)


def _run_svn(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    # Python 2：stdout/stderr 是 bytes，尝试按 UTF-8 解码
    if out is None:
        out = b""
    if err is None:
        err = b""
    try:
        out_text = out.decode("utf-8", "replace")
    except Exception:
        out_text = out
    try:
        err_text = err.decode("utf-8", "replace")
    except Exception:
        err_text = err

    if proc.returncode != 0:
        raise RuntimeError(
            "svn 命令执行失败。\n"
            "命令: {0}\n退出码: {1}\nstderr: {2}".format(cmd, proc.returncode, err_text.strip())
        )
    return out_text


class SvnSyncTool(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def export_log(self, start_date, end_date, output_json):
        _parse_ymd(start_date)
        _parse_ymd(end_date)

        # svn 支持用 {YYYY-MM-DD}:{YYYY-MM-DD} 做 revision range
        rev_range = "{{{0}}}:{{{1}}}".format(start_date, end_date)
        cmd = ["svn", "log", "--xml", "-r", rev_range, self.source_path]
        xml_text = _run_svn(cmd)

        root = ET.fromstring(xml_text)
        logentries = root.findall(".//logentry")

        changes = []
        files_added = 0
        files_modified = 0
        files_deleted = 0

        for entry in logentries:
            rev_str = entry.attrib.get("revision", "")
            try:
                revision = int(rev_str) if rev_str else -1
            except ValueError:
                revision = -1

            author = (entry.findtext("author") or "").strip()
            date_raw = entry.findtext("date") or ""
            date = _format_utc_datetime(date_raw)
            msg = entry.findtext("msg") or ""
            msg = msg.strip("\n")

            for p in entry.findall(".//paths/path"):
                action = (p.attrib.get("action") or "").strip().upper()
                if action not in ("A", "M", "D"):
                    continue

                rel = _normalize_rel_path(p.text or "", self.source_path)
                if not rel:
                    continue

                changes.append(
                    {
                        "file_path": rel,
                        "change_type": action,
                        "revision": revision,
                        "author": author,
                        "date": date,
                        "message": msg,
                    }
                )

                if action == "A":
                    files_added += 1
                elif action == "M":
                    files_modified += 1
                elif action == "D":
                    files_deleted += 1

        payload = {
            "query_range": {
                "start_date": start_date,
                "end_date": end_date,
                "source_path": self.source_path,
            },
            "summary": {
                "total_commits": len(logentries),
                "files_added": files_added,
                "files_modified": files_modified,
                "files_deleted": files_deleted,
            },
            "changes": changes,
        }

        with open(output_json, "w") as f:
            # indent 在 python2 json 库里可用
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload

    def sync_from_json(self, input_json, target_path, dry_run=False, sync_delete=False, source_override=None):
        with open(input_json, "r") as f:
            payload = json.load(f)

        source_path = source_override
        if not source_path:
            source_path = payload.get("query_range", {}).get("source_path", self.source_path)

        changes = payload.get("changes", [])

        def _rev(c):
            try:
                return int(c.get("revision", -1))
            except Exception:
                return -1

        # 为了把最终状态落到目标：按 revision 升序执行（svn log 常见新->旧）
        changes_sorted = sorted(changes, key=lambda c: (_rev(c), str(c.get("file_path", ""))))

        if not os.path.exists(target_path):
            if dry_run:
                print("[dry-run] 目标目录不存在，将创建: {0}".format(target_path))
            else:
                os.makedirs(target_path)

        total = len(changes_sorted)
        for idx, c in enumerate(changes_sorted):
            file_path = str(c.get("file_path", "")).replace("\\", "/").lstrip("/")
            change_type = str(c.get("change_type", "")).strip().upper()
            revision = c.get("revision", "")
            author = c.get("author", "")
            date = c.get("date", "")

            src = _join_root_rel(source_path, file_path)
            dst = _join_root_rel(target_path, file_path)

            if change_type in ("A", "M"):
                if dry_run:
                    print(
                        "[dry-run] ({0}/{1}) COPY {2} ({3}) rev={4} author={5} date={6}".format(
                            idx + 1, total, file_path, change_type, revision, author, date
                        )
                    )
                    continue

                dst_dir = os.path.dirname(dst)
                if dst_dir and (not os.path.exists(dst_dir)):
                    os.makedirs(dst_dir)

                if not os.path.exists(src):
                    print("[warn] 源文件不存在，跳过: {0} (来自 {1} rev={2})".format(src, file_path, revision))
                    continue

                shutil.copy2(src, dst)
                continue

            if change_type == "D":
                if not sync_delete:
                    print("[skip] D 不同步删除（需要加 --sync-delete）: {0} rev={1}".format(file_path, revision))
                    continue

                if dry_run:
                    print(
                        "[dry-run] ({0}/{1}) DELETE {2} rev={3} author={4} date={5}".format(
                            idx + 1, total, file_path, revision, author, date
                        )
                    )
                    continue

                if not os.path.exists(dst):
                    continue

                # dst 可能是文件或目录（更稳一点）
                if os.path.isfile(dst) or os.path.islink(dst):
                    os.remove(dst)
                elif os.path.isdir(dst):
                    shutil.rmtree(dst)
                continue

            print("[skip] 未识别变更类型，跳过: {0} type={1} rev={2}".format(file_path, change_type, revision))


def main(argv=None):
    parser = argparse.ArgumentParser(description="SVN 变更导出与文件同步工具（按日期范围）")
    sub = parser.add_subparsers(dest="cmd")

    p_log = sub.add_parser("log", help="导出指定时间段 SVN 变更 JSON")
    p_log.add_argument("--start", required=True, help="起始日期 YYYY-MM-DD")
    p_log.add_argument("--end", required=True, help="结束日期 YYYY-MM-DD")
    p_log.add_argument(
        "--source",
        default=DEFAULT_SOURCE_PATH,
        help="源工程路径（SVN working copy 或可访问路径 URL 对应的本地可解析路径）。默认: {0}".format(DEFAULT_SOURCE_PATH),
    )
    p_log.add_argument("--output", required=True, help="输出 JSON 文件路径")

    p_sync = sub.add_parser("sync", help="读取 JSON 并同步到目标目录")
    p_sync.add_argument("--input", required=True, help="输入 changes.json 路径")
    p_sync.add_argument("--target", required=True, help="目标工程根目录")
    p_sync.add_argument("--source", default=None, help="覆盖 JSON 里的 source_path（可选）")
    p_sync.add_argument("--sync-delete", action="store_true", help="包含删除操作（默认不删除）")
    p_sync.add_argument("--dry-run", action="store_true", help="干运行：只输出将执行的操作，不实际写文件")

    args = parser.parse_args(argv)

    if args.cmd == "log":
        tool = SvnSyncTool(args.source)
        tool.export_log(start_date=args.start, end_date=args.end, output_json=args.output)
        print("导出完成: {0}".format(args.output))
        return 0

    if args.cmd == "sync":
        tool = SvnSyncTool(args.source or DEFAULT_SOURCE_PATH)
        tool.sync_from_json(
            input_json=args.input,
            target_path=args.target,
            dry_run=bool(args.dry_run),
            sync_delete=bool(args.sync_delete),
            source_override=args.source,
        )
        print("同步处理完成")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

'''__PYTHON3_REMNANT_START__
# -*- coding: utf-8 -*-
"""
SVN 资源同步工具

用途：
1) 导出指定时间段内 SVN 变更（JSON）
2) 读取 JSON，将变更应用到目标目录（可选删除、支持干运行）
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


DEFAULT_SOURCE_PATH = r"D:\a2\assets\branches\dragon_ball_release_26_02_11"


def _parse_ymd(s: str) -> _dt.date:
    # 只接受 YYYY-MM-DD，避免歧义
    return _dt.datetime.strptime(s, "%Y-%m-%d").date()


def _format_utc_datetime(s: str) -> str:
    """
    svn log --xml 的 date 通常类似：
    2026-03-20T14:30:00.123456Z 或 2026-03-20T14:30:00Z
    """
    if not s:
        return ""
    s = s.strip()
    # 兼容尾部 Z
    if s.endswith("Z"):
        s2 = s[:-1] + "+00:00"
    else:
        s2 = s
    dt = _dt.datetime.fromisoformat(s2)
    dt_utc = dt.astimezone(_dt.timezone.utc)
    return dt_utc.strftime("%Y-%m-%d %H:%M:%S")


def _normalize_rel_path(rel_path: str, source_root_path: str) -> str:
    """
    将 svn log 里的路径规范成“相对路径”（去掉可能出现的源目录名等前缀）。
    """
    if not rel_path:
        return ""
    rel_path = rel_path.replace("\\", "/").lstrip("/")

    # 若 svn log 输出的是含有根目录名的路径，则去掉
    source_base = os.path.basename(source_root_path.rstrip("/\\"))
    if source_base and source_base in rel_path.split("/"):
        parts = rel_path.split("/")
        idx = parts.index(source_base)
        rel_path = "/".join(parts[idx + 1 :])
    return rel_path


def _join_root_rel(root: str, rel: str) -> str:
    # rel 可能含有 /，统一转成 OS 分隔符
    rel = rel.replace("/", os.sep).replace("\\", os.sep)
    return os.path.join(root, rel)


def _run_subprocess(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "svn 命令执行失败。\n"
            f"命令: {cmd}\n"
            f"退出码: {proc.returncode}\n"
            f"stderr: {proc.stderr.strip()}"
        )
    return proc


@dataclass(frozen=True)
class Change:
    file_path: str  # 相对路径
    change_type: str  # A/M/D
    revision: int
    author: str
    date: str  # "YYYY-MM-DD HH:MM:SS"
    message: str

    def to_json_obj(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
            "revision": self.revision,
            "author": self.author,
            "date": self.date,
            "message": self.message,
        }


class SvnSyncTool:
    def __init__(self, source_path: str) -> None:
        self.source_path = source_path

    def export_log(
        self, start_date: str, end_date: str, output_json: str
    ) -> Dict[str, Any]:
        # 生成 svn log XML
        _parse_ymd(start_date)
        _parse_ymd(end_date)

        # svn 支持用 {YYYY-MM-DD}:{YYYY-MM-DD} 做 revision range
        rev_range = f"{{{start_date}}}:{{{end_date}}}"
        cmd = [
            "svn",
            "log",
            "--xml",
            "-r",
            rev_range,
            self.source_path,
        ]
        proc = _run_subprocess(cmd)

        root = ET.fromstring(proc.stdout)
        logentries = root.findall(".//logentry")

        changes: List[Change] = []
        files_added = 0
        files_modified = 0
        files_deleted = 0

        for entry in logentries:
            rev_str = entry.attrib.get("revision", "")
            try:
                revision = int(rev_str) if rev_str else -1
            except ValueError:
                revision = -1

            author = (entry.findtext("author") or "").strip()
            date_raw = entry.findtext("date") or ""
            date = _format_utc_datetime(date_raw)
            msg = entry.findtext("msg") or ""
            msg = msg.strip("\n")

            # action 可能是 A/M/D/..，这里只取题目要求的 A/M/D
            for p in entry.findall(".//paths/path"):
                action = (p.attrib.get("action") or "").strip().upper()
                if action not in {"A", "M", "D"}:
                    continue
                rel = _normalize_rel_path(p.text or "", self.source_path)
                if not rel:
                    continue

                change = Change(
                    file_path=rel,
                    change_type=action,
                    revision=revision,
                    author=author,
                    date=date,
                    message=msg,
                )
                changes.append(change)

                if action == "A":
                    files_added += 1
                elif action == "M":
                    files_modified += 1
                elif action == "D":
                    files_deleted += 1

        summary = {
            "total_commits": len(logentries),
            "files_added": files_added,
            "files_modified": files_modified,
            "files_deleted": files_deleted,
        }

        payload: Dict[str, Any] = {
            "query_range": {
                "start_date": start_date,
                "end_date": end_date,
                "source_path": self.source_path,
            },
            "summary": summary,
            "changes": [c.to_json_obj() for c in changes],
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload

    def sync_from_json(
        self,
        input_json: str,
        target_path: str,
        dry_run: bool = False,
        sync_delete: bool = False,
        source_override: Optional[str] = None,
    ) -> None:
        with open(input_json, "r", encoding="utf-8") as f:
            payload = json.load(f)

        source_path = source_override or payload.get("query_range", {}).get(
            "source_path", self.source_path
        )
        changes = payload.get("changes", [])

        # svn log 输出常见为新->旧；为了“把最终状态落到目标”，这里按 revision 升序执行
        def _rev(c: Dict[str, Any]) -> int:
            try:
                return int(c.get("revision", -1))
            except (TypeError, ValueError):
                return -1

        changes_sorted = sorted(
            changes, key=lambda c: (_rev(c), str(c.get("file_path", "")))
        )

        if not os.path.exists(target_path):
            if dry_run:
                print(f"[dry-run] 目标目录不存在，将创建: {target_path}")
            else:
                os.makedirs(target_path, exist_ok=True)

        for idx, c in enumerate(changes_sorted):
            file_path = str(c.get("file_path", "")).replace("\\", "/").lstrip("/")
            change_type = str(c.get("change_type", "")).strip().upper()
            revision = c.get("revision", "")
            author = c.get("author", "")
            date = c.get("date", "")

            src = _join_root_rel(source_path, file_path)
            dst = _join_root_rel(target_path, file_path)

            # A/M：复制文件
            if change_type in {"A", "M"}:
                if dry_run:
                    print(
                        f"[dry-run] ({idx+1}/{len(changes_sorted)}) "
                        f"COPY {file_path} ({change_type}) rev={revision} author={author} date={date}"
                    )
                    continue

                dst_dir = os.path.dirname(dst)
                if dst_dir and not os.path.exists(dst_dir):
                    os.makedirs(dst_dir, exist_ok=True)

                if not os.path.exists(src):
                    # 假设源目录是最新状态；如果缺失，说明本地工作区不包含该变更后的文件
                    print(
                        f"[warn] 源文件不存在，跳过: {src} (来自 {file_path} rev={revision})"
                    )
                    continue

                shutil.copy2(src, dst)
                continue

            # D：删除目标文件（可选）
            if change_type == "D":
                if not sync_delete:
                    print(
                        f"[skip] D 不同步删除（需要加 --sync-delete）: {file_path} rev={revision}"
                    )
                    continue

                if dry_run:
                    print(
                        f"[dry-run] ({idx+1}/{len(changes_sorted)}) "
                        f"DELETE {file_path} rev={revision} author={author} date={date}"
                    )
                    continue

                if not os.path.exists(dst):
                    continue

                # 允许 dst 是文件或目录（更稳一点）
                if os.path.isfile(dst) or os.path.islink(dst):
                    os.remove(dst)
                elif os.path.isdir(dst):
                    shutil.rmtree(dst)
                continue

            print(
                f"[skip] 未识别变更类型，跳过: {file_path} type={change_type} rev={revision}"
            )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="SVN 变更导出与文件同步工具（按日期范围）"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="导出指定时间段 SVN 变更 JSON")
    p_log.add_argument("--start", required=True, help="起始日期 YYYY-MM-DD")
    p_log.add_argument("--end", required=True, help="结束日期 YYYY-MM-DD")
    p_log.add_argument(
        "--source",
        default=DEFAULT_SOURCE_PATH,
        help=f"源工程路径（SVN working copy 或 URL 本地可访问路径）。默认: {DEFAULT_SOURCE_PATH}",
    )
    p_log.add_argument("--output", required=True, help="输出 JSON 文件路径")

    p_sync = sub.add_parser("sync", help="读取 JSON 并同步到目标目录")
    p_sync.add_argument("--input", required=True, help="输入 changes.json 路径")
    p_sync.add_argument("--target", required=True, help="目标工程根目录")
    p_sync.add_argument(
        "--source",
        default=None,
        help="覆盖 JSON 里的 source_path（可选）",
    )
    p_sync.add_argument(
        "--sync-delete",
        action="store_true",
        help="包含删除操作（默认不删除）",
    )
    p_sync.add_argument(
        "--dry-run",
        action="store_true",
        help="干运行：只输出将执行的操作，不实际写文件",
    )

    args = parser.parse_args(argv)

    if args.cmd == "log":
        tool = SvnSyncTool(args.source)
        tool.export_log(start_date=args.start, end_date=args.end, output_json=args.output)
        print(f"导出完成: {args.output}")
        return 0

    if args.cmd == "sync":
        tool = SvnSyncTool(source_path=args.source or DEFAULT_SOURCE_PATH)
        tool.sync_from_json(
            input_json=args.input,
            target_path=args.target,
            dry_run=bool(args.dry_run),
            sync_delete=bool(args.sync_delete),
            source_override=args.source,
        )
        print("同步处理完成")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

