# wealth-radar-ai 设计文档 (v1.1)

> 这套架构的核心工程防线是 **Fail-Closed（故障安全闭环）**、**Evidence-Grounded（仅基于证据审计）** 与 **Lifecycle Guardrail（买卖全周期风控）**：确定性代码负责持仓存续期预警、预算硬约束、信用底线初筛与公告打包；LLM 按资产类型采用双模式审计（可转债执行冷血 CRO 一票否决，宽基指数执行客观下跌归因防恐慌误杀）；任何 API 超时、证据缺失或 JSON 校验失败均默认拦截买入，绝不误放行。

---

## v1.0 → v1.1 核心修订说明

| 修订项 | v1.0 隐患 | v1.1 解决方案 |
| :--- | :--- | :--- |
| **【P0】持仓存续期与卖出风控** | 仅覆盖买入开仓，缺乏强赎、评级异动、止盈与 C 类费率监控 | 新增 **Stage 0 持仓守卫（`position_monitor.py`）**，不依赖 LLM、置顶推送强赎/暴雷/止盈/C 类持有时长提醒 |
| **【P0】转债信用下沉陷阱** | 仅限 `max_price <= 108`，70~95 元高危违约债容易挤占双低 `top_k` | 新增 `min_price`、`min_ytm_pct`、正股股价下限（防面值退市）、最低信用评级、排除已公告强赎，并支持高危公告正文摘要抓取 |
| **【P1】指数与转债 LLM 策略错配** | 用“冷血空头 CRO”审指数回调新闻，易在恐慌底部误杀左侧分批 | Stage 2 拆分为双模式：`CB_CONVEX` 维持冷血 CRO 排雷；`INDEX_BRIEFING` 改为下跌归因与结构校验，禁止仅凭短期情绪新闻否决 |
| **【P1】资金超支与高相关性风险** | QQQ + SOXX 强相关且 6 档共 6,000 元超过 5,000 元预算，易同向打光子弹 | 引入总预算与相关性分组预算硬约束、冷却期防锯齿重置、低相关配置模板，并标注美股 T-1 时区滞后与 QDII 限购提示 |
| **【P2】复盘窗口与不免五磨损** | 仅 30 天复盘难衡量下修与左侧策略；3,000 元转债高频小额轮动佣金损耗大 | `review` 支持多周期（30/90/180 天）分资产归因；增加 `min_order_amount_cny` 单笔磨损护栏与打新预留资金提示 |

---

## 1. 项目目标与非目标 (Scope & Non-Goals)

- **核心定位**：`wealth-radar-ai` —— 面向 1 万元“不免五”实战方案的三阶段混合投研与风控雷达。每天收盘前（14:30）运行一次，围绕 **5,000 元场外 C 类主线分批舱 + 3,000 元可转债打新与低价下修博弈舱（+ 2,000 元现金/货基安全垫）**，将持仓风控预警、开仓筛选、AI 审计、推送与复盘日志完全自动化。
- **三阶段职责切分**：
  - **Stage 0（持仓存续期守卫与卖出预警）**：纯确定性规则，读取 `data/portfolio.json`，优先扫描已持仓标的的强赎临界/公告、评级下调、回售登记、目标止盈位及 C 类基金持有天数，结果**置顶最高优先级推送**（不依赖 LLM，防止 API 故障漏报致命强赎风险）。
  - **Stage 1（确定性漏斗、预算校验与证据打包器）**：纯 Python 计算指数回撤档位（含总预算/相关性组预算硬约束与冷却期去重）以及带信用底线的可转债双低指标，将噪声压缩至 3 至 5 个高赔率候选；仅对命中候选抓取近期公告（高危公告优先拉取正文摘要）与新闻，按硬字符上限打包成 `EvidenceBundle`。
  - **Stage 2（双模式 LLM 审计网关）**：将 `EvidenceBundle` 喂给支持 Gemini 或 OpenAI 兼容接口（OpenAI / DeepSeek / OpenRouter / 本地 vLLM）的 LLM，强制输出受 Pydantic 校验的结构化 JSON 并落盘审计记录：
    - `CB_CONVEX`（可转债）：**对抗式 CRO 排雷模式**，默认有罪，执行一票否决（`hard_veto`）。
    - `INDEX_BATCH`（宽基/行业主线）：**下跌归因与结构校验模式**，输出下跌驱动归因与逆向风险提示，避免被恐慌媒体情绪误杀左侧分批纪律。
- **明确非目标（严禁 AI 越界实现）**：
  - 严禁接入任何券商自动交易或下单接口（纯只读雷达与决策支持）。
  - 严禁构建 Web 前端、数据库管理后台或复杂微服务。
  - 严禁让 LLM 预测短期涨跌点位或直接决定仓位金额。

---

## 2. 技术栈与架构铁律

