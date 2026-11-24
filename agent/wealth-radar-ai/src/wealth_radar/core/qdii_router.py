"""Stage 1: QDII 平替智能路由器（物理防老鼠仓、风格漂移校验、相关性评分、限额拆单与 ETF 溢价守卫）。"""

from __future__ import annotations

import math
import re
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from wealth_radar.config.loader import QDIIRouterConfig
from wealth_radar.domain.models import (
    ETFSpotPremium,
    HoldingRegion,
    PriceBar,
    QDIIHoldingItem,
    QDIIProxyEvaluation,
    QDIIPurchaseInfo,
    QDIIRoutePlan,
    QDIISplitAllocation,
)

# 全球/美股核心大盘科技与半导体龙头（单只市值千亿~数万亿美元，不存在国内私募/公募坐庄老鼠仓物理基础）
US_MEGA_CAP_TECH_TICKERS: frozenset[str] = frozenset(
    {
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "META",
        "GOOG",
        "GOOGL",
        "AVGO",
        "TSLA",
        "NFLX",
        "AMD",
        "ASML",
        "TSM",
        "COST",
        "QCOM",
        "INTC",
        "MU",
        "LRCX",
        "AMAT",
        "TXN",
        "ADBE",
        "CRM",
        "ORCL",
        "CSCO",
        "PLTR",
        "ARM",
        "PANW",
        "KLAC",
        "SNPS",
        "CDNS",
        "ANET",
        "APP",
        "NOW",
        "CRWD",
        "INTU",
        "ISRG",
        "BKNG",
        "ADI",
        "MRVL",
        "UBER",
        "SHOP",
        "SPOT",
        "GLW",
        "SNDK",
        "TER",
    }
)

_NON_CN_INTL_NAME_HINTS = ("三星", "海力士", "SK海力士", "台积电", "阿斯麦", "索尼", "丰田", "东京电子", "爱德万")
_US_TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,6}$")
_HK_CODE_PATTERN = re.compile(r"^\d{5}$")
_CN_A_CODE_PATTERN = re.compile(r"^\d{6}$")


def classify_stock_holding(stock_code: str, stock_name: str) -> Tuple[HoldingRegion, bool]:
    """判定季报单只重仓股所属市场区域与是否为美股/全球大盘科技龙头。"""
    code = stock_code.strip().upper()
    name = stock_name.strip()

    if any(hint in name for hint in _NON_CN_INTL_NAME_HINTS):
        return "US_DEVELOPED", True

    if _US_TICKER_PATTERN.match(code):
        base_ticker = code.split(".")[0]
        return "US_DEVELOPED", base_ticker in US_MEGA_CAP_TECH_TICKERS

    if _HK_CODE_PATTERN.match(code):
        return "HK", False

    if _CN_A_CODE_PATTERN.match(code):
        return "CN_A", False

    return "OTHER", False


def analyze_holdings_purity(
    holdings: Sequence[QDIIHoldingItem],
) -> Tuple[Optional[float], Optional[float], int, str]:
    """计算最新一季前十大重仓中的美股/发达市场纯度(%)、A+港股占比(%)与美股大盘科技重合数。"""
    if not holdings:
        return None, None, 0, ""

    # 锁定最新一个季度（季度字符串如 "2026年1季度股票投资明细"）
    latest_quarter = max(h.quarter for h in holdings if h.quarter) if any(h.quarter for h in holdings) else ""
    scoped = [h for h in holdings if not latest_quarter or h.quarter == latest_quarter][:10]

    total_weight = sum(h.weight_pct for h in scoped)
    if total_weight <= 0:
        return None, None, 0, latest_quarter

    us_weight = 0.0
    cn_hk_weight = 0.0
    mega_cap_count = 0

    for item in scoped:
        region, is_mega = classify_stock_holding(item.stock_code, item.stock_name)
        if region == "US_DEVELOPED":
            us_weight += item.weight_pct
        elif region in {"CN_A", "HK"}:
            cn_hk_weight += item.weight_pct
        if is_mega:
            mega_cap_count += 1

    us_pct = round(us_weight / total_weight * 100.0, 2)
    cn_hk_pct = round(cn_hk_weight / total_weight * 100.0, 2)
    return us_pct, cn_hk_pct, mega_cap_count, latest_quarter


