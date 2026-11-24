"""Stage 1 QDII 平替路由器单元测试：反老鼠仓纯度、风格漂移拦截、相关性计算、限额拆单与 ETF 溢价红线。"""

from __future__ import annotations

from datetime import date, timedelta

from wealth_radar.config.loader import (
    OnExchangeETFConfig,
    QDIIProxyItemConfig,
    QDIIRouterConfig,
)
from wealth_radar.core.qdii_router import (
    analyze_holdings_purity,
    build_qdii_route_plan,
    classify_stock_holding,
    compute_benchmark_correlation,
)
from wealth_radar.domain.models import PriceBar, QDIIHoldingItem, QDIIPurchaseInfo


def _series(closes: list[float], start: date) -> list[PriceBar]:
    return [PriceBar(trade_date=start + timedelta(days=i), close=c) for i, c in enumerate(closes)]


def test_stock_region_classification_and_purity_analysis() -> None:
    assert classify_stock_holding("NVDA", "英伟达") == ("US_DEVELOPED", True)
    assert classify_stock_holding("005930", "三星电子") == ("US_DEVELOPED", True)
    assert classify_stock_holding("300502", "新易盛") == ("CN_A", False)
    assert classify_stock_holding("00700", "腾讯控股") == ("HK", False)

    # 模拟广发全球精选结构（9只美股科技 + 1只港股）
    gf_holdings = [
        QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=8.0, quarter="2026Q1"),
        QDIIHoldingItem(stock_code="GOOG", stock_name="谷歌-C", weight_pct=8.0, quarter="2026Q1"),
        QDIIHoldingItem(stock_code="AAPL", stock_name="苹果", weight_pct=8.0, quarter="2026Q1"),
        QDIIHoldingItem(stock_code="AMZN", stock_name="亚马逊", weight_pct=8.0, quarter="2026Q1"),
        QDIIHoldingItem(stock_code="02513", stock_name="智谱", weight_pct=4.0, quarter="2026Q1"),
    ]
    us_pct, cn_hk_pct, mega_cnt, quarter = analyze_holdings_purity(gf_holdings)
    assert us_pct == round(32.0 / 36.0 * 100.0, 2)
    assert cn_hk_pct == round(4.0 / 36.0 * 100.0, 2)
    assert mega_cnt == 4
    assert quarter == "2026Q1"


def test_correlation_handles_t_plus_1_lag() -> None:
    start = date(2026, 9, 1)
    bench_closes = [100.0 * (1.0 + (0.02 if i % 2 == 0 else -0.015) * (1 + i % 3)) for i in range(25)]
    bench = _series(bench_closes, start)
    # 模拟 QDII 净值滞后 1 天反映美股走势
    fund = _series(bench_closes, start + timedelta(days=1))
    corr = compute_benchmark_correlation(fund, bench)
    assert corr is not None
    assert corr > 0.99