- **运行环境**：Python 3.11+（`uv` + `pyproject.toml`）。
- **核心依赖**：
  - **数据契约与配置**：`pydantic>=2.7`、`pyyaml`、`python-dotenv`
  - **行情与推送**：`akshare`、`yfinance`、`pandas`、`httpx`
  - **LLM 适配**：`google-genai`（Gemini 原生结构化输出）、`openai`（覆盖 OpenAI / DeepSeek / 各类中转与本地兼容接口）
  - **CLI 与测试**：`typer`、`rich`、`pytest`、`pytest-mock`
- **五条架构铁律**：
  1. **单向依赖**：`core/`（纯计算、持仓检查与证据组装）禁止发起任何网络 IO 或文件写入；所有外部行情与 LLM 调用必须通过 `typing.Protocol` 抽象，确保单元测试 100% 离线运行。
  2. **Fail-Closed 故障降级**：LLM 超时、HTTP 异常、JSON 解析失败、证据包为空或预算超限时，严禁输出 `APPROVE_BUY`，必须自动降级为 `WATCHLIST` 或 `REJECT` 并标记 `hard_veto=True`。
  3. **故障隔离（Partial-Degrade）**：单一数据源异常（例如 `yfinance` 限流或单只转债公告详情抓取超时）不得中断整条管线；Stage 0 持仓强赎预警与当日可转债打新推送必须优先成功送达。
  4. **幂等与费用护栏**：对 `(target_id, trade_date, evidence_sha256, prompt_version)` 计算缓存键，当日重复运行直接命中本地缓存，避免重复消耗 Token。
  5. **原子持久化**：所有状态文件（`state.json`）写入采用同目录 `.tmp` 加 `os.replace` 原子替换。

---

## 3. 目录结构

```text
wealth-radar-ai/
├── pyproject.toml
├── .env.example                     # API Key 与 Webhook 环境变量模板
├── config/
│   └── radar.yaml                   # 主线标的、预算组、转债信用底线、持仓预警、LLM 路由配置
├── docs/
│   └── DESIGN.md                    # 本文档 (v1.1)
├── data/                            # 运行期生成（加入 .gitignore）
│   ├── state.json                   # 已触发回撤档位/冷却状态 + 当日 LLM 审计缓存
│   ├── portfolio.json               # 用户当前持仓快照（驱动 Stage 0 风控与预算硬约束）
│   └── audits/                      # 每日完整审计归档（JSONL，用于多周期胜率复盘）
├── src/wealth_radar/
│   ├── __init__.py
│   ├── domain/
│   │   ├── models.py                # 全部 Pydantic v2 数据契约（含 Portfolio/PositionAlert/AuditVerdict）
│   │   └── errors.py                # 自定义异常
│   ├── config/
│   │   └── loader.py                # YAML + .env 加载与严格校验（含预算一致性检查）
│   ├── data_feed/
│   │   ├── protocols.py             # MarketProvider / NewsProvider / CBProvider 协议
│   │   ├── index_feed.py            # yfinance + akshare 指数/ETF 历史行情、时区元信息与近期新闻
│   │   └── cb_feed.py               # akshare 可转债打新、全市场行情、强赎/评级状态与正股近90天公告(含高危正文摘要)
│   ├── core/
│   │   ├── position_monitor.py      # Stage 0: 持仓存续期风控、强赎预警、止盈/再平衡与 C 类费率提醒
│   │   ├── index_screener.py        # Stage 1: 120日回撤阶梯触发器（带冷却期、总预算与相关性组硬约束）
│   │   ├── cb_screener.py           # Stage 1: 可转债打新 + 带信用底线的低价下修筛选器
│   │   └── evidence_packer.py       # Stage 1: 关键词过滤、高危正文截断、去重与 SHA256 哈希
│   ├── llm/
│   │   ├── prompts.py               # 双模式固化 Prompt（CRO_CB_PROMPT 与 INDEX_BRIEFING_PROMPT）及版本号
│   │   ├── base.py                  # BaseAuditLLM 协议、双模式分派与统一代码层强校验/重试封装
│   │   ├── gemini_client.py         # google-genai 原生 response_schema 适配器
│   │   ├── openai_client.py         # OpenAI 兼容适配器（兼容 json_schema 与 json_object 降级）
│   │   └── factory.py               # 按 radar.yaml 实例化对应 Provider
│   ├── app/
│   │   ├── pipeline.py              # Stage 0 -> Stage 1 -> Stage 2 -> 落盘 -> 推送 主管线（带故障隔离）
│   │   ├── audit_store.py           # 审计记录持久化与 30/90/180 日分资产胜率复盘器
│   │   └── notifier.py              # Rich 终端渲染 + 飞书/企微/Telegram Webhook（置顶告警分级）
│   └── cli.py                       # Typer CLI 入口
└── tests/
    ├── fixtures/                    # 离线行情、公告(含正文片段)、持仓快照与模拟 LLM 响应 JSON
    ├── test_position_monitor.py
    ├── test_index_screener.py
    ├── test_cb_screener.py
    ├── test_evidence_packer.py
    ├── test_llm_gateway.py
    └── test_pipeline.py
```

---

