# wealth-radar-ai 设计文档 (v2.0 — Skill + 确定性投研基础设施)

> **v2.0 核心范式升级**：全面移除自研 LLM API 网关（零 API Key、零模型适配与重试负担），将项目重塑为 **「纯 Python 确定性基础设施 + 零 LLM 定时哨兵 + 跨平台 Agent Skill（Antigravity / Codex / Claude Code）」**。确定性代码 100% 掌控数据采集、持仓保命告警、QDII 平替纯度/限额路由、信用底线筛选、四重硬门禁与复盘账本；顶级 Agent Harness 专职负责深度联网排雷（补查 PDF 公告原文/三季报/基金经理舆情）、多轮操盘推演与持仓记账。

---

## v1.1 → v2.0 核心演进说明

| 演进维度 | v1.1（自研 LLM 网关） | v2.0（Skill + 确定性基础设施） |
| :--- | :--- | :--- |
| **深度投研与排雷能力** | 受限于 3,200 字静态摘要与小模型，遇到 PDF 公告抓不到正文即卡死 | 交由 Antigravity / Codex 旗舰模型 + 联网工具，发现正文缺失可主动深挖公告/财报/舆情 |
| **工程复杂度与密钥维护** | 维护 Gemini/OpenAI 双客户端、400 回退、重试与多套 API Key | **删除全部 `llm/` 代码与 SDK 依赖**，零 LLM API Key，项目聚焦核心金融数据与风控护城河 |
| **大陆 QQQ 限购破局** | 仅提示“请手动核对 QDII 限购”，实盘被动纳指全市场限 5~10 元/日且场内溢价 >20% | 新增 **QDII 平替智能路由器（`qdii_router.py`）**：实时扫申购开关/日限额、审季报美股大盘纯度（防老鼠仓/风格漂移）、算 120 日 QQQ 相关性、监控场内 ETF 实时溢价红线 |
| **无人值守保命底线** | 依赖每日定时跑全量管线 | 独立 **`wealth-radar sentinel` 零 LLM 自动哨兵**：每天 14:30 无人值守监控强赎/信用恶化/打新/回撤触发，有信号再唤起 Skill 深度研判 |
| **防迎合纪律与量化复盘** | 内嵌于 LLM 网关后处理 | 抽象为独立 **`wealth-radar record-audit` 代码层硬门禁**：Agent 结论必须通过 Pydantic + 四重硬门禁校验后方可落盘 `audits/`，保留 30/90/180 天客观胜率复盘 |

---

## 1. 项目目标与非目标 (Scope & Non-Goals)

- **核心定位**：`wealth-radar-ai` —— 面向中国大陆 1 万元“不免五”实战方案（5,000 元场外低相关主线分批舱 + 3,000 元可转债打新与低价下修博弈舱 + 2,000 元现金安全垫）的**确定性投研基础设施 + 跨平台 AI Skill**。
- **两层职责切分**：
  1. **确定性基础设施层（纯 Python CLI，零 LLM 依赖）**：
     - **Stage 0 持仓存续期守卫（`position_monitor.py`）**：监控已持仓转债强赎倒计时/公告、信用恶化、回售、止盈，以及已持仓指数/QDII 的止盈、C 类持有时长与**季报风格漂移告警**。
     - **Stage 1 全市场漏斗与 QDII 平替路由（`index_screener.py` / `qdii_router.py` / `cb_screener.py` / `evidence_packer.py`）**：确定性计算 120 日回撤档位与三层预算硬约束、实时评估 QQQ 平替 QDII 池（开关门/日限额/美股大盘纯度/相关性/场内 ETF 溢价红线）、筛除信用垃圾转债并打包 `EvidenceBundle` JSON。
     - **Gate & Ledger 硬门禁账本（`audit_gate.py` / `audit_store.py`）**：以代码铁律拦截 Agent 可能出现的预算越界、空证据放行、不下修未核验放行、高溢价场内 ETF 追高与 `hard_veto` 矛盾，原子持久化 `state.json`、`portfolio.json` 与 `data/audits/*.jsonl`。
  2. **跨平台 Agent Skill 层（`.agents/skills/wealth-radar/SKILL.md`）**：
     - 原生兼容 **Antigravity / Codex / Claude Code**。
     - 固化标准作业流程（SOP）：强制先运行 CLI 获取硬数据 → 针对 PDF 公告或可疑基金主动联网补证 → 执行双模式审计（可转债=冷血 CRO；指数/QDII=客观归因+反漂移拆单）→ 强制调用 `record-audit` 过门禁归档 → 用户确认成交后调用 `portfolio` 安全记账。
