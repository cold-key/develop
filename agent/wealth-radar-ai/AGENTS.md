# AGENTS.md — wealth-radar-ai

本仓库是面向中国大陆小资金实战方案的**确定性投研基础设施 + 跨平台 Agent Skill（v2.0，零 LLM API 依赖）**。

## 关键协作规范

1. **投研与风控任务**：执行市场扫描、可转债排雷、QQQ 平替 QDII 选基、持仓监控或胜率复盘时，请激活并使用 [.agents/skills/wealth-radar/SKILL.md](.agents/skills/wealth-radar/SKILL.md)。
2. **代码架构铁律**：
   - `src/wealth_radar/core/` 严禁发起任何网络 IO 或文件写入，所有外部行情/基金/公告调用必须通过 `data_feed/protocols.py` 注入。
   - 严禁重新引入 LLM API SDK（如 `openai` / `google-genai`）或券商自动下单接口。
   - 状态与持仓文件（`data/state.json`、`data/portfolio.json`、`data/last_scan.json`）必须原子替换写入。
3. **验证命令**：
   - 离线单元测试（0 网络、<5s）：`pytest -v`
   - 静态与类型检查：`ruff check src tests`、`mypy src`
   - 离线演练：`wealth-radar scan --dry-run`、`wealth-radar qdii-check --dry-run`