## 4. 配置文件模板 (`config/radar.yaml`、`data/portfolio.json` 与 `.env.example`)

### `config/radar.yaml`

```yaml
# config/radar.yaml (v1.1)
index_monitor:
  total_budget_cny: 5000            # 指数舱总预算硬上限（严格禁止超支）
  lookback_days: 120
  reset_drawdown_pct: -2.0          # 回撤收敛至 -2% 以内自动重置所有已触发档位
  cooldown_trading_days: 5          # 重置后冷却交易日数，防止震荡市在浅回调反复触发打光子弹
  # 相关性组预算上限：避免把高相关标的（如 QQQ 与 SOXX）独立核算导致同向满仓
  correlation_groups:
    us_tech: 3500
    defensive_hedge: 1500
  targets:
    - symbol: "QQQ"
      source: "yfinance"
      market_timezone: "US"         # 14:30 运行时自动标注 T-1 美股收盘滞后，并提示核对 QDII 限购
      correlation_group: "us_tech"
      name: "纳指100 (对应场外C类)"
      budget_cny: 3500
      # 金字塔分批加仓（越跌买越多，合计 <= budget_cny）
      tiers:
        - drawdown_pct: -5.0
          amount_cny: 800
        - drawdown_pct: -10.0
          amount_cny: 1200
        - drawdown_pct: -15.0
          amount_cny: 1500
    # 默认搭配低相关主线平滑回撤；若仍想配置 SOXX，请将其 correlation_group 设为 "us_tech" 并与 QQQ 共享 3,500 元预算
    - symbol: "518880"
      source: "akshare"
      market_timezone: "CN"
      correlation_group: "defensive_hedge"
      name: "黄金ETF (对应场外C类联接)"
      budget_cny: 1500
      tiers:
        - drawdown_pct: -4.0
          amount_cny: 600
        - drawdown_pct: -8.0
          amount_cny: 900

cb_screener:
  total_budget_cny: 3000
  reserved_ipo_cash_cny: 1000       # 建议常备的打新中签缴款机动额（超额使用时发出提示）
  min_order_amount_cny: 2000        # “不免五”佣金防磨损护栏（若确认券商转债免五可调低至 1000）
  # 信用与价格双底线：严防 70~95 元深度违约债挤占双低 top_k
  min_price: 96.0
  max_price: 108.0
  max_premium_rate_pct: 45.0
  min_ytm_pct: 0.0                  # 到期税前收益率 >= 0%，守住债底保护
  min_remaining_years: 0.8
  max_remaining_years: 2.5
  min_stock_price_cny: 2.0          # 正股现价 >= 2.0 元，远离 1 元面值退市高危区
  min_credit_rating: "A+"           # 最低主体/债项评级（稳健型可提高至 "AA-"）
  exclude_st: true
  exclude_redeem_announced: true    # 排除已公告强赎或临近强赎触发标的
  top_k: 5                          # 仅取合规双低前 5 只进入公告抓取与 LLM 审计
  notice_lookback_days: 90
  # 命中以下高危关键词时，尝试抓取公告正文前 400 字用于核对锁定期截止日/强赎日/立案事由
  fetch_detail_keywords:
    - "不向下修正"
    - "不下修"
    - "提议向下修正"
    - "强赎"
    - "提前赎回"
    - "立案"
    - "违约"
    - "退市"
  notice_keywords:
    - "不向下修正"
    - "不下修"
    - "提议向下修正"
    - "向下修正"
    - "回售"
    - "赎回"
    - "强赎"
    - "提前赎回"
    - "业绩预告"
    - "立案"
    - "问询函"
    - "评级"
    - "逾期"
    - "违约"
    - "退市"
    - "面值"
    - "风险提示"

position_monitor:
  cb_take_profit_price: 128.0       # 持仓转债达到目标价提醒分批止盈
  cb_stop_review_price: 92.0        # 持仓转债跌破信用警戒线触发 CRITICAL 复审
  cb_redeem_alert_days_remaining: 5 # 强赎触发计数剩余 <= 5 个交易日或已公告强赎触发 CRITICAL 告警
  cb_putback_window_alert: true     # 触发回售窗口或回售登记期提醒
  index_take_profit_pct: 25.0       # 指数持仓浮盈达到 +25% 提醒分批止盈或再平衡
  index_c_class_max_days: 330       # 场外 C 类持有临近 1 年提醒评估销售服务费损耗

evidence_budget:
  max_notices_per_target: 8
  max_detail_chars_per_notice: 400  # 单条高危公告正文片段上限
  max_news_per_target: 6
  max_chars_per_bundle: 3200        # 单个标的送入 LLM 的最大证据字符数

llm:
  provider: "gemini"                # 可选: "gemini" | "openai_compatible"
  model: "gemini-2.5-flash"         # 若用 DeepSeek 可改为 "deepseek-chat"
  base_url: null                    # openai_compatible 时可填如 "https://api.deepseek.com"
  temperature: 0.1                  # 低温保证审计稳定性与可复现性
  timeout_sec: 30
  max_parse_retries: 1              # JSON 校验失败最多带报错信息重试 1 次
  strict_json_schema: true          # DeepSeek 等仅支持 json_object 的接口自动回退或置为 false
  enable_daily_cache: true
```