- **明确非目标（严禁越界实现）**：
  - 严禁接入任何券商自动交易或下单接口（纯只读雷达、风控门禁与决策支持）。
  - 严禁在代码中内置第三方 LLM SDK 或自行调用大模型 API。
  - 严禁构建 Web 前端、数据库管理后台或复杂微服务。
  - 严禁预测短期涨跌点位，严禁突破配置预算上限或鼓励追高高溢价场内 ETF。

---

## 2. 技术栈与架构铁律

- **运行环境**：Python 3.11+（`uv` 或 `pip` + `pyproject.toml`）。
- **核心依赖（极简无 LLM SDK）**：
  - **数据契约与配置**：`pydantic>=2.7`、`pyyaml`、`python-dotenv`
  - **国内高可用行情与基金数据**：`akshare`（新浪美股/ETF、天天基金申购限额/季报持仓/历史净值、集思录强赎/双低、财联社电报）、`pandas`、`httpx`（东财个股公告与正文）
  - **可选行情备源**：`yfinance`（海外网络环境可用，失败自动回退新浪）
  - **CLI 与测试**：`typer`、`rich`、`pytest`、`ruff`、`mypy`
- **五条架构铁律**：
  1. **单向依赖**：`core/`（纯计算、持仓守卫、QDII 路由、硬门禁）严禁发起任何网络 IO 或文件写入；所有外部数据源必须通过 `typing.Protocol` 抽象，确保单元测试 100% 离线运行、耗时 < 5 秒。
  2. **Fail-Closed 代码硬门禁**：无论 Agent 推理多么自信，通过 `record-audit` 落盘前必须过 Python 代码层硬门禁（预算超限、空证据且未联网补证、不下修正文未核验、场内 ETF 溢价超红线、`hard_veto=True` 企图放行），违者自动拦截覆写。
  3. **板块级故障隔离（Partial-Degrade）**：单一数据源超时或限流不得拖垮全管线；Stage 0 强赎告警与当日可转债打新必须优先送达。
  4. **物理防老鼠仓与风格漂移底线**：QDII 平替池绝不听基金名称，必须通过季报前十大持仓美股大盘纯度（`≥ 65%`）、A/港股占比上限（`≤ 20%`）、近 120 日与 QQQ 真实收益相关性（`corr ≥ 0.65`）与大厂/无锁定期校验。
  5. **原子持久化**：`state.json` 与 `portfolio.json` 写入全部采用同目录 `.tmp` 加 `os.replace` 原子替换。

---

## 3. 目录结构