def _bars_to_daily_returns(bars: Sequence[PriceBar]) -> Dict[date, float]:
    ordered = sorted(bars, key=lambda b: b.trade_date)
    rets: Dict[date, float] = {}
    for prev, curr in zip(ordered, ordered[1:]):
        if prev.close > 0:
            rets[curr.trade_date] = (curr.close - prev.close) / prev.close
    return rets


def _pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    n = len(xs)
    if n < 15:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x <= 1e-12 or den_y <= 1e-12:
        return None
    return round(num / (den_x * den_y), 4)


def compute_benchmark_correlation(
    fund_bars: Sequence[PriceBar],
    benchmark_bars: Sequence[PriceBar],
) -> Optional[float]:
    """计算 QDII 净值与基准（如 QQQ）的日收益率皮尔逊相关系数（兼容 T+0 / T+1 净值时差取最优对齐）。"""
    fund_rets = _bars_to_daily_returns(fund_bars)
    bench_rets = _bars_to_daily_returns(benchmark_bars)
    if len(fund_rets) < 15 or len(bench_rets) < 15:
        return None

    candidates: List[float] = []
    for day_shift in (0, -1, 1):
        xs: List[float] = []
        ys: List[float] = []
        for f_date, f_ret in fund_rets.items():
            b_date = f_date + timedelta(days=day_shift)
            if b_date in bench_rets:
                xs.append(f_ret)
                ys.append(bench_rets[b_date])
        corr = _pearson_corr(xs, ys)
        if corr is not None:
            candidates.append(corr)

    return max(candidates) if candidates else None


def evaluate_etf_premiums(
    cfg: QDIIRouterConfig,
    etf_spot_prices: Dict[str, float],
    etf_nav_map: Dict[str, float],
) -> List[ETFSpotPremium]:
    """计算场内纳指 ETF 实时溢价率，并按 max_etf_premium_pct（默认 2.0%）执行防追高门禁。"""
    results: List[ETFSpotPremium] = []
    for etf in cfg.on_exchange_etfs:
        spot = etf_spot_prices.get(etf.code)
        nav = etf_nav_map.get(etf.code)
        if spot is None or nav is None or spot <= 0 or nav <= 0:
            continue
        premium_pct = round((spot / nav - 1.0) * 100.0, 2)
        executable = premium_pct <= cfg.max_etf_premium_pct
        warning = (
            ""
            if executable
            else f"场内溢价 {premium_pct:+.2f}% 超过红线 +{cfg.max_etf_premium_pct:.1f}%，严禁高溢价接盘！"
        )
        results.append(
            ETFSpotPremium(
                code=etf.code,
                name=etf.name,
                spot_price=round(spot, 4),
                latest_nav=round(nav, 4),
                premium_pct=premium_pct,
                executable=executable,
                warning=warning,
            )
        )
    results.sort(key=lambda item: item.premium_pct)
    return results