### `data/portfolio.json`（用户持仓快照示例）

> 每次手动完成申购、买入或卖出后更新此文件；系统启动时由 Pydantic 严格校验，同时作为 Stage 0 存续期风控和 Stage 1 预算硬约束的唯一事实来源。

```json
{
  "updated_at": "2026-11-24",
  "index_holdings": [
    {
      "symbol": "QQQ",
      "name": "纳指100场外C类",
      "fund_class": "C",
      "correlation_group": "us_tech",
      "invested_cny": 800.0,
      "avg_entry_price": 495.2,
      "first_buy_date": "2026-09-10"
    }
  ],
  "cb_holdings": [
    {
      "bond_code": "123xxx",
      "bond_name": "XX转债",
      "stock_code": "300xxx",
      "quantity": 20,
      "avg_cost_price": 103.5,
      "buy_date": "2026-10-15"
    }
  ]
}
```

### `.env.example`

```dotenv
# 根据 config/radar.yaml 中的 provider 填写对应 Key
GEMINI_API_KEY=""
OPENAI_API_KEY=""
# 可选覆盖 config 中的 base_url
OPENAI_BASE_URL=""
# 飞书 / 企微 / Telegram Webhook（留空则仅输出彩色终端报告）
WEBHOOK_URL=""
```

---

## 5. 核心数据契约 (`domain/models.py`)

Stage 0 告警契约 `PositionAlert` 与 Stage 2 审计契约 `AuditVerdict` 共同构成系统核心护城河，强制区分“可转债排雷”与“指数归因”，并要求所有 LLM 结论严格绑定输入证据（`evidence_citations`）：

```python
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

AssetType = Literal["INDEX_BATCH", "CB_CONVEX"]
AuditMode = Literal["CRO_VETO", "INDEX_BRIEFING"]
AlertSeverity = Literal["INFO", "WARNING", "CRITICAL"]
PositionAlertType = Literal[
    "REDEEM_URGENT",          # 已公告强赎或临近触发强赎
    "CREDIT_DETERIORATION",   # 持仓跌破警戒线或出现立案/退市/评级下调公告
    "PUTBACK_WINDOW",         # 进入回售触发或回售登记期
    "TAKE_PROFIT",            # 达到预设止盈/再平衡阈值
    "C_CLASS_FEE_DRAG",       # 场外 C 类持仓临近 1 年费率磨损提示
]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ThesisStatus = Literal["INTACT", "STRENGTHENED", "WEAKENED", "BROKEN", "UNKNOWN"]
FinalAction = Literal["REJECT", "WATCHLIST", "APPROVE_BUY"]


class IndexHolding(BaseModel):
    symbol: str
    name: str
    fund_class: Literal["A", "C", "ETF"] = "C"
    correlation_group: str
    invested_cny: float = Field(ge=0)
    avg_entry_price: float = Field(gt=0)
    first_buy_date: date


class CBHolding(BaseModel):
    bond_code: str
    bond_name: str
    stock_code: str
    quantity: int = Field(gt=0)         # 张数（10 张 = 1 手）
    avg_cost_price: float = Field(gt=0)
    buy_date: date


class PortfolioSnapshot(BaseModel):
    updated_at: date
    index_holdings: List[IndexHolding] = Field(default_factory=list)
    cb_holdings: List[CBHolding] = Field(default_factory=list)


class PositionAlert(BaseModel):
    target_id: str
    target_name: str
    asset_type: AssetType
    alert_type: PositionAlertType
    severity: AlertSeverity
    message: str
    recommended_action: str


class NoticeItem(BaseModel):
    pub_date: date
    title: str
    snippet: str = ""
    detail_fetched: bool = False        # 标注是否成功抓取公告正文片段（避免仅凭标题误判锁定期）
    matched_keywords: List[str] = Field(default_factory=list)


class EvidenceBundle(BaseModel):
    trade_date: date
    asset_type: AssetType
    audit_mode: AuditMode
    target_id: str                      # 如 "123xxx" 或 "QQQ"
    target_name: str
    data_as_of: str                     # 如 "2026-11-23 US Close (T-1 滞后，申购按今晚净值)"
    quantitative_metrics: Dict[str, float | str]
    trigger_summary: str                # 如 "首次触发 -10% 档位(拟投1200元)" 或 "合规双低第2(103.5/溢价24%/YTM+1.8%)"
    budget_check: Dict[str, float | str] = Field(default_factory=dict)
    notices: List[NoticeItem] = Field(default_factory=list)
    news_items: List[NoticeItem] = Field(default_factory=list)
    user_holding_context: Dict[str, float | str] = Field(default_factory=dict)
    evidence_sha256: str = ""


class AuditVerdict(BaseModel):
    target_id: str
    target_name: str
    asset_type: AssetType
    audit_mode: AuditMode
    hard_veto: bool = Field(
        description=(
            "CRO_VETO 模式下存在明确否决项（不下修锁定期、立案、违约、退市、评级大幅下调、关键证据缺失）时必须为 true；"
            "INDEX_BRIEFING 模式下仅当出现不可逆结构性崩坏(BROKEN)或预算/证据硬失败时才为 true"
        )
    )
    veto_reason: Optional[str] = Field(
        default=None,
        description="当 hard_veto 为 true 时，用一句话给出最硬核的否决事实"
    )
    lockup_expiry_date: Optional[str] = Field(
        default=None,
        description="仅 CB_CONVEX：若证据含不下修公告，提取锁定期截止日(YYYY-MM-DD)，未披露则填 UNSPECIFIED_IN_TITLE"
    )
    drawdown_attribution: Optional[str] = Field(
        default=None,
        description="仅 INDEX_BRIEFING：用 1~2 句话提炼本次回撤的核心客观归因（宏观利率/盈利/政策/情绪）"
    )
    credit_or_structural_risk: RiskLevel
    thesis_status: ThesisStatus
    bear_case_arguments: List[str] = Field(
        min_length=1,
        max_length=4,
        description="必须列出至少 1 条反对买入或需警惕的空头/风险论据"
    )
    bull_case_catalysts: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="仅基于提供证据中存在的潜在催化或支撑因素"
    )
    evidence_citations: List[str] = Field(
        default_factory=list,
        description="引用的公告或新闻日期与标题，严禁编造输入中不存在的日期或公告"
    )
    missing_info_warnings: List[str] = Field(
        default_factory=list,
        description="指出缺失的关键信息（例如：不下修公告未抓到正文无法确认截止日、未提供财务数据）"
    )
    final_action: FinalAction
    confidence_score: int = Field(ge=0, le=100)


class AuditRecord(BaseModel):
    run_timestamp: datetime
    prompt_version: str
    provider: str
    model: str
    price_at_audit: float
    bundle: EvidenceBundle
    verdict: AuditVerdict
    from_cache: bool = False
```