```text
wealth-radar-ai/
├── pyproject.toml                       # 零 LLM SDK 依赖
├── AGENTS.md                            # 供 Codex / Antigravity 自动读取的项目协作铁律
├── .env.example                         # 仅含可选 WEBHOOK_URL 与 JISILU_COOKIE（无 LLM Key）
├── .agents/
│   └── skills/
│       └── wealth-radar/
│           ├── SKILL.md                 # 跨平台投研风控 Skill 主手册（Antigravity / Codex 通用）
│           └── references/
│               ├── audit_schema.md      # record-audit 输入 JSON 规范与双模式审计红线
│               └── qdii_selection.md    # QDII 反老鼠仓、防漂移与拆单核查清单
├── config/
│   └── radar.yaml                       # 主线标的、QDII平替池、转债信用底线、持仓预警配置
├── docs/
│   └── DESIGN.md                        # 本文档 (v2.0)
├── data/                                # 运行期生成（加入 .gitignore）
│   ├── state.json                       # 已触发回撤档位与冷却期状态
│   ├── portfolio.json                   # 用户持仓快照（支持通过 CLI 安全增删改）
│   └── audits/                          # 每日结构化审计归档（JSONL，仅经 record-audit 门禁写入）
├── src/wealth_radar/
│   ├── __init__.py
│   ├── domain/
│   │   ├── models.py                    # 全部 Pydantic v2 数据契约（含 QDIIProxy / ScanPacket / AuditVerdict）
│   │   └── errors.py                    # 自定义异常
│   ├── config/
│   │   └── loader.py                    # YAML + .env + portfolio.json 加载与严格预算校验
│   ├── data_feed/
│   │   ├── protocols.py                 # MarketProvider / NewsProvider / CBProvider / QDIIProvider 协议
│   │   ├── index_feed.py                # 新浪美股/ETF + 财联社电报（yfinance 可选回退）
│   │   ├── cb_feed.py                   # 免 Cookie 全市场转债融合 + 东财正股近90天公告与正文摘要
│   │   └── qdii_feed.py                 # 天天基金实时申购限额、季报前十大持仓、120日净值与场内ETF溢价
│   ├── core/
│   │   ├── position_monitor.py          # Stage 0: 持仓强赎/信用/回售/止盈/C类费率 + QDII 风格漂移告警
│   │   ├── index_screener.py            # Stage 1: 120日回撤金字塔档位、冷却期与三层预算硬约束
│   │   ├── qdii_router.py               # Stage 1: QDII 平替纯度评分、相关性计算、限额拆单与 ETF 溢价守卫
│   │   ├── cb_screener.py               # Stage 1: 可转债打新 + 带信用底线的低价双低筛选器
│   │   ├── evidence_packer.py           # Stage 1: 高危关键词置顶、正文截断、字符硬上限与 SHA256
│   │   └── audit_gate.py                # Gate: 独立于任何大模型的 Python 代码层硬门禁校验器
│   ├── app/
│   │   ├── service.py                   # 编排 sentinel / scan / qdii-check / record-audit / portfolio / review
│   │   ├── audit_store.py               # 原子 state/portfolio 持久化、JSONL 归档与多周期胜率复盘
│   │   └── notifier.py                  # Rich 彩色终端渲染 + 飞书/企微/Telegram Webhook 推送
│   └── cli.py                           # Typer CLI 入口（同时支持人类阅读渲染与 --json 机器输出）
└── tests/
    ├── fixtures/                        # 离线行情、转债、QDII 持仓/净值/限额测试夹具
    ├── test_position_monitor.py
    ├── test_index_screener.py
    ├── test_qdii_router.py
    ├── test_cb_screener.py
    ├── test_evidence_packer.py
    ├── test_audit_gate.py
    └── test_service.py
```

---

## 4. 核心配置模板 (`config/radar.yaml`)

新增 **`qdii_router`** 节，将 `QQQ` 信号锚与大陆可执行 QDII 平替白名单池及场内 ETF 溢价守卫正式解耦：

