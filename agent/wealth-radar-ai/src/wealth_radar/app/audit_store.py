"""原子状态/持仓/扫描快照持久化、JSONL 审计账本与多周期分资产胜率复盘器（v2.0）。"""

from __future__ import annotations

import json
import os
import statistics
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from wealth_radar.domain.errors import PersistenceError
from wealth_radar.domain.models import (
    AssetType,
    AuditRecord,
    FinalAction,
    PortfolioSnapshot,
    RadarState,
    ScanPacket,
)


def _atomic_write_json(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    except Exception as exc:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise PersistenceError(f"原子写入文件 {path} 失败: {exc}") from exc


def load_state(state_path: Path | str) -> RadarState:
    """加载 state.json；若不存在则返回初始空状态（向后兼容旧版含缓存字段的文件）。"""
    path = Path(state_path)
    if not path.exists():
        return RadarState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        # 兼容 v1.x state.json（忽略已移除的 daily_audit_cache）
        if isinstance(raw, dict):
            raw = {"index_tiers": raw.get("index_tiers", {})}
        return RadarState.model_validate(raw)
    except Exception as exc:
        raise PersistenceError(f"读取状态文件 {path} 失败: {exc}") from exc


def save_state_atomic(state_path: Path | str, state: RadarState) -> None:
    """采用同目录 .tmp + os.replace 原子写入 state.json。"""
    payload = json.dumps(state.model_dump(mode="json"), ensure_ascii=False, indent=2)
    _atomic_write_json(Path(state_path), payload)


def save_portfolio_atomic(portfolio_path: Path | str, portfolio: PortfolioSnapshot) -> None:
    """采用同目录 .tmp + os.replace 原子写入 portfolio.json。"""
    payload = json.dumps(portfolio.model_dump(mode="json"), ensure_ascii=False, indent=2)
    _atomic_write_json(Path(portfolio_path), payload)


def save_last_scan_atomic(scan_path: Path | str, packet: ScanPacket) -> None:
    """保存最近一次确定性扫描快照，供 record-audit 匹配不可篡改的 EvidenceBundle。"""
    payload = json.dumps(packet.model_dump(mode="json"), ensure_ascii=False, indent=2)
    _atomic_write_json(Path(scan_path), payload)


def load_last_scan(scan_path: Path | str) -> Optional[ScanPacket]:
    path = Path(scan_path)
    if not path.exists():
        return None
    try:
        return ScanPacket.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PersistenceError(f"读取最近扫描快照 {path} 失败: {exc}") from exc


def reset_symbol_tier_state(state_path: Path | str, symbol: str) -> bool:
    """手动重置指定主线标的的已触发档位与冷却期状态。"""
    state = load_state(state_path)
    existed = symbol in state.index_tiers
    if existed:
        state.index_tiers[symbol].triggered_tiers = []
        state.index_tiers[symbol].cooldown_until = None
        state.index_tiers[symbol].last_reset_date = date.today()
        save_state_atomic(state_path, state)
    return existed


def append_audit_records(audits_dir: Path | str, records: List[AuditRecord]) -> Optional[Path]:
    """将审计记录按 JSONL 追加写入 data/audits/YYYY-MM-DD.jsonl。"""
    if not records:
        return None
    directory = Path(audits_dir)
    directory.mkdir(parents=True, exist_ok=True)

    grouped: Dict[str, List[AuditRecord]] = {}
    for rec in records:
        day_key = rec.bundle.trade_date.isoformat()
        grouped.setdefault(day_key, []).append(rec)

    last_path: Optional[Path] = None
    try:
        for day_key, day_records in grouped.items():
            file_path = directory / f"{day_key}.jsonl"
            with file_path.open("a", encoding="utf-8") as fh:
                for rec in day_records:
                    fh.write(rec.model_dump_json() + "\n")
            last_path = file_path
    except Exception as exc:
        raise PersistenceError(f"写入审计归档失败: {exc}") from exc
    return last_path


def load_audit_records(
    audits_dir: Path | str,
    days: int = 30,
    as_of_date: Optional[date] = None,
) -> List[AuditRecord]:
    """读取最近 days 天内的所有审计记录（兼容 v1.x 与 v2.0 归档格式）。"""
    directory = Path(audits_dir)
    if not directory.exists():
        return []

    anchor = as_of_date or date.today()
    cutoff = anchor - timedelta(days=days)
    records: List[AuditRecord] = []

    for file_path in sorted(directory.glob("*.jsonl")):
        try:
            file_date = date.fromisoformat(file_path.stem)
            if file_date < cutoff or file_date > anchor:
                continue
        except ValueError:
            pass

        for line in file_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            raw = json.loads(stripped)
            # 兼容 v1.x 归档行（将 provider/model 映射为 auditor）
            if "auditor" not in raw and "provider" in raw:
                raw["auditor"] = f"{raw.get('provider')}:{raw.get('model', '')}"
            if "skill_version" not in raw and "prompt_version" in raw:
                raw["skill_version"] = str(raw["prompt_version"])
            record = AuditRecord.model_validate(raw)
            if cutoff <= record.bundle.trade_date <= anchor:
                records.append(record)

    records.sort(key=lambda r: (r.bundle.trade_date, r.run_timestamp))
    return records


class ReviewItemOutcome(BaseModel):
    trade_date: date
    asset_type: AssetType
    target_id: str
    target_name: str
    final_action: FinalAction
    hard_veto: bool
    price_at_audit: float
    latest_price: Optional[float] = None
    return_pct: Optional[float] = None


class ActionBucketStats(BaseModel):
    action: FinalAction
    total_count: int = 0
    priced_count: int = 0
    avg_return_pct: Optional[float] = None
    median_return_pct: Optional[float] = None
    win_rate_pct: Optional[float] = None
    min_return_pct: Optional[float] = None
    max_return_pct: Optional[float] = None


class AssetReviewReport(BaseModel):
    asset_type: AssetType
    buckets: Dict[FinalAction, ActionBucketStats] = Field(default_factory=dict)
    items: List[ReviewItemOutcome] = Field(default_factory=list)


def compute_review_report(
    records: List[AuditRecord],
    latest_prices: Dict[str, float],
) -> Dict[AssetType, AssetReviewReport]:
    """按 CB_CONVEX 与 INDEX_BATCH 分资产独立统计 REJECT / WATCHLIST / APPROVE_BUY 后续表现。"""
    reports: Dict[AssetType, AssetReviewReport] = {
        "CB_CONVEX": AssetReviewReport(asset_type="CB_CONVEX"),
        "INDEX_BATCH": AssetReviewReport(asset_type="INDEX_BATCH"),
    }

    grouped_returns: Dict[AssetType, Dict[FinalAction, List[float]]] = {
        "CB_CONVEX": {"REJECT": [], "WATCHLIST": [], "APPROVE_BUY": []},
        "INDEX_BATCH": {"REJECT": [], "WATCHLIST": [], "APPROVE_BUY": []},
    }
    grouped_totals: Dict[AssetType, Dict[FinalAction, int]] = {
        "CB_CONVEX": {"REJECT": 0, "WATCHLIST": 0, "APPROVE_BUY": 0},
        "INDEX_BATCH": {"REJECT": 0, "WATCHLIST": 0, "APPROVE_BUY": 0},
    }

    for rec in records:
        asset_type = rec.bundle.asset_type
        action = rec.verdict.final_action
        grouped_totals[asset_type][action] += 1

        latest = latest_prices.get(rec.bundle.target_id)
        ret_pct: Optional[float] = None
        if latest is not None and rec.price_at_audit > 0:
            ret_pct = round((latest - rec.price_at_audit) / rec.price_at_audit * 100.0, 2)
            grouped_returns[asset_type][action].append(ret_pct)

        reports[asset_type].items.append(
            ReviewItemOutcome(
                trade_date=rec.bundle.trade_date,
                asset_type=asset_type,
                target_id=rec.bundle.target_id,
                target_name=rec.bundle.target_name,
                final_action=action,
                hard_veto=rec.verdict.hard_veto,
                price_at_audit=rec.price_at_audit,
                latest_price=latest,
                return_pct=ret_pct,
            )
        )

    asset_types: tuple[AssetType, ...] = ("CB_CONVEX", "INDEX_BATCH")
    actions: tuple[FinalAction, ...] = ("REJECT", "WATCHLIST", "APPROVE_BUY")
    for asset_type in asset_types:
        for action in actions:
            rets = grouped_returns[asset_type][action]
            total = grouped_totals[asset_type][action]
            if rets:
                wins = sum(1 for r in rets if r > 0)
                stats = ActionBucketStats(
                    action=action,
                    total_count=total,
                    priced_count=len(rets),
                    avg_return_pct=round(sum(rets) / len(rets), 2),
                    median_return_pct=round(statistics.median(rets), 2),
                    win_rate_pct=round(wins / len(rets) * 100.0, 1),
                    min_return_pct=round(min(rets), 2),
                    max_return_pct=round(max(rets), 2),
                )
            else:
                stats = ActionBucketStats(action=action, total_count=total)
            reports[asset_type].buckets[action] = stats

    return reports