---

## 6. Stage 0 / Stage 1 / Stage 2 关键实现细节

### 6.1 Stage 0 持仓存续期守卫与卖出预警 (`core/position_monitor.py`)

纯确定性规则，**每次运行优先执行，告警置顶推送，不经由 LLM**，确保退出纪律和保命告警 100% 稳定触发：

- **可转债持仓扫描（读取 `portfolio.json` → `cb_holdings`）**：
  - **强赎紧急告警（`REDEEM_URGENT` / `CRITICAL`）**：若已发布强赎公告（标明最后交易日/转股日），或满足强赎条件的计数距触发仅剩 ≤ `cb_redeem_alert_days_remaining`（5 个交易日），立刻发出最高级别提醒，防止遗忘卖出/转股导致 20%~40% 溢价清零。
  - **信用恶化复审（`CREDIT_DETERIORATION` / `CRITICAL`）**：若持仓转债现价跌破 `cb_stop_review_price`（92.0 元），或正股近 7 日出现“立案/退市/违约/评级下调”公告，立即报警提醒人工紧急评估止损。
  - **回售窗口提醒（`PUTBACK_WINDOW` / `WARNING`）**：进入回售期且触发回售条件或公告回售登记期时提醒核对回售价与市价差。
  - **目标止盈提醒（`TAKE_PROFIT` / `WARNING`）**：转债现价达到 `cb_take_profit_price`（128.0 元）时提醒分批止盈，锁定下修博弈脉冲收益。
- **指数持仓扫描（读取 `portfolio.json` → `index_holdings`）**：
  - **止盈与再平衡提醒（`TAKE_PROFIT` / `WARNING`）**：当持仓标的现价较 `avg_entry_price` 浮盈 ≥ `index_take_profit_pct`（25%），提醒部分止盈或将超额收益再平衡至低相关资产/现金垫。
  - **C 类费率磨损提醒（`C_CLASS_FEE_DRAG` / `INFO`）**：对 `fund_class == "C"` 且持有天数 ≥ `index_c_class_max_days`（330 天）的持仓，提醒评估销售服务费损耗，考虑择机置换为 A 类或场内 ETF。

### 6.2 Stage 1 确定性筛选、预算校验与证据打包 (`core/`)

- **指数回撤阶梯器（`index_screener.py`）**：
  - 计算近 120 日最高收盘价 `peak_120d` 与当日回撤 `(close - peak_120d) / peak_120d * 100`。
  - **重置与冷却**：回撤收敛至 `reset_drawdown_pct`（`-2.0%`）以上时重置已触发档位，并写入 `cooldown_until`（未来 `cooldown_trading_days = 5` 个交易日内不再重复触发浅回调档位）。
  - **三层预算硬约束**：结合 `portfolio.json` 计算（1）单标的可投余额、（2）所属 `correlation_group` 可投余额、（3）指数舱总可投余额（≤ 5,000 元）。实际拟投入金额取 `min(tier.amount_cny, 三层余额)`；若余额为 0，标记 `BUDGET_EXHAUSTED` 并跳过 LLM 调用。
  - **时区与限购提示**：对 `market_timezone == "US"` 标的自动填充 `data_as_of`（提示 14:30 获取的是美股 T-1 收盘价，且场外 QDII 按今晚净值成交、申购前需手动核对基金是否限购）。
  - 仅在非 `--dry-run` 模式下将新触发档位写入 `state.json`。
