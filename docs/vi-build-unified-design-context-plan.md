# VI Build 统一设计上下文：设计与开发计划

状态：设计评审稿（本文件不改变运行时代码）  
适用分支：`codex/theme-integration-upgrade`

## 1. 结论与边界

VI Build 不是另一套 PPT 渲染器，也不是在 Build Mode 外再包一层
不可消费的“VI 字典”。它的职责是在 Build 开始前，从模板中提取可执行的
视觉约束；Build Mode 是唯一的页面规划、组件装配与渲染消费者。

因此，VI 提取结果必须与已经完成的主题视觉系统共用一个可序列化的
`ResolvedDesignContext`。主题、模板和人工补充只是这个上下文的不同生产者；
所有 Build helper 都只读取这一种格式，并回传它实际采用或未采用的规则。

本阶段不改变下列边界：

- `generate_ppt(content=...)` 仍是 FreeStyle API，不自动变成 VI Build。
- Build Mode 保持精确、可编辑的原生 PPTX 输出，不把整页栅格化为模板截图。
- 系统和 VI Build 模板统一以 16:9 画布为基础；非 16:9 模板属于输入适配议题，
  不在本轮“保留任意模板尺寸”的承诺范围内。
- 原模板的封面、目录、章节页、结束页等框架页默认保持不变。
- 不自动把未知文本框按顺序替换；模板中的内容槽位必须可识别或人工确认。

## 2. 已有证据与问题定义

植物风格模板的验证证明了两点：

1. 当前 Build 可继承颜色、字号和局部网格，因此新增页能“看起来接近”。
2. 仅继承这些 token 不足以保留模板的视觉语法。该模板的关键特征还包括
   植物摄影、照片裁切、深绿图像面板、大留白、粗黑标题和固定的图文比例。
   缺少照片时，即使颜色正确，新页仍不属于同一视觉系统。

一次无文件的可行性探针已确认：现有主题上下文可无损携带 `assets`、
`components`、`archetypes`、`content_slots`、`locks` 和 `acceptance` 字段，
但当前 Build 只有颜色与字体的消费者；其余字段既不会约束构建，也没有
“未采用”诊断。因此接口形式可行，但当前能力尚未达到 VI Build 标准。

## 3. 统一数据契约

### 3.1 规范对象

对外保持字典兼容；内部可使用类型化结构。所有上下文均通过
`normalize_design_context()` 归一化为以下版本化对象：

```python
ResolvedDesignContext = {
    "schema_version": "1.0",
    "source": {
        "kind": "theme | template | merged",
        "template_path": "...",              # 可选
        "template_fingerprint": "...",       # 可选，避免误用规则
        "extractor_version": "...",          # 可选
        "confidence": 0.0,                     # 0~1
        "warnings": [],
    },
    # 与已上线主题上下文兼容
    "colors": {},
    "semantic_roles": {},
    "typography": {},
    "decoration": {},
    "layout_variant": {},
    "dark_mode": False,

    # VI Build 扩展，均由 Build 消费或显式诊断
    "assets": {
        "logo": {},
        "references": [],
        "image_grammar": {
            "required": False,
            "subjects": [],
            "treatment": {},
            "crop": {},
            "min_area_ratio": None,
            "safe_zones": [],
            "reuse_policy": "allow",
        },
    },
    "components": {},
    "archetypes": [],
    "content_slots": [],
    "locks": [],
    "acceptance": {"must_coverage": [], "thresholds": {}},
    "diagnostics": {"warnings": [], "unknown_fields": []},
}
```

`BrandSpec` 和现有 `extract_design_dna()` 暂时保留，作为到此对象的兼容
适配层，而不是并行的运行时格式。这样已有客户不会被迫迁移，新能力也不必
让每个下游消费者理解两份数据。

### 3.2 字段语义

| 区域 | 表达内容 | Build 的责任 |
|---|---|---|
| `semantic_roles` / `typography` | 颜色角色、字体与 CJK 回退 | 延续现有主题继承与显式覆盖规则 |
| `assets.image_grammar` | 是否必须有图、主体、色调、裁切、占比、安全区 | 在页面装配前计划图片；缺资产时阻止或标记待补，不以色块代替 |
| `components` | 绿图像面板、编号标记、标题处理、页脚等可复用语法 | 由组件工厂创建可编辑形状/图片容器，并记录采用情况 |
| `archetypes` | 从参考页归纳的页面结构、允许组件、必需资产 | 选择合适参考页来新增页面，不机械复制任意幻灯片 |
| `content_slots` | 已确认的可替换文字/图片槽位、容量、溢出策略 | 只绑定有 ID 的槽位；未知槽位不自动覆盖 |
| `locks` | 模板锁定、可调整和禁止项 | 在渲染前校验请求是否合法，保护 logo、页脚、边距等 |
| `acceptance` | MUST 覆盖、版面/图片阈值、参考证据 | 生成 `design_application` 和验收报告，不能静默漏用 |