```yaml
# config/radar.yaml (v2.0)
index_monitor:
  total_budget_cny: 5000            # 指数舱总预算硬上限
  lookback_days: 120
  reset_drawdown_pct: -2.0
  cooldown_trading_days: 5
  correlation_groups:
    us_tech: 3500
    defensive_hedge: 1500
  targets:
    - symbol: "QQQ"
      source: "akshare_us"          # 国内直连推荐 akshare_us（新浪美股日线）
      market_timezone: "US"
      correlation_group: "us_tech"
      name: "纳指100 (信号锚 -> QDII平替池)"
      budget_cny: 3500
      qdii_router_enabled: true     # 触发信号时自动联动 QDII 平替智能路由
      tiers:
        - drawdown_pct: -5.0
          amount_cny: 800
        - drawdown_pct: -10.0
          amount_cny: 1200
        - drawdown_pct: -15.0
          amount_cny: 1500
    - symbol: "518880"
      source: "akshare"
      market_timezone: "CN"
      correlation_group: "defensive_hedge"
      name: "黄金ETF (对应场外C类联接)"
      budget_cny: 1500
      qdii_router_enabled: false
      tiers:
        - drawdown_pct: -4.0
          amount_cny: 600
        - drawdown_pct: -8.0
          amount_cny: 900

qdii_router:
  benchmark_symbol: "QQQ"
  min_us_developed_top10_pct: 65.0  # 物理防老鼠仓底线：前十大重仓中纯美股/发达市场大盘占比 >= 65%
  max_cn_hk_top10_pct: 20.0         # 防风格漂移红线：前十大重仓中 A股+港股占比 <= 20%
  min_corr_with_benchmark: 0.65     # 近120日净值收益率与 QQQ 相关系数下限（兼容 T+1 时差）
  max_etf_premium_pct: 2.0          # 场内纳指 ETF 溢价红线（>2% 自动标红严禁接盘）
  forbidden_name_keywords:
    - "持有期"
    - "定开"
    - "封闭"
    - "美元"
    - "港元"
  # 场内纳指 ETF 溢价监控列表（仅在溢价 <= 2% 时才作为无老鼠仓备选）
  on_exchange_etfs:
    - code: "513100"
      name: "国泰纳指ETF"
    - code: "159941"
      name: "广发纳指ETF"
    - code: "159659"
      name: "招商纳指100ETF"
    - code: "159501"
      name: "嘉实纳指ETF"
    - code: "513300"
      name: "华夏纳指ETF"
  # 头部公募白名单 QDII 平替备选池（含被动纳指 + 高纯度美股大科技主动 QDII）
  proxy_pool:
    - fund_code: "021277"
      holdings_code: "270023"       # 季报持仓挂在主代码(A类)下，净值与申购限额看 C类代码
      name: "广发全球精选股票(QDII)人民币C"
      company: "广发基金"
      is_passive: false
    - fund_code: "022184"
      holdings_code: "100055"
      name: "富国全球科技互联网股票(QDII)C"
      company: "富国基金"
      is_passive: false
    - fund_code: "021842"
      holdings_code: "006373"
      name: "国富全球科技互联混合(QDII)人民币C"
      company: "国海富兰克林"
      is_passive: false
    - fund_code: "024239"
      holdings_code: "005698"
      name: "华夏全球科技先锋混合(QDII)C"
      company: "华夏基金"
      is_passive: false
    - fund_code: "008971"
      holdings_code: "000834"
      name: "大成纳斯达克100ETF联接(QDII)C"
      company: "大成基金"
      is_passive: true
    - fund_code: "016453"
      holdings_code: "016452"
      name: "南方纳斯达克100指数发起(QDII)C"
      company: "南方基金"
      is_passive: true
    - fund_code: "019173"
      holdings_code: "019172"
      name: "摩根纳斯达克100指数(QDII)人民币C"
      company: "摩根资产"
      is_passive: true
```

*(注：`cb_screener`、`position_monitor`、`evidence_budget` 完整保留 v1.1 全部信用底线、强赎守卫与正文摘要配置。)*

---

## 5. CLI 工具集与 Skill 协同工作流

全部 CLI 命令在无 API Key 环境下即可独立运行，并同时支持面向人类的 Rich 彩色渲染与面向 Agent 的 `--json` 结构化输出：

