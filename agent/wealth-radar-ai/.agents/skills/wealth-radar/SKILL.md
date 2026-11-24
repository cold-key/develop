---
name: wealth-radar
description: >-
  Execute disciplined investment risk-control, convertible bond CRO red-teaming,
  China mainland QDII proxy routing for QQQ, position lifecycle monitoring,
  audit-ledger recording, and portfolio accounting using the local wealth-radar
  CLI infrastructure. Use this skill whenever the user asks to run daily market
  screening, audit convertible bonds or index drawdowns, find open low-drift
  QDII proxies for QQQ, check redemption/take-profit alerts, record trades, or
  review historical audit win rates.
---

# wealth-radar 投研风控 Skill (v2.0)

本 Skill 将 **本地确定性 CLI 基础设施** 与 **Agent 顶级推理及联网查证能力** 深度结合，服务中国大陆小资金（5,000 元场外低相关主线分批舱 + 3,000 元可转债打新/下修博弈舱 + 2,000 元现金安全垫）的机构级投研纪律。

## 铁律红线（绝对禁止违背）

1. **先拿硬数据，严禁拍脑袋**：在给出任何结论、行情或限额前，必须先执行本地 CLI 拉取确定性数据，严禁凭记忆编造股价、转债价、基金限额、溢价率或公告日期。
2. **绝不迎合情绪**：若用户询问“要不要梭哈/加杠杆/追高 20% 溢价场内纳指 ETF”，必须冷血拒绝并给出客观风控依据；严禁预测短期涨跌点位。
3. **只做决策支持，不越界下单**：严禁生成自动交易脚本；仅在用户明确告知“已成交”后，才可调用 `wealth-radar portfolio` 更新本地持仓。
4. **所有正式审计必须过 Python 硬门禁落盘**：完成深度研判后，必须调用 `wealth-radar record-audit` 通过代码层五重硬门禁校验并归档，保证 30/90/180 天可量化复盘。

---

## 标准作业流程 (SOP)

### 场景 A：每日完整投研审计（主流程）

1. **拉取确定性扫描数据包**：
   ```bash
   wealth-radar scan --json
   ```
   - 仔细核查返回的 `ScanPacket`：
     - **置顶优先处理 `position_alerts`（Stage 0）**：若存在 `CRITICAL` 强赎倒计时（`REDEEM_URGENT`）、信用恶化（`CREDIT_DETERIORATION`）或持仓 QDII 风格漂移（`STYLE_DRIFT`），必须在回复最顶部用醒目警示标出。
     - **其次处理 `cb_ipos`**：若有今日可申购新债，置顶提醒顶格申购并核对 `ipo_cash_warning`。
     - 检查 `section_errors`：若局部数据源降级，如实向用户披露。

2. **对 `cb_bundles`（可转债）执行冷血 CRO 红队审计**：
   - 默认有罪原则（Guilty Until Proven Innocent），优先寻找反对买入的硬伤（详见 [audit_schema.md](./references/audit_schema.md)）。
   - **主动联网补证（Harness 核心优势）**：若关键公告（如“不向下修正”“向下修正”“业绩预告”“立案”“回售”）的 `detail_fetched == false`，**主动调用联网搜索工具**查阅公告原文或最新财报（确认不下修锁定期截止日、下修后转股价、当期盈亏与现金流），并将附带日期与来源的一手核验写入 `web_research_notes`。
   - 无法排除不下修锁定期、信用违约或退市风险时，必须 `hard_veto = true` 且 `final_action = "REJECT"` 或 `"WATCHLIST"`。

3. **对 `index_bundles`（指数主线）与 `qdii_route_plan` 执行客观归因与平替路由审计**：
   - **严禁因短期恐慌媒体情绪误杀左侧分批纪律**（常规利率重定价/情绪杀跌评 `INTACT` 或 `WEAKENED`，不触发 `hard_veto`）。
   - 若标的支持 QDII 平替（如 `QQQ`），参考 [qdii_selection.md](./references/qdii_selection.md)：
     - 检查 `qdii_route_plan.etf_premiums`：凡溢价率 > `2.0%` 的场内纳指 ETF 一律严禁推荐；
     - 检查 `qdii_route_plan.allocations` 推荐的开门平替 QDII，必要时**联网核查目标基金近期是否更换基金经理、有无违规处罚或重大持仓风格转向**；
     - 结合日限额与用户剩余预算，给出清晰的拆单执行计划（写入 `execution_plan`）。

4. **过 Python 代码层硬门禁并归档**：
   - 对每个完成深度审计的候选标的，按 [audit_schema.md](./references/audit_schema.md) 构造 `AuditVerdict` JSON（写入临时文件或直接传参），执行：
     ```bash
     wealth-radar record-audit --verdict-file <tmp_verdict.json> --auditor antigravity --commit-tier
     ```
     *(若当前在 Codex 中运行，将 `--auditor` 设为 `codex`；若本次用户仅演练不想锁定档位，省略 `--commit-tier`)*
   - 核查命令返回的 `gate_overrides`：若代码硬门禁触发覆写（如预算超限、溢价 ETF 拦截或未核验不下修），最终回复必须以门禁覆写后的 `final_action` 为准。

5. **输出简洁、可执行的投研风控日报**：
   - 结构顺序：`Stage 0 置顶预警` → `今日新债打新` → `指数主线归因与 QDII 拆单方案` → `可转债 CRO 排雷结论` → `缺失信息与风险提示`。

---

### 场景 B：单独排查大陆 QQQ 平替 QDII 与场内溢价

```bash
wealth-radar qdii-check --amount 1200 --json
```
结合 [qdii_selection.md](./references/qdii_selection.md) 解读实时限额、美股大盘纯度、A/港股漂移占比、120 日 QQQ 相关系数与场内 ETF 溢价，必要时联网核查基金经理稳定性后给出拆单建议。

### 场景 C：安全持仓记账（仅在用户确认成交后执行）

- 查看持仓：`wealth-radar portfolio show`
- 记录指数/QDII 成交（自动原子更新 `data/portfolio.json`）：
  ```bash
  wealth-radar portfolio add-index --symbol QQQ --name "广发全球精选C" --group us_tech --amount 1200 --price 651.03 --fund-class C --qdii-code 021277 --qdii-holdings-code 270023
  ```
- 记录可转债成交：
  ```bash
  wealth-radar portfolio add-cb --code 118034 --name "晶能转债" --stock-code 688223 --qty 20 --price 105.42
  ```
- 清仓移除：`wealth-radar portfolio remove --asset-type CB_CONVEX --id 118034`

### 场景 D：历史胜率复盘与档位重置

- 复盘 30/90/180 天胜率：`wealth-radar review --days 90`
- 手动重置回撤档位：`wealth-radar reset-tier QQQ`
- 离线验证整个 CLI 链路：`wealth-radar scan --dry-run`