- **可转债打新与带信用底线的低价筛选器（`cb_screener.py`）**：
  - **打新模块**：独立返回当日可申购新债列表（无需送进 LLM，置顶推送并检查转债舱可用现金是否低于 `reserved_ipo_cash_cny`）。
  - **信用底线过滤（v1.1 关键加固）**：依次过滤 `min_price <= price <= max_price`、`premium_rate_pct <= max_premium_rate_pct`、`ytm_pct >= min_ytm_pct`、`min_remaining_years <= remaining_years <= max_remaining_years`、`stock_price >= min_stock_price_cny`、`credit_rating >= min_credit_rating`、非 ST、未公告强赎；合规集合按 `double_low = price + premium_rate_pct` 升序截取前 `top_k` 只进入公告抓取。
  - **不免五磨损提醒**：若转债舱当前可用资金 < `min_order_amount_cny`（2,000 元），在 `budget_check` 与推送摘要中显式提示“单笔金额过小，不免五双边 10 元佣金将显著侵蚀收益”。
- **证据打包与高危正文截断（`evidence_packer.py`）**：
  - 可转债正股近 90 天公告中，优先保留标题命中 `notice_keywords` 的条目并按日期倒序截取最多 `max_notices_per_target` 条。
  - 对命中 `fetch_detail_keywords`（如“不向下修正”“强赎”“立案”）的公告，由 `cb_feed.py` 尝试拉取正文前 `max_detail_chars_per_notice`（400 字）写入 `snippet` 并置 `detail_fetched = True`；抓取失败时回退为仅标题并置 `detail_fetched = False`（不崩溃）。
  - 汇总文本按 `max_chars_per_bundle`（3,200 字符）硬截断，并基于规范化后的 JSON 内容计算 `evidence_sha256` 供缓存去重。

### 6.3 Stage 2 双模式 Prompt 设计 (`llm/prompts.py`)

针对“个券信用排雷”与“宽基左侧分批”的本质差异，固化两套独立 Prompt 与版本号：

```python
CB_PROMPT_VERSION = "cro_cb_v1.1"
INDEX_PROMPT_VERSION = "brief_index_v1.1"

CRO_CB_SYSTEM_PROMPT = """你是一家顶级对冲基金的冷血首席风控官（Chief Risk Officer）。
你的唯一 KPI 不是预测明天涨跌，而是通过严格的红队审计（Red-Teaming）找出可转债候选标的的条款陷阱、信用风险与退市硬伤，保护 1 万元小资金（无法靠 30 只分散对冲踩雷）绝不踩雷。

### 绝对审计纪律：
1. **默认有罪原则（Guilty Until Proven Innocent）**：假设每一只进入初筛的低价转债都藏着陷阱，你必须先全力寻找反对买入的空头证据（bear_case_arguments）。
2. **严禁迎合与预测**：不要鼓励交易，不要预测短期涨跌。你的工作是排雷与评估下修/债底赔率结构是否完好。
3. **仅基于给定证据（Strict Grounding）**：只能依据用户提供的 quantitative_metrics、notices 与 news_items 推理，严禁编造未出现的日期、条款或财务数字。
4. **必须触发 hard_veto = true 且 final_action = "REJECT" 的硬红线**：
   - 正股在近 90 天内发布过“不向下修正转股价格”公告，且当前仍处于承诺不下修锁定期内（必须在 lockup_expiry_date 提取截止日；若 detail_fetched=false 且标题未注明锁定期截止日，按保守原则标记 UNSPECIFIED_IN_TITLE 并触发 WATCHLIST/hard_veto=true 提示人工核验正文）；
   - 正股出现立案调查、严重违约/逾期、退市警示/面值退市风险、或明确主体/债项评级下调；
   - 转债已公告强赎或临近强赎触发且溢价率偏高。
5. **证据不足降级规则**：如果 notices 和 news_items 均为空，必须在 missing_info_warnings 中明确警告，且**严禁输出 APPROVE_BUY**（最高给 WATCHLIST 且 hard_veto = true）。
6. **一致性校验**：只要 hard_veto 为 true，final_action 绝不允许为 APPROVE_BUY。

请严格按照指定的 JSON Schema 输出结果，不要输出任何 Markdown 解释文字。"""


INDEX_BRIEFING_SYSTEM_PROMPT = """你是一家顶级资产管理公司的客观宏观策略师与纪律校验官。
当前标的为宽基或核心主线指数，已按用户预设的左侧回撤阶梯规则触发分批买入信号。你的职责不是用恐慌新闻吓退左侧纪律，而是帮用户看清本次下跌的真实驱动因素与潜在风险。

### 绝对审计纪律：
1. **客观归因，对抗情绪误杀**：宽基指数在回撤 -5% 至 -20% 时，财经媒体必然充满悲观叙事。**严禁仅因短期恐慌新闻、分析师唱空或常规宏观波动就输出 hard_veto = true**。
2. **清晰归因（drawdown_attribution）**：仅基于给定 news_items 与 quantitative_metrics，提炼本次回撤的 1~2 句核心客观归因（如利率预期重定价、龙头财报指引、地缘/关税摩擦、获利回吐）。
3. **反方风险提示（bear_case_arguments）**：仍须列出 1~3 条最值得警惕的中期风险点，帮助用户清醒认识下行风险，严禁盲目乐观。
4. **允许触发 hard_veto = true 的极窄红线**：
   - 仅当证据明确显示该指数底层逻辑发生**不可逆的结构性破坏**（例如核心成分行业遭遇永久性制度禁止或系统性偿付崩溃，thesis_status = "BROKEN"）；
   - 或 budget_check 明确提示预算已超限；
   - 若为常规周期回调与情绪杀跌，thesis_status 应评为 INTACT 或 WEAKENED，且不设 hard_veto（可正常输出 APPROVE_BUY，由用户最终确认执行）。
5. **仅基于给定证据（Strict Grounding）**：严禁编造输入中未出现的新闻或宏观数据；若 news_items 为空，在 missing_info_warnings 说明并输出 WATCHLIST。

请严格按照指定的 JSON Schema 输出结果，不要输出任何 Markdown 解释文字。"""
```