### 3.3 模板记录示例

植物模板的“文本左、照片右”原型会被表达为类似以下规则：

```yaml
archetypes:
  - id: botanical-text-photo-right
    reference_slide: 2
    permitted_components: [left_rule, editorial_title, forest_photo_panel]
    required_assets: [supporting_photo]
    layout: {text_zone: left, media_zone: right, media_min_area_ratio: 0.35}
assets:
  image_grammar:
    required: true
    subjects: [botanical, natural_material, organic_detail]
    treatment: {tonal_direction: natural, crop: cover}
components:
  forest_photo_panel: {fill_role: primary, image_mode: cover, editable: true}
acceptance:
  must_coverage: [image_present, image_subject_match, media_area, heading_treatment]
```

当用户没有提供合规图片时，构建结果应为 `NEEDS_ASSET`（或显式的待补占位符，
取决于调用方是否允许），而不是生成没有视觉锚点的纯文字页。

## 4. 生产者、消费者与回写闭环

```text
主题解析 ─┐
模板结构扫描 ─┼─> normalize_design_context ─> Build 规划器/组件/图片工具
人工规则补充 ─┘                                      │
                                                     ▼
                                   design_application + acceptance report
```

字段必须拥有明确消费者。无消费者的字段不得以“已支持”名义进入稳定接口。

| 上下文字段 | 首个消费者 | 输出证据 |
|---|---|---|
| 颜色、字体、装饰 | 现有 theme context 与高频 helper | `applied_to` |
| 资产规则 | 图片规划器、`cover_image` 路径 | `asset_plan`、缺失原因 |
| 组件语法 | 组件工厂 | 创建组件 ID、绑定的形状 ID |
| 页面原型 | Build 页面规划器 | 原型选择与适配原因 |
| 内容槽位 | 内容绑定器 | 槽位 ID、容量和溢出结论 |
| 锁定项 | 覆盖解析器 | 允许/拒绝的字段和来源 |
| 验收项 | VI QA 验证器 | 每个 MUST 的 PASS / NEEDS_REVISION / BLOCKED |

`design_application` 至少包含 `applied_to`、`not_applied`、`blocked`、
`fallbacks`、`asset_plan`、`slot_bindings` 和 `acceptance`。这使一次失败可以
定位为“提取错误”“Build 未消费”或“用户缺资产”，而不是把问题归结为模糊的
设计效果。

## 5. 合并与优先级

模板规则首先是合法性边界，然后才参与常规样式继承。

```text
硬性模板锁 / 必需资产 / 槽位安全与溢出规则
    > 同字段的显式值（除非 allow_template_override 明确授权）
    > helper 的局部 C / typo / 组件参数
    > 幻灯片级上下文
    > 演示文稿级上下文
    > 主题或库的归一化默认值
```

对未锁定的字段，继续遵循已发布的主题优先级：元素显式值优先于 helper、
slide 和 presentation 默认值。部分字典按字段合并，不能因为传入一个
`accent` 就丢失 `ink`、`surface` 或字体。模板派生值默认高于通用主题值；
用户希望修改模板锁定项时，必须使用明确的 `allow_template_override`，并把
该决定写入诊断。

## 6. 提取策略：先确定性，后推断

VI 提取器按下列层次产出同一契约，低置信度绝不伪装成确定结论。

1. **结构扫描（确定性）**：尺寸、母版/布局、形状、层级、文本 run 字体、
   颜色、图片关系、裁切、坐标、组合、页脚与 logo 候选。
2. **资产清单（确定性）**：媒体指纹、用途位置和可复用规则；上下文存引用与
   哈希，不把二进制图片塞进 JSON。
3. **语法归纳（可解释推断）**：按几何与样式聚类生成组件和页面原型，并为每条
   规则给出来源页、证据和置信度。
4. **语义标注（保守推断）**：识别标题、正文、图片、页脚、章节页等。低置信度
   产生 `needs_confirmation`，不自动成为替换槽位或锁定规则。
5. **人工覆盖**：支持小型 YAML/JSON 合同补充，用户可确认槽位、图片主题、
   lock 和允许的改写范围；覆盖本身也进入同一上下文与审计记录。

现有 `DesignDNAExtractor` 仅可靠给出了少量文本位置，颜色、字体、图片、
形状等字段尚未填充；它将在上述第一阶段得到补全，但不会直接成为 Build 的
执行格式。

## 7. 测试先行与验收门槛

在实现提取器之前，先用当前植物模板和固定的小型 fixture 集合写出会失败的
Build 消费者测试。只有这些测试红灯，才开始补运行时代码。

### P0：消费者契约测试

