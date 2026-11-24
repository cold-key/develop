# wealth-radar-ai

面向 1 万元“不免五”实战方案的三阶段混合投研与风控雷达（详见 [docs/DESIGN.md](docs/DESIGN.md)）。

## 核心架构

- **Stage 0（持仓存续期守卫）**：纯确定性规则扫描已持仓标的的强赎临界、信用恶化、回售窗口、止盈与场外 C 类持有时长，置顶告警。
- **Stage 1（确定性漏斗与证据打包）**：指数 120 日回撤阶梯（含三层预算硬约束与冷却期）+ 可转债打新与带信用底线的双低初筛 + 高危公告正文截取与 SHA256 哈希。
- **Stage 2（双模式 LLM 审计网关）**：可转债执行冷血 CRO 一票否决（`CRO_VETO`），宽基指数执行客观下跌归因（`INDEX_BRIEFING`）；代码层二次强校验与 Fail-Closed 兜底。

## 快速开始

```bash
# 1. 安装依赖（推荐 uv）
uv sync --extra dev
# 或使用 pip
pip install -e ".[dev]"

# 2. 配置环境变量与持仓快照
cp .env.example .env
# 在 data/portfolio.json 中维护当前持仓快照（首次运行若不存在则视为空仓）

# 3. 离线演练（0 网络、不修改 state.json）
wealth-radar run --dry-run

# 4. 验证 LLM 连通性与双模式审计红线
wealth-radar test-llm

# 5. 运行全套离线单元测试
pytest
```

## CLI 命令

- `wealth-radar run [--dry-run] [--no-llm] [--force-audit] [--positions-only]`
- `wealth-radar review --days 30`（支持 `30` / `90` / `180` 分资产统计）
- `wealth-radar reset-tier <symbol>`
- `wealth-radar test-llm`