### 6.4 双 Provider LLM 网关、故障隔离与代码层强校验 (`llm/` & `app/`)

- **`GeminiAuditClient`（`gemini_client.py`）**：
  - 使用 `from google import genai` 与 `types.GenerateContentConfig(temperature=cfg.temperature, system_instruction=system_prompt, response_mime_type="application/json", response_schema=AuditVerdict)`，由 Gemini 底层语法约束保证结构化输出。
- **`OpenAICompatibleAuditClient`（`openai_client.py`）**：
  - 使用 `openai.OpenAI(api_key=..., base_url=..., timeout=cfg.timeout_sec)`。
  - 当 `strict_json_schema=True` 时优先调用 `client.beta.chat.completions.parse(..., response_format=AuditVerdict)`；若目标中转站或第三方模型（如 DeepSeek）返回 400 不支持 `json_schema`，自动捕获异常并优雅回退至 `response_format={"type": "json_object"}`（同时将 `AuditVerdict.model_json_schema()` 附加在 User Prompt 末尾），提取文本后交由 `AuditVerdict.model_validate_json()` 校验。
- **代码层二次强校验（`BaseAuditLLM` 后处理硬规则，不轻信模型自觉）**：
  - **预算硬门禁**：若 `bundle.budget_check.get("allowed") == False`，无论模型输出什么，代码强制覆写 `verdict.hard_veto = True`、`verdict.final_action = "REJECT"`。
  - **证据空缺门禁**：若 `bundle.notices` 与 `bundle.news_items` 均为空，强制覆写 `verdict.hard_veto = True`、`verdict.final_action = "WATCHLIST"`（若原为 `APPROVE_BUY`）。
  - **不下修标题未抓正文门禁（`CB_CONVEX`）**：若输入存在命中“不向下修正/不下修”且 `detail_fetched == False` 的公告，且模型未将 `final_action` 置为 `REJECT`，代码强制拦截 `APPROVE_BUY` 并降级为 `WATCHLIST` + `hard_veto = True`（提醒人工点开公告核对锁定期截止日）。
  - **一致性门禁**：若 `verdict.hard_veto` 为 `True` 但模型错误输出了 `final_action = "APPROVE_BUY"`，代码强制覆写为 `"REJECT"`。
  - **解析重试与 Fail-Closed**：若 JSON 解析或 Pydantic 校验失败，附带具体 `ValidationError` 重试 1 次；仍失败或网络超时则触发 Fail-Closed，返回合成兜底 `AuditVerdict(hard_veto=True, final_action="WATCHLIST", veto_reason="LLM_AUDIT_FAILED: ...", ...)`，保证整条管线不崩溃且不误放行。
- **管线故障隔离（`app/pipeline.py`）**：
  - 按 `Stage 0（持仓强赎/止盈）→ 可转债打新 → Stage 1 & 2（指数舱）→ Stage 1 & 2（转债舱）` 顺序分段 `try/except` 隔离执行；单一板块行情源异常时仅在推送报告中附带该板块错误摘要，不影响其他板块正常交付。

---

## 7. CLI 命令与多周期胜率复盘 (`cli.py` & `audit_store.py`)

提供 4 个简洁命令：

