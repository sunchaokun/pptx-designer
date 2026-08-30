# Acceptance contract

| ID | Level | Requirement | Expected evidence in rendered output | Status |
|---|---|---|---|---|
| R1 | MUST | 暖色编辑主题在全部页面保持一致，并明显影响字体、颜色、对齐与装饰 | 深色墨色标题、米白背景、金色规则线、居中关键页面 | OPEN |
| R2 | MUST | 8 页形成完整管理层叙事：决策、证据、流程、风险、请求 | 封面、摘要、问题、成果、流程、运营、护栏、决策页完整可见 | OPEN |
| R3 | MUST | 所有数值均明确为演示数据，且不伪装为外部事实 | 页脚及数据页写有“演示数据” | OPEN |
| R4 | MUST | 数据与流程关系应可在投影尺度阅读 | 指标、前后对比和流程节点清晰，无小字号或文字碰撞 | OPEN |
| R5 | MUST | 重要内容保持可编辑 | 结构 QA 显示 100% 原生可编辑形状，无越界 | OPEN |
| R6 | SHOULD | 页面密度随叙事变化，不重复同一张卡片布局 | 至少包含摘要、对比、指标、流程、时间线与决策请求 | OPEN |

Rules:

- Do not rewrite a MUST requirement merely to fit an output.
- Every MUST requires visible evidence in the rendered pages.
- Record `PASS`, `NEEDS_REVISION`, or `BLOCKED` with evidence.

