# AuditVerdict Schema 与双模式审计红线

调用 `wealth-radar record-audit` 时，提交的 JSON 必须严格满足 `AuditVerdict` Pydantic v2 契约。

## 1. JSON 字段规范

```json
{
  "target_id": "118034",
  "target_name": "晶能转债",
  "asset_type": "CB_CONVEX",
  "audit_mode": "CRO_VETO",
  "hard_veto": true,
  "veto_reason": "用一句话给出最硬核的否决事实（hard_veto=false 时为 null）",
  "lockup_expiry_date": "YYYY-MM-DD 或 UNSPECIFIED_IN_TITLE 或 null",
  "drawdown_attribution": "仅 INDEX_BRIEFING：1~2 句客观下跌归因，CB_CONVEX 为 null",
  "execution_plan": "可执行方案，如：申购 021277(广发全球精选C) 1200元，或暂缓观望",
  "selected_etf_code": null,
  "credit_or_structural_risk": "LOW | MEDIUM | HIGH | CRITICAL",
  "thesis_status": "INTACT | STRENGTHENED | WEAKENED | BROKEN | UNKNOWN",
  "bear_case_arguments": [
    "至少 1 条（最多 5 条）硬核空头/风险论据"
  ],
  "bull_case_catalysts": [
    "仅基于证据存在的潜在催化（0~4 条）"
  ],
  "evidence_citations": [
    "2026-11-24 公告或新闻标题（严禁编造不存在的日期与标题）"
  ],
  "web_research_notes": [
    "2026-11-24 [来源名称] 通过联网核验的公告原文/三季报/基金经理信息"
  ],
  "missing_info_warnings": [
    "明确指出仍缺失的关键核验信息"
  ],
  "final_action": "REJECT | WATCHLIST | APPROVE_BUY",
  "confidence_score": 80
}
```

## 2. 双模式审计纪律

### 模式 A：`CB_CONVEX` + `CRO_VETO`（可转债冷血排雷）
- **默认有罪**：3,000 元小舱位最多持有 1~2 只转债，无法靠 30 只分散对冲尾部违约，宁可错过绝不踩雷。
- **必须 `hard_veto=true` 且 `final_action="REJECT"` 的红线**：
  1. 正股近 90 日公告“不向下修正转股价格”且当前仍处锁定期内（须填写 `lockup_expiry_date`）；
  2. 正股立案调查、债务逾期/违约、退市/面值退市风险、主体/债项评级下调；
  3. 已公告强赎或临近强赎触发且溢价率偏高。
- **PDF 公告补证规则**：若扫描包中关键公告 `detail_fetched=false`，先联网查证正文写入 `web_research_notes`；若联网仍无法查实关键条款，保守输出 `WATCHLIST` + `hard_veto=true`。

### 模式 B：`INDEX_BATCH` + `INDEX_BRIEFING`（宽基左侧归因与平替执行）
- **对抗恐慌误杀**：严禁仅凭媒体悲观标题、分析师唱空或常规加息/通胀波动触发 `hard_veto=true`。
- **极窄否决红线**：仅当出现不可逆结构性破坏（`thesis_status="BROKEN"`）、三层预算超限或试图使用高溢价场内 ETF（> 2%）时才设 `hard_veto=true`。
- **美股 T-1 披露**：对美股标的须在风险或缺失警告中提醒 `T-1` 美股收盘价与今日 15:00 申购场外 QDII 按今晚净值成交的隔夜偏差。

## 3. Python 代码层五重硬门禁（`audit_gate.py` 自动强制执行）
1. **预算门禁**：`budget_check.allowed == false` → 强制覆写 `REJECT` + `hard_veto=true`。
2. **空证据门禁**：本地 `notices`、`news_items` 与 `web_research_notes` 全空 → 强制拦截 `APPROVE_BUY` 降级为 `WATCHLIST` + `hard_veto=true`。
3. **不下修未核验门禁**：命中不下修公告且 `detail_fetched=false` 且 `web_research_notes` 为空 → 强制拦截 `APPROVE_BUY`。
4. **场内高溢价 ETF 门禁**：若填写了 `selected_etf_code` 且该 ETF 溢价率 > `2.0%` → 强制覆写 `REJECT` + `hard_veto=true`。
5. **一致性门禁**：`hard_veto=true` 绝不允许与 `final_action="APPROVE_BUY"` 并存。