def build_qdii_route_plan(
    cfg: QDIIRouterConfig,
    requested_amount_cny: float,
    benchmark_bars: Sequence[PriceBar],
    purchase_info_map: Dict[str, QDIIPurchaseInfo],
    holdings_by_code: Dict[str, List[QDIIHoldingItem]],
    nav_series_by_code: Dict[str, List[PriceBar]],
    etf_spot_prices: Dict[str, float],
    etf_nav_map: Dict[str, float],
) -> QDIIRoutePlan:
    """全面体检白名单 QDII 平替池与场内 ETF 溢价，并生成满足目标金额的最优拆单方案。"""
    etf_premiums = evaluate_etf_premiums(cfg, etf_spot_prices, etf_nav_map)
    evaluations: List[QDIIProxyEvaluation] = []

    for item in cfg.proxy_pool:
        p_info = purchase_info_map.get(item.fund_code)
        purchase_status = p_info.purchase_status if p_info else "UNKNOWN"
        daily_limit = p_info.daily_limit_cny if p_info else None
        fee_rate = p_info.fee_rate_pct if p_info else None
        live_name = (p_info.fund_name if p_info and p_info.fund_name else item.name).strip()

        raw_holdings = holdings_by_code.get(item.holdings_code) or holdings_by_code.get(item.fund_code) or []
        enriched_holdings = [
            QDIIHoldingItem(
                stock_code=h.stock_code,
                stock_name=h.stock_name,
                weight_pct=h.weight_pct,
                quarter=h.quarter,
                region=classify_stock_holding(h.stock_code, h.stock_name)[0],
                is_mega_cap_tech=classify_stock_holding(h.stock_code, h.stock_name)[1],
            )
            for h in raw_holdings[:10]
        ]

        us_pct, cn_hk_pct, mega_count, latest_quarter = analyze_holdings_purity(enriched_holdings)
        corr = compute_benchmark_correlation(
            nav_series_by_code.get(item.fund_code, []),
            benchmark_bars,
        )

        reject_reasons: List[str] = []

        # 1. 禁用名称关键词检查（防一年持有期锁死 / 美元份额）
        for kw in cfg.forbidden_name_keywords:
            if kw in live_name:
                reject_reasons.append(f"名称命中禁用项 '{kw}'（流动性受限或非人民币份额）")

        # 2. 申购开关与日限额检查
        if purchase_status in {"暂停申购", "封闭期", "场内交易", "UNKNOWN"}:
            reject_reasons.append(f"当前申购状态不可用: {purchase_status}")
        elif daily_limit is not None and daily_limit <= 0:
            reject_reasons.append("日累计限购金额为 0 元")

        # 3. 物理防老鼠仓与风格漂移检查（纯被动指数联接基金若季报只持 ETF 无个股明细则豁免个股占比校验）
        if not item.is_passive:
            if us_pct is None or cn_hk_pct is None:
                reject_reasons.append("缺少最新季报前十大持仓数据，无法验证美股大盘纯度")
            else:
                if us_pct < cfg.min_us_developed_top10_pct:
                    reject_reasons.append(
                        f"美股/发达市场重仓占比 {us_pct:.1f}% 低于底线 {cfg.min_us_developed_top10_pct:.1f}%"
                    )
                if cn_hk_pct > cfg.max_cn_hk_top10_pct:
                    reject_reasons.append(
                        f"A股+港股重仓占比 {cn_hk_pct:.1f}% 超过防漂移红线 {cfg.max_cn_hk_top10_pct:.1f}%"
                    )

        # 4. 真实收益相关性校验（防挂羊头卖狗肉）
        if corr is not None and corr < cfg.min_corr_with_benchmark:
            reject_reasons.append(
                f"近120日净值与 {cfg.benchmark_symbol} 相关系数 {corr:.2f} 低于门槛 {cfg.min_corr_with_benchmark:.2f}"
            )

        passed = len(reject_reasons) == 0

        # 综合纯度评分（0~100）：被动指数优先 + 相关性 + 美股大盘纯度 + 巨头重合度 + 低费率
        score = 0.0
        if item.is_passive:
            score += 30.0
        if corr is not None:
            score += max(0.0, corr) * 35.0
        if us_pct is not None:
            score += (us_pct / 100.0) * 20.0
        elif item.is_passive:
            score += 20.0
        score += min(mega_count, 8) * 1.5
        if fee_rate is not None and fee_rate == 0.0:
            score += 3.0
        purity_score = round(min(100.0, score), 2)

        evaluations.append(
            QDIIProxyEvaluation(
                fund_code=item.fund_code,
                holdings_code=item.holdings_code,
                name=live_name,
                company=item.company,
                is_passive=item.is_passive,
                purchase_status=purchase_status,
                daily_limit_cny=daily_limit,
                fee_rate_pct=fee_rate,
                us_developed_top10_pct=us_pct,
                cn_hk_top10_pct=cn_hk_pct,
                mega_cap_overlap_count=mega_count,
                corr_with_benchmark=corr,
                latest_quarter=latest_quarter,
                top_holdings=enriched_holdings,
                passed=passed,
                reject_reasons=reject_reasons,
                purity_score=purity_score,
            )
        )

    # 排序：合规通过优先 -> 限额能承载较大比例优先（避免全拆成 5 元/10 元碎单）-> 纯度分降序
    def _sort_key(ev: QDIIProxyEvaluation) -> Tuple[int, int, float]:
        is_tiny_cap = 1 if (ev.daily_limit_cny is not None and ev.daily_limit_cny < 100.0) else 0
        return (0 if ev.passed else 1, is_tiny_cap, -ev.purity_score)

    evaluations.sort(key=_sort_key)

    # 贪心生成可执行拆单路线（跳过单日限额 < 50 元的极碎单，除非大额全部用完）
    allocations: List[QDIISplitAllocation] = []
    remaining = round(max(0.0, requested_amount_cny), 2)

    passing_large = [
        ev for ev in evaluations if ev.passed and (ev.daily_limit_cny is None or ev.daily_limit_cny >= 50.0)
    ]
    passing_tiny = [
        ev for ev in evaluations if ev.passed and ev.daily_limit_cny is not None and 0 < ev.daily_limit_cny < 50.0
    ]

    for ev in passing_large + passing_tiny:
        if remaining <= 0:
            break
        cap = remaining if ev.daily_limit_cny is None else min(remaining, ev.daily_limit_cny)
        cap = round(cap, 2)
        if cap <= 0:
            continue
        allocations.append(
            QDIISplitAllocation(
                fund_code=ev.fund_code,
                name=ev.name,
                company=ev.company,
                allocated_cny=cap,
                daily_limit_cny=ev.daily_limit_cny,
                is_passive=ev.is_passive,
                us_developed_top10_pct=ev.us_developed_top10_pct,
                corr_with_benchmark=ev.corr_with_benchmark,
            )
        )
        remaining = round(remaining - cap, 2)

    total_allocated = round(requested_amount_cny - remaining, 2)
    shortfall = round(max(0.0, remaining), 2)

    exec_etfs = [e for e in etf_premiums if e.executable]
    etf_note = (
        f"场内低溢价 ETF 可选: {', '.join(f'{e.code}({e.premium_pct:+.2f}%)' for e in exec_etfs)}"
        if exec_etfs
        else (
            f"场内纳指 ETF 溢价均超 +{cfg.max_etf_premium_pct:.1f}% 红线"
            f"（最低 {etf_premiums[0].code} {etf_premiums[0].premium_pct:+.2f}%），严禁场内追高"
            if etf_premiums
            else "未拉取到场内 ETF 溢价数据"
        )
    )

    if allocations and shortfall == 0:
        plan_desc = " + ".join(f"{a.name}({a.fund_code}) {a.allocated_cny:.0f}元" for a in allocations)
        summary = f"目标 {requested_amount_cny:.0f} 元可全额执行：{plan_desc}；{etf_note}"
    elif allocations:
        plan_desc = " + ".join(f"{a.name}({a.fund_code}) {a.allocated_cny:.0f}元" for a in allocations)
        summary = (
            f"目标 {requested_amount_cny:.0f} 元仅能执行 {total_allocated:.0f} 元（缺口 {shortfall:.0f} 元）："
            f"{plan_desc}；{etf_note}"
        )
    else:
        summary = f"当前白名单池无可满足纯度与限额条件的开放 QDII（缺口 {shortfall:.0f} 元）；{etf_note}"

    return QDIIRoutePlan(
        benchmark_symbol=cfg.benchmark_symbol,
        requested_amount_cny=requested_amount_cny,
        total_allocated_cny=total_allocated,
        shortfall_cny=shortfall,
        allocations=allocations,
        proxy_evaluations=evaluations,
        etf_premiums=etf_premiums,
        summary=summary,
    )