- **`wealth-radar run [--dry-run] [--no-llm] [--force-audit] [--positions-only]`**
  执行完整管线（Stage 0 → Stage 1 → Stage 2 → 落盘 → 推送）。`--dry-run` 使用离线夹具跑通整套流程且不改写 `state.json`；`--no-llm` 仅跑 Stage 0 & Stage 1 排查行情源；`--force-audit` 忽略当日缓存强制重调 LLM；`--positions-only` 仅执行 Stage 0 持仓存续期风控（强赎/止盈快速核验）。
- **`wealth-radar review --days 30`**
  支持 `--days 30 / 90 / 180` 多窗口复盘，读取 `data/audits/` 历史记录，拉取最新现价对比 `price_at_audit`，**按 `CB_CONVEX` 与 `INDEX_BATCH` 分资产独立统计**“被否决（`REJECT`）标的后续表现”与“被放行（`APPROVE_BUY`）标的后续表现”：
  - 30 天窗口：重点验证可转债 CRO 排雷是否有效避开信用雷与不下修滞涨债；
  - 90~180 天窗口：评估转债下修博弈与指数左侧分批的真实策略胜率与盈亏比。
- **`wealth-radar reset-tier <symbol>`**
  手动重置某条主线指数已触发的回撤档位及冷却期状态。
- **`wealth-radar test-llm`**
  内置 2 条离线测试夹具直连当前配置的 Gemini / OpenAI 兼容 API：
  1. 含“不下修公告陷阱”的可转债夹具 → 验证 `CRO_VETO` 模式正确触发 `hard_veto=True` 与 `REJECT`；
  2. 含“常规宏观恐慌新闻”的 QQQ 回撤夹具 → 验证 `INDEX_BRIEFING` 模式输出清晰 `drawdown_attribution` 且不被恐慌情绪误杀。

---

## 8. 离线单元测试验收矩阵 (`tests/`)

全部测试必须 0 网络请求、耗时小于 5 秒、全绿通过：

- **`test_position_monitor.py`**：
  - 验证持仓转债强赎公告/距触发 ≤ 5 天发出 `CRITICAL` 级 `REDEEM_URGENT` 告警。
  - 验证持仓转债跌破 `92.0` 元或正股近 7 日出现立案公告发出 `CREDIT_DETERIORATION` 告警。
  - 验证转债触达 `128.0` 元止盈、指数浮盈 ≥ `25%` 止盈、场外 C 类持有 ≥ `330` 天触发费率磨损提醒。
- **`test_index_screener.py`**：
  - 验证首次击穿 `-5%` / `-10%` 按金字塔金额触发提醒、次日停留在 `-11%` 不重复刷屏。
  - 验证反弹回 `-1.5%` 重置档位后，在 `cooldown_trading_days` 冷却期内再次触及 `-5%` 不重复触发。
  - 验证超过单标的预算、`correlation_group` 合并预算或 5,000 元总预算时精确截断或拦截。
  - 验证美股标的正确填充 T-1 时区与 QDII 限购提示。
- **`test_cb_screener.py`**：
  - 验证 `min_price=96.0` 过滤 80 元高危违约债、`min_ytm_pct=0.0` 过滤负收益债、`min_stock_price_cny=2.0` 过滤面值退市高危股、`min_credit_rating` 过滤低评级债、排除 ST 与已公告强赎标的。
  - 验证合规标的按双低正确升序截取 `top_k`，并在转债舱余额不足 `min_order_amount_cny` 时给出不免五磨损警告。
- **`test_evidence_packer.py`**：
  - 验证“不向下修正”“强赎”等高危关键词公告排在最前、正文 snippet 按 `max_detail_chars_per_notice` 截断并正确保留 `detail_fetched` 标志。
  - 验证汇总证据超过 `max_chars_per_bundle` 严格截断且 `evidence_sha256` 稳定一致。
- **`test_llm_gateway.py`**：
  - 验证 `CB_CONVEX` 与 `INDEX_BRIEFING` 正确路由至对应 Prompt 与版本号。
  - Mock 可转债含“不下修”且 `detail_fetched=False` 时，代码层后处理强制拦截 `APPROVE_BUY`。
  - Mock 预算超限时代码层强制覆写为 `REJECT`；证据为空时强制拦截 `APPROVE_BUY`。
  - Mock 模型返回非法 JSON 后第 2 次重试成功；2 次均失败时触发 Fail-Closed（绝不返回 `APPROVE_BUY`）。
  - Mock OpenAI `json_schema` 报 400 时自动回退到 `json_object` 模式并解析成功。
  - 验证同一 `(target_id, trade_date, evidence_sha256, prompt_version)` 当日二次运行命中本地缓存不重复调 API。
- **`test_pipeline.py`**：
  - 端到端 Mock 测试 `Stage 0 -> 打新 -> Stage 1 -> Stage 2` 完整流转、审计记录落盘与 Webhook 分级摘要生成。
  - 验证 `yfinance` 抛出网络超时异常时，Stage 0 持仓强赎预警与可转债打新推送仍正常输出（故障隔离）。