def test_qdii_route_plan_blocks_drift_lockup_high_premium_and_splits_limits() -> None:
    start = date(2026, 9, 1)
    bench_closes = [500.0 + (i % 5) * 4.0 - i * 1.1 for i in range(25)]
    bench_bars = _series(bench_closes, start)

    cfg = QDIIRouterConfig(
        benchmark_symbol="QQQ",
        min_us_developed_top10_pct=65.0,
        max_cn_hk_top10_pct=20.0,
        min_corr_with_benchmark=0.65,
        max_etf_premium_pct=2.0,
        on_exchange_etfs=[
            OnExchangeETFConfig(code="513100", name="国泰纳指ETF"),
            OnExchangeETFConfig(code="159941", name="广发纳指ETF"),
        ],
        proxy_pool=[
            QDIIProxyItemConfig(
                fund_code="021277",
                holdings_code="270023",
                name="广发全球精选C",
                company="广发基金",
                is_passive=False,
            ),
            QDIIProxyItemConfig(
                fund_code="022184",
                holdings_code="100055",
                name="富国全球科技互联网C",
                company="富国基金",
                is_passive=False,
            ),
            QDIIProxyItemConfig(
                fund_code="012922",
                holdings_code="012920",
                name="漂移光模块全球基C",
                company="某基金",
                is_passive=False,
            ),
            QDIIProxyItemConfig(
                fund_code="012536",
                holdings_code="012535",
                name="万家全球成长一年持有期C",
                company="万家基金",
                is_passive=False,
            ),
            QDIIProxyItemConfig(
                fund_code="008971",
                holdings_code="000834",
                name="大成纳斯达克100联接C",
                company="大成基金",
                is_passive=True,
            ),
        ],
    )

    purchase_map = {
        "021277": QDIIPurchaseInfo(fund_code="021277", fund_name="广发全球精选C", purchase_status="限大额", daily_limit_cny=800.0, fee_rate_pct=0.0),
        "022184": QDIIPurchaseInfo(fund_code="022184", fund_name="富国全球科技互联网C", purchase_status="限大额", daily_limit_cny=10000.0, fee_rate_pct=0.0),
        "012922": QDIIPurchaseInfo(fund_code="012922", fund_name="漂移光模块全球基C", purchase_status="开放申购", daily_limit_cny=None, fee_rate_pct=0.0),
        "012536": QDIIPurchaseInfo(fund_code="012536", fund_name="万家全球成长一年持有期C", purchase_status="开放申购", daily_limit_cny=None, fee_rate_pct=0.0),
        "008971": QDIIPurchaseInfo(fund_code="008971", fund_name="大成纳斯达克100联接C", purchase_status="限大额", daily_limit_cny=10.0, fee_rate_pct=0.0),
    }

    holdings_map = {
        "270023": [
            QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="AAPL", stock_name="苹果", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="GOOG", stock_name="谷歌", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="AMZN", stock_name="亚马逊", weight_pct=10.0, quarter="2026Q1"),
        ],
        "100055": [
            QDIIHoldingItem(stock_code="TSM", stock_name="台积电", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="GOOGL", stock_name="谷歌-A", weight_pct=10.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="09899", stock_name="网易云音乐", weight_pct=3.0, quarter="2026Q1"),
        ],
        "012920": [
            QDIIHoldingItem(stock_code="300502", stock_name="新易盛", weight_pct=15.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="300308", stock_name="中际旭创", weight_pct=15.0, quarter="2026Q1"),
            QDIIHoldingItem(stock_code="TSM", stock_name="台积电", weight_pct=10.0, quarter="2026Q1"),
        ],
        "012535": [
            QDIIHoldingItem(stock_code="NVDA", stock_name="英伟达", weight_pct=10.0, quarter="2026Q1"),
        ],
    }

    nav_map = {code: _series(bench_closes, start) for code in purchase_map}

    plan = build_qdii_route_plan(
        cfg=cfg,
        requested_amount_cny=1200.0,
        benchmark_bars=bench_bars,
        purchase_info_map=purchase_map,
        holdings_by_code=holdings_map,
        nav_series_by_code=nav_map,
        etf_spot_prices={"513100": 2.05, "159941": 1.27},
        etf_nav_map={"513100": 1.67, "159941": 1.25},
    )

    eval_by_code = {e.fund_code: e for e in plan.proxy_evaluations}
    # 漂移基与持有期基必须被门禁拦截
    assert eval_by_code["012922"].passed is False
    assert any("漂移" in r or "低于底线" in r for r in eval_by_code["012922"].reject_reasons)
    assert eval_by_code["012536"].passed is False
    assert any("持有期" in r for r in eval_by_code["012536"].reject_reasons)

    # 拆单结果必须满足 1200 元全额执行（广发 800 + 富国 400），且不会先拆给 10 元碎单大成
    assert plan.total_allocated_cny == 1200.0
    assert plan.shortfall_cny == 0.0
    alloc_map = {a.fund_code: a.allocated_cny for a in plan.allocations}
    assert alloc_map["021277"] == 800.0
    assert alloc_map["022184"] == 400.0

    # 场内 ETF 溢价守卫：513100 (+22.75%) 禁止，159941 (+1.60%) 可考虑
    etf_map = {e.code: e for e in plan.etf_premiums}
    assert etf_map["513100"].executable is False
    assert etf_map["159941"].executable is True