- `test_build_requires_asset_when_archetype_demands_photo`
- `test_build_applies_image_grammar_to_photo_crop_and_area`
- `test_build_emits_component_application_for_template_component`
- `test_build_rejects_unknown_or_overflowing_content_slot`
- `test_template_lock_blocks_unapproved_override`
- `test_vi_acceptance_reports_each_must_requirement`
- `test_legacy_theme_and_brand_spec_remain_compatible`

### P1：提取与映射测试

- 同一模板重复提取的指纹、角色、组件 ID 与原型结果稳定；
- 提取出的字体、填充、图片裁切和几何可追溯到具体 slide/shape；
- 低置信度识别不会变成可写槽位；
- `BrandSpec` 与旧 `extract_design_dna()` 的兼容投影不丢已有字段。

### P2：端到端视觉门槛

fixture 至少覆盖：植物照片型模板、图文企业模板、深色数据模板、含中文字体的
模板、带 logo/页脚的模板。每个 fixture 要：

- 保留的原始框架页像素/对象检查通过；
- 新增页必须选择一个参考原型，并在 `design_application` 有记录；
- 需要图片的原型必须有合规图片；没有图片时必须显式失败或待补；
- 经 PPTX → PDF → PNG 渲染后，逐页人工检查图片占比、裁切、留白、字体、
  页脚和视觉锚点；
- 结构 QA、PPTX 重开和可编辑性检查通过。

植物模板是首个验收样本：新增“文本左、照片右”页必须有一张符合自然/植物
图像语法的照片，媒体面积不少于 35%，保留深绿面板、粗黑标题和既定安全区。
这条要求正是之前测试缺失的关键，不能再仅靠色块通过。

## 8. 分步开发计划与预估

| 阶段 | 主要改动 | 工作量 | 退出条件 |
|---|---|---:|---|
| 0. 契约与红灯测试 | schema、消费者注册表、fixture、失败测试 | 1–2 人日 | P0 测试能准确暴露当前未消费字段 |
| 1. Build 消费与诊断 | 规范化、资产/原型/组件/槽位/lock 消费链、报告 | 3–4 人日 | P0 全绿，缺图不再静默降级 |
| 2. 确定性 VI 提取 | DNA 扫描、资产指纹、旧接口适配 | 3–4 人日 | P1 结构与兼容测试全绿 |
| 3. 语法归纳与人工覆盖 | 组件/原型推断、置信度、覆盖合同 | 4–5 人日 | fixture 模板可稳定输出可执行上下文 |
| 4. 视觉回归与文档 | A/B、PNG 审查、API/LLM 文档、样例 | 3–4 人日 | P2 与人工验收通过 |

合计预计 **14–19 人日**。阶段 0–1 是最高优先级：它先证明 Build 真能消费
VI 信息，再扩大提取能力，避免“提取很多、下游不用”的返工。

## 9. 预期文件范围

- `src/pptx_designer/renderer/theme_context.py`：升级为统一上下文的归一化与合并
  边界，保持现有主题调用兼容。
- `src/pptx_designer/enterprise/design_dna_extractor.py`：补全确定性结构/媒体提取，
  输出标准上下文或适配投影。
- `src/pptx_designer/enterprise/template_analyzer.py`、`brand.py`：成为兼容适配器，
  不再新增并行消费者格式。
- 新的公共 Build 编排/VI 校验模块（名称在阶段 0 固化）：页面原型、资产规划、
  槽位绑定、锁校验和 `design_application`。
- 图片与高频组件 helper：仅增加规范上下文消费，不复制 Build 引擎。
- `tests/` 中的契约、提取、兼容和渲染回归测试；`ppt_tasks/` 中的审查样例。
- `docs/api-reference.md`、`docs/llm-authoring-guide.md` 与本设计文档。

## 10. 兼容、发布与风险控制

- `Presentation(theme=...)`、`set_presentation_theme()`、已有 `C`/`typo` 调用保持
  不变；VI Build 作为 opt-in 编排入口推出。
- `generate_ppt(content=...)` 不因本升级改变语义。后续若支持模板输入，也必须走
  同一 `ResolvedDesignContext` 与完整验收链，而非暗中切换模式。
- schema 版本、模板指纹和提取器版本写入上下文；模板变更时拒绝复用旧规则或发
  出高优先级警告。
- 图片版权、素材缺失、字体不可用、复杂母版/SmartArt 等问题必须进入诊断；
  不能用无关图片、默认字体或空白色块伪装为成功。
- 开发保持在 `codex/theme-integration-upgrade`，`master` 继续作为可清理的基线；
  每一阶段形成独立、可回滚的提交。

## 11. 开发启动条件

代码升级前需要确认三项：

1. 采用 `ResolvedDesignContext` 作为主题和 VI 的唯一运行时契约；
2. 接受“需要图片的模板原型在缺图时显式待补/失败”的质量门槛；
3. 按阶段 0 → 1 → 2 → 3 → 4 推进，并以植物模板作为第一个视觉验收样本。

确认后先提交阶段 0 的红灯测试与 fixture，再进入任何运行时代码改动。
