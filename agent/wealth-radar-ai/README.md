# wealth-radar-ai (v2.0)

面向中国大陆 1 万元“不免五”实战方案的 **确定性投研风控基础设施 + 跨平台 Agent Skill**（详见 [docs/DESIGN.md](docs/DESIGN.md)）。

## 核心架构（零 LLM API Key）

- **纯 Python 确定性基础设施（CLI）**：
  - `wealth-radar sentinel`：14:30 无人值守自动哨兵（Stage 0 持仓强赎/信用/止盈/风格漂移告警 + 可转债打新 + 指数回撤与 QDII 限额），支持飞书/企微/Telegram Webhook 推送。
  - `wealth-radar scan --json`：全市场确定性扫描与证据打包（含 QDII 平替路由与场内 ETF 溢价守卫），快照保存至 `data/last_scan.json`。
  - `wealth-radar qdii-check --amount 1200`：实时体检大陆 QQQ 平替 QDII 白名单池（申购开关/日限额、季报美股大盘纯度防老鼠仓、A/港股占比防漂移、120 日 QQQ 相关性、场内纳指 ETF 溢价红线）。
  - `wealth-radar record-audit`：独立于任何大模型的 Python 五重 Fail-Closed 硬门禁（预算/空证据/不下修未核验/高溢价 ETF/一致性），校验通过后归档至 `data/audits/`。
  - `wealth-radar portfolio [show | add-index | add-cb | remove]`：原子安全记账更新 `data/portfolio.json`。
  - `wealth-radar review --days 90` & `wealth-radar reset-tier <symbol>`：多周期分资产胜率复盘与档位重置。
- **跨平台 Agent Skill（`.agents/skills/wealth-radar/SKILL.md`）**：
  - 原生兼容 **Antigravity / Codex / Claude Code**，在 IDE 中直接借助顶级推理模型 + 联网搜索深挖 PDF 公告原文与基金经理舆情，告别手写 LLM API 网关与弱模型截断。

## 快速开始

```bash
# 1. 安装依赖（无 LLM SDK 依赖）
pip install -e ".[dev]"

# 2. 离线演练（0 网络、不修改 data/）
wealth-radar scan --dry-run
wealth-radar qdii-check --dry-run

# 3. 实盘一键扫描 / 体检 QQQ 平替 QDII
wealth-radar sentinel
wealth-radar qdii-check --amount 1200

# 4. 在 Antigravity 或 Codex 中直接使用
# 直接提问："帮我用 wealth-radar 跑今天的投研审计并核查 QQQ 平替 QDII"

# 5. 运行全套离线单元测试
pytest -v
```