1. **`wealth-radar sentinel [--dry-run] [--push]`**（无人值守 14:30 自动哨兵）
   - 零 LLM 依赖、3~8 秒跑完：检查 Stage 0 持仓强赎/信用/漂移告警、今日可转债打新、指数回撤首次触发与 QDII 平替可用额度；若存在有效信号且配置了 `WEBHOOK_URL`，自动推送提醒你打开 Antigravity / Codex 做深度研判。
2. **`wealth-radar scan [--json] [--dry-run]`**（Skill 主数据入口）
   - 输出完整的结构化 `ScanPacket`（Stage 0 告警 + 打新 + 命中的指数回撤 `EvidenceBundle` + QDII 平替路由计划 + 场内 ETF 溢价表 + 合规转债 `EvidenceBundle`）。
   - Agent 拿到 `ScanPacket` 后，针对缺失正文（`detail_fetched=false`）的公告或目标 QDII 基金经理近况，**直接使用 Harness 原生联网能力补齐一手信息**。
3. **`wealth-radar qdii-check [--amount 1200] [--json]`**（独立 QDII 平替体检与拆单工具）
   - 实时扫描白名单池的申购开关/日限额、最新季报美股大盘纯度、A/港股漂移占比、近 120 日与 QQQ 相关系数、场内纳指 ETF 溢价率，并给出满足目标金额的拆单路线。
4. **`wealth-radar record-audit --verdict-file <path> [--bundle-file <path>] [--commit-tier]`**（防迎合代码硬门禁 + 审计账本）
   - Agent 完成深度审计后必须调用此命令落盘：Python 执行 Pydantic 契约校验 + 四重硬门禁（预算门禁、空证据拦截、不下修未核验拦截、高溢价 ETF 拦截、`hard_veto` 一致性覆写），校验通过后原子写入 `data/audits/YYYY-MM-DD.jsonl`（若 `--commit-tier` 则同步记录已触发指数档位到 `state.json`）。
5. **`wealth-radar portfolio [show | add-index | add-cb | remove]`**（安全持仓记账）
   - 让 Agent 在你确认成交后直接通过 CLI 原子更新 `data/portfolio.json`，彻底杜绝手改 JSON 出错或忘记同步导致持仓漂移。
6. **`wealth-radar review --days 30`** & **`wealth-radar reset-tier <symbol>`**
   - 分资产（`CB_CONVEX` / `INDEX_BATCH`）统计 30/90/180 天后 AI 否决与放行标的的真实收益表现，客观检验策略与 Agent 研判质量。

---

## 6. 跨平台 Skill 规范 (`.agents/skills/wealth-radar/SKILL.md`)

放在项目根目录 `.agents/skills/wealth-radar/SKILL.md`，**同时符合 Antigravity 与 Codex 的原生自动发现规范**：

- **触发条件**：当用户要求执行每日投研雷达审计、排查可转债条款/信用雷、寻找大陆 QQQ 平替 QDII、核对持仓强赎/止盈风险、记录成交或复盘历史胜率时自动激活。
- **强制 SOP**：
  1. 先调用 `wealth-radar scan --json`（或 `qdii-check --json`）获取客观确定性数据包，**严禁跳过 CLI 凭记忆编造行情、限额或回撤**；
  2. 对 `CB_CONVEX` 候选严格执行冷血 CRO 红队审计：若发现公告 `detail_fetched=false`，主动利用联网工具查证公告原文（不下修锁定期截止日、下修后转股价、业绩预告盈亏与现金流）；
  3. 对 `INDEX_BATCH` 候选执行客观下跌归因（防恐慌误杀左侧纪律），并结合 `qdii_route_plan` 核查推荐 QDII 近期有无基金经理变更、违规处罚或风格漂移新闻；若场内 ETF 溢价 > 2%，严禁建议场内追高；
  4. 调用 `wealth-radar record-audit` 通过 Python 硬门禁检验并落盘归档，将最终可执行方案（含具体金额、平替拆单、核心空头论据与缺失警告）清晰呈现给用户；
  5. 仅在用户明确回复“已成交”后，调用 `wealth-radar portfolio` 安全记账。
