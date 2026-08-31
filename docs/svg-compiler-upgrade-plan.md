# SVG 编译器升级方案与实施计划

状态：待审批

本文档只记录代码调研、架构方案和实施计划。本阶段不新增实现代码，不改变现有行为。所有行号均基于当前工作树，编码前必须先确认工作树未发生影响相关文件行号的变更；若行号变化，先更新本文档并重新审批。

## 1. 目标与非目标

### 1.1 目标

- 保证基础几何、开放路径、描边、透明度、渐变和文字在 PowerPoint 与 LibreOffice 渲染结果中稳定。
- 为复杂 SVG 能力建立明确的原生渲染、近似渲染和栅格回退分层。
- 支持 `image`、常用 `pattern`、常用 `mask` 和有限的 `filter`。
- 任何无法准确转换的内容都必须产生可追踪的诊断信息，不能静默丢失。
- 保持简单图形的原生 PPT 可编辑性。
- 将“生成 PPTX → 导出 PDF/PNG → 视觉检查 → 回归测试”纳入正式验收链路。

### 1.2 非目标

- 不承诺完整实现浏览器 SVG 规范。
- 不承诺所有 SVG filter 在 PPT 中保持 100% 像素级一致。
- 不把整个 SVG 统一转成一张图片，避免破坏现有编辑性。
- 不在第一阶段修改现有图形组件的视觉风格；视觉设计系统应在编译器稳定后单独升级。

## 2. 当前实现盘点

### 2.1 调用链

当前主链路为：

`svg_chart` → `SVGCompiler.compile` → sanitizer → CSS 展开 → IR 分析 → 直接遍历 lxml 树 → 生成 PPT 原生 shapes → 输出 `SVGResult`。

对应位置：

- 公共入口：`src/pptx_designer/tools/svg.py:23-94`
- 编译入口：`src/pptx_designer/compiler/_compiler.py:355-446`
- 清洗器：`src/pptx_designer/compiler/_sanitizer.py:118-156`
- IR：`src/pptx_designer/compiler/_ir.py:90-132`
- 树遍历：`src/pptx_designer/compiler/_compiler.py:928-1010`
- 几何绘制：`src/pptx_designer/compiler/_compiler.py:1012-1205`
- Freeform 输出：`src/pptx_designer/compiler/_compiler.py:1207-1268`
- 文字输出：`src/pptx_designer/compiler/_compiler.py:1276-1295`

### 2.2 已确认的问题

1. 开放路径曾被无条件闭合。当前已在 `src/pptx_designer/compiler/_compiler.py:1236-1237` 改为仅对至少三个命令的子路径调用 `close()`。这是必须保留的回归修复。
2. 无填充路径曾被默认填充为白色。当前 `src/pptx_designer/compiler/_compiler.py:1116` 已把 `fill_hex or "#FFFFFF"` 改为直接传入 `fill_hex`。这是必须保留的回归修复。
3. IR 已将 `image`、`filter`、`mask`、`pattern`、`marker` 标记为 `raster_fallback_candidate`，位置为 `src/pptx_designer/compiler/_ir.py:64-84`，但当前实现没有真正的 fallback 渲染器。
4. `_walk` 对 `image`、`filter`、`mask` 的处理位于 `src/pptx_designer/compiler/_compiler.py:948-950`，当前是记录 warning 后跳过。
5. `SVGResult` 已有 `fallback_shapes`、`feature_levels`、`metrics` 字段，位置为 `src/pptx_designer/compiler/_compiler.py:298-330`，但 `fallback_shape_count` 当前固定为 0，位置为 `src/pptx_designer/compiler/_compiler.py:446`。
6. `group opacity` 当前提供 strict/distribute 两种策略，位置为 `src/pptx_designer/compiler/_compiler.py:336-350` 和 `489-519`。这说明项目已经具备能力分层的基础，但还没有统一的 feature policy。
7. 当前测试主要验证 shape_count、warning、feature level 和 PPTX 可保存重开，位置为 `tests/test_svg_compiler_integration.py:211-237`、`238-270`。还缺少复杂能力的视觉金标准和渲染后图像检查。

### 2.3 当前支持边界

| 能力 | 当前实现 | 结论 |
|---|---|---|
| rect/circle/ellipse/line/polygon/polyline/path | 原生 Freeform 或原生 shape | 可继续加强稳定性 |
| text/tspan | 原生文本框 | 受字体、基线和缩放影响 |
| linear/radial gradient | PPTX gradient effect | 可用，但不等于浏览器渲染 |
| transform | Affine 变换 | 当前主流程可用 |
| clipPath/evenodd | 布尔近似 | 需要保留“近似”诊断 |
| group opacity | strict 或 distribute | 不应静默声称完全一致 |
| image | warning 后跳过 | 第一阶段实现 |
| pattern | IR 标记，未渲染 | 第二阶段实现 |
| mask | warning 后跳过 | 第二阶段只做有限子集 |
| filter | warning 后跳过 | 第三阶段只做常用子集 |

## 3. 设计原则

### 3.1 三类渲染等级

每个 SVG 节点在编译前必须归类为：

1. `NATIVE`：使用 PPT 原生对象，保持编辑性。
2. `NATIVE_APPROX`：使用 PPT 原生能力近似，必须记录 approximation warning。
3. `RASTER_FALLBACK`：将复杂子树渲染为 PNG 后作为 PPT 图片插入，必须记录 fallback 资产与原因。

禁止出现“编译成功但节点被静默跳过”的情况。

### 3.2 子树级回退

复杂能力不能让整页 SVG 全部栅格化。回退边界应是带复杂效果的最小可渲染子树，并保留未涉及复杂效果的兄弟节点为原生对象。

### 3.3 单一坐标系统

所有 fallback 资产必须使用同一套 viewBox → slide inches 转换，不能由 rasterizer 和 native renderer 各自重新计算位置。

### 3.4 可诊断性优先

每次回退必须包含 feature、source id、边界框、使用的 renderer、分辨率和原因。编译结果必须能回答“哪个 SVG 节点没有原生转换”。

## 4. 分阶段实施方案

## 阶段 0：冻结基线与测试基础

### 目标

在任何新能力实现前，固定当前开放路径修复和现有测试结果。

### 代码位置

- 不新增生产代码。
- 在 `tests/test_svg_compiler_integration.py:1-347` 现有测试集上增加基线快照测试，新增代码必须插入到 `TestUnsupported` 类之后，即当前第 238 行之前；实际编码前重新确认行号。
- 新增独立文件 `tests/test_svg_render_regression.py`，从第 1 行开始创建。

### 必须新增的测试

- 两点 `<line fill="none">` 编译后必须存在一个带描边、无填充的 PPT 对象。
- 两点开放 `<path fill="none">` 编译后必须存在一个带描边、无填充的 PPT 对象。
- 现有基础图形、渐变、clipPath、group opacity、use 和文字测试全部保持通过。
- 对测试 SVG 执行 PPTX 保存、PDF 导出和 PNG 渲染，保存渲染输出目录，不以 shape_count 代替视觉验证。

### 阶段验收

- `python -m pytest -q tests/test_svg_compiler_integration.py tests/test_svg_tools.py`
- 现有 39 项 SVG 回归测试全部通过。
- 线条诊断样例中的主线和开放路径在 PNG 中可见。

## 阶段 1：统一 Feature Policy 与 fallback 接口

### 目标

建立能力决策层，但暂不实现复杂滤镜本身。

### 精确代码位置

1. 在 `src/pptx_designer/compiler/_compiler.py:298` 的 `SVGResult` 类中，在当前字段 `shape_count` 后插入新的诊断字段；若不需要新增公共字段，则复用现有 `fallback_shapes` 和 `metrics`，避免不必要的 API 扩张。
2. 在 `src/pptx_designer/compiler/_compiler.py:334` 的 `SVGCompiler` 类之前新增独立的 feature policy 类型文件：`src/pptx_designer/compiler/_policy.py`，从第 1 行开始创建。
3. 在 `src/pptx_designer/compiler/_compiler.py:336-350` 的构造函数参数区增加 policy、asset resolver 和 rasterizer 注入点；必须保持现有参数默认行为不变。
4. 在 `src/pptx_designer/compiler/_compiler.py:355-446` 的 `compile()` 中，在 `build_svg_ir(root)` 之后、`_reject_unrenderable_features()` 之前插入 feature classification 和 policy resolution。
5. 在 `src/pptx_designer/compiler/_compiler.py:559-577` 的 `_feature_levels()` 中，将固定 feature level 映射改为调用 policy resolver；保留现有 `NATIVE`、`NATIVE_APPROX`、`RASTER_FALLBACK_CANDIDATE` 字符串，避免破坏外部调用。
6. 在 `src/pptx_designer/compiler/_compiler.py:928-950` 的 `_walk()` 中，将复杂节点分派给 policy handler；禁止继续使用“warning 后直接跳过”的默认路径。
7. 在 `src/pptx_designer/tools/svg.py:23-94` 中增加可选配置参数时，必须使用默认值保持现有调用兼容，并在文档字符串中明确三种渲染等级。

### 阶段验收

- 不启用新能力时，现有所有测试结果不变。
- 未实现的复杂能力会产生明确 warning 和 feature level。
- 不允许 `fallback_shape_count` 仍然固定为 0。

## 阶段 2：实现 image 原生渲染

### 目标

支持本地文件、data URI 和受控资源解析，并以 PPT 图片对象插入。

### 精确代码位置

1. 在 `src/pptx_designer/compiler/_sanitizer.py:54-67` 的自闭合标签和清洗流程附近，增加 `href`/`xlink:href` 的规范化入口；不得在 sanitizer 中读取任意外部网络资源。
2. 新增 `src/pptx_designer/compiler/_assets.py`，从第 1 行创建，负责 data URI 解码、允许的本地资源解析、MIME 检查和资源大小限制。
3. 在 `src/pptx_designer/compiler/_compiler.py:928-950` 的 `_walk()` 中，将 `image` 从统一跳过分支拆出，调用 asset resolver。
4. 在 `src/pptx_designer/compiler/_compiler.py:1012` 的 `_render_shape()` 前新增 `_render_image()`，负责 `x/y/width/height`、`preserveAspectRatio`、opacity 和 transform 到 PPT 图片对象的映射。
5. 在 `src/pptx_designer/compiler/_compiler.py:421-446` 的结果汇总区记录 image asset 数量、fallback 数量和未解析资源原因。
6. 在 `tests/test_svg_compiler_integration.py:211-237` 的 `TestUnsupported` 后增加 image data URI、本地图片、缺失资源、非法协议和 preserveAspectRatio 测试。

### 阶段验收

- data URI 图片可插入 PPTX 并在 PNG 中显示。
- 缺失或未授权资源必须失败为可读 warning，不得产生空白占位且无说明。
- 图片不伪装成可编辑矢量对象，结果报告必须标记为 `RASTER_FALLBACK` 或 `NATIVE_IMAGE`。

## 阶段 3：实现有限 pattern 与 mask

### 目标

只实现可控、可验证的常用子集，复杂情况走局部栅格回退。

### 精确代码位置

1. 在 `src/pptx_designer/compiler/_paint.py:31-162` 的 paint server 体系中增加 pattern 定义解析入口；不要把 pattern 逻辑塞入 `_compiler.py` 的几何分支。
2. 在 `src/pptx_designer/compiler/_ir.py:64-84` 的 feature 分析中细分 `pattern_simple` 和 `pattern_complex`，判断依据必须写成可测试函数。
3. 新增 `src/pptx_designer/compiler/_pattern.py`，从第 1 行创建，负责 pattern tile 的边界、units、transform 和有限几何子集。
4. 在 `src/pptx_designer/compiler/_compiler.py:1012-1205` 的 `_render_shape()` 中，在 `_paint()` 之后调用 pattern policy；简单 pattern 使用重复原生形状，复杂 pattern 转局部 PNG。
5. 新增 `src/pptx_designer/compiler/_mask.py`，从第 1 行创建，仅支持单一几何遮罩和 alpha/luminance 两种明确模式；其余模式必须回退并记录原因。
6. 在 `src/pptx_designer/compiler/_compiler.py:928-950` 的子树分派中接入 mask handler，保证 mask 影响范围只覆盖其引用节点。
7. 在 `tests/test_svg_compiler_integration.py:211-237` 之后新增简单 pattern、复杂 pattern、几何 mask、luminance mask 和嵌套 mask 测试。

### 阶段验收

- 简单 pattern 在 PNG 中与 SVG 参考图保持可接受误差。
- 不支持的 pattern/mask 不得静默消失。
- 回退图片的边界框不允许超出原 SVG 节点的视觉范围。

## 阶段 4：实现常用 filter 与栅格回退

### 目标

支持高价值的少量滤镜，并为其他 filter 提供稳定的局部栅格回退。

### 精确代码位置

1. 新增 `src/pptx_designer/compiler/_raster.py`，从第 1 行创建，负责 SVG 子树栅格化、DPI、透明背景、边界扩展和临时资产生命周期。
2. 新增 `src/pptx_designer/compiler/_filters.py`，从第 1 行创建，仅实现 `feGaussianBlur`、常规 drop shadow 和有限 opacity/color transform；所有其他 primitive 必须返回明确的 unsupported reason。
3. 在 `src/pptx_designer/compiler/_compiler.py:479-486` 的 `_reject_unrenderable_features()` 中，把“必须失败”的 group opacity 与“可局部回退”的 filter/mask 分离。
4. 在 `src/pptx_designer/compiler/_compiler.py:928-950` 的 `_walk()` 中，为带 filter 的节点或最小祖先子树建立 fallback boundary。
5. 在 `src/pptx_designer/compiler/_compiler.py:421-446` 的 metrics 汇总中记录 rasterizer 名称、DPI、资产尺寸、fallback 节点数量和耗时。
6. 在 `tests/test_svg_compiler_integration.py:211-237` 之后增加 blur、drop shadow、多个 primitive、无效 filter reference 和 fallback 资产测试。

### 阶段验收

- blur 和 drop shadow 在 PNG 中可见且位置正确。
- 复杂 filter 可以局部栅格化，未受影响的兄弟节点仍然保持原生可编辑。
- 在没有可用栅格后端时必须明确失败，不得生成错误的空形状。

## 阶段 5：视觉回归与公共文档

### 精确代码位置

1. 新增 `tests/fixtures/svg/` 下的固定 SVG 样例，从目录第一个文件开始建立，不使用运行时生成的不可追踪输入。
2. 新增 `tests/test_svg_render_regression.py`，从第 1 行创建，负责调用既有 PPTX→PDF→PNG 渲染脚本并验证文件存在、页数和关键区域非空。
3. 在 `docs/svg-guide.md:1-96` 增加“支持矩阵、fallback 行为、资源安全和视觉验收”章节；插入位置为现有文档末尾第 97 行。
4. 在 `docs/api-reference.md` 当前 SVG API 章节末尾增加 policy、asset resolver 和 raster fallback 参数说明；编码前必须重新定位章节行号。

## 5. 依赖与风险控制

### 5.1 依赖策略

- 原生几何继续使用现有 `python-pptx`、`FreeformBuilder` 和布尔几何实现。
- 图片处理优先复用仓库已有图片处理能力，不重复引入第二套图片缩放/裁切逻辑。
- 栅格 fallback 必须使用明确的可选后端；后端不可用时返回诊断错误。
- 不允许从 SVG `href` 直接访问任意网络地址，避免 SSRF、不可重复构建和资源污染。

### 5.2 防止引入新问题

- 每一阶段只开放一个新 feature family。
- 所有新参数都必须向后兼容，默认行为保持现状。
- 新 renderer 不直接修改现有 native renderer 的 shape 逻辑。
- 所有复杂能力必须有“支持、近似、回退、拒绝”四种测试路径。
- 每次编码后必须先跑单元测试，再生成 PPTX，最后导出 PNG 检查；不能只依据 `shape_count` 判断成功。
- 不改变当前开放路径修复 `src/pptx_designer/compiler/_compiler.py:1236-1237` 和无填充路径修复 `src/pptx_designer/compiler/_compiler.py:1116`。

## 6. 预计工作量

| 阶段 | 预计时间 | 主要产出 |
|---|---:|---|
| 阶段 0 | 1–2 天 | 基线、线条回归、渲染样例 |
| 阶段 1 | 3–5 天 | policy、诊断、fallback 接口 |
| 阶段 2 | 3–5 天 | image 资源解析和 PPT 图片输出 |
| 阶段 3 | 5–10 天 | 简单 pattern、有限 mask、局部回退 |
| 阶段 4 | 10–20 天 | 栅格后端、常用 filter、子树回退 |
| 阶段 5 | 5–8 天 | 视觉回归、文档和跨渲染器验证 |

单人连续开发约 5–9 周。若只做 `image` 和基础 diagnostics，可压缩到 1–2 周；若要求复杂 filter 全部保持原生可编辑，则不建议承诺周期，因为 PPTX 原生效果与 SVG filter 语义并不等价。

## 7. 审批门槛

在你审批前，本方案只作为设计文档，不开始编码。审批时需要确认：

1. 是否接受“简单 SVG 原生可编辑、复杂 SVG 局部栅格回退”的总体策略。
2. 是否先实施阶段 0–2，再根据 image 结果决定是否继续 pattern/mask/filter。
3. 是否接受 PowerPoint 与 LibreOffice 对复杂效果存在渲染差异。
4. 是否允许引入一个明确的可选栅格化后端。

## 8. 可直接实施的工程规格

本节把方案细化到实现契约。编码时不得跳过本节的接口、状态和失败语义。

### 8.1 编译阶段顺序

`SVGCompiler.compile()` 必须保持以下固定顺序，新增 feature 不得在任意阶段提前产生 PPT shape：

1. 输入大小检查。
2. sanitizer 解析并移除危险节点。
3. CSS presentation attributes 展开。
4. 建立 `SVGIRDocument`。
5. 为每个 IR 节点计算 effective transform、visibility、opacity、paint reference 和 visual bounds。
6. 根据 feature policy 为节点选择 `NATIVE`、`NATIVE_APPROX`、`RASTER_FALLBACK` 或 `REJECT`。
7. 合并相邻且 policy 相同的 fallback 子树。
8. 先渲染原生节点，再渲染 fallback 资产；两者必须使用同一坐标映射。
9. 汇总 shape、资产、warning、error、feature level 和 metrics。
10. 执行 text collision 和 layout contract 检查。

新增功能不得在第 8 步之前直接调用 `slide.shapes.add_*`。这样可以避免已经生成原生对象后才发现父节点需要栅格化，造成重复或叠加。

### 8.2 Policy 数据契约

新增文件 `src/pptx_designer/compiler/_policy.py` 的第 1 行开始定义以下稳定概念：

- `RenderLevel`：只能包含 `NATIVE`、`NATIVE_APPROX`、`RASTER_FALLBACK`、`REJECT`。
- `FeatureDecision`：必须包含 feature 名称、render level、source node index、source id、reason 和是否可继续编译。
- `FallbackBoundary`：必须包含根节点 index、节点 index 集合、视觉边界框、包含的 feature 集合。
- `SVGFeaturePolicy`：必须提供按 feature 查询支持级别、生成决定、生成可读 reason 的方法。

默认 policy 必须保持现有行为兼容：基础几何和文字为 `NATIVE`，渐变为现有实现，clipPath/evenodd 为 `NATIVE_APPROX`，image/filter/mask/pattern 在未注入 renderer 时为 `REJECT` 而不是静默跳过。

### 8.3 SVGResult 扩展契约

当前 `src/pptx_designer/compiler/_compiler.py:298-330` 已有 `SVGResult`。编码时只允许在当前 `shape_count` 字段之后增加以下字段，不得重命名现有字段：

- `decisions`：按 source-order 排列的 `FeatureDecision` 列表。
- `fallback_assets`：每个资产的路径、mime、像素尺寸、边界框和来源节点。
- `rejected_features`：拒绝编译的 feature 及原因。

`fallback_shapes` 必须只保存实际插入 PPT 的图片 shape；不能保存临时 Pillow/渲染对象。`metrics["fallback_shape_count"]` 必须等于 `len(fallback_shapes)`，不能再固定写成 0。

## 9. 各复杂能力的精确支持子集

### 9.1 image

第一版只支持以下来源：

- `data:image/png;base64,...`
- `data:image/jpeg;base64,...`
- `data:image/webp;base64,...`，仅当当前图片库可解码时
- 由调用方显式提供的本地绝对路径

第一版拒绝：

- `http://`、`https://`、`file://` 自动访问；
- 未通过 asset resolver 的相对路径；
- 超过资源大小限制的图片；
- 无法识别 MIME 的内容。

坐标算法必须统一处理：

- 没有 `preserveAspectRatio` 时按当前 API 的 `contain` 策略；
- `xMidYMid meet` 映射为等比缩放并居中；
- `slice` 映射为等比放大并裁切；
- `none` 映射为非等比 stretch；
- `opacity` 和 `transform` 必须作用于最终图片 shape；
- 图片 bbox 必须在 viewBox 坐标转换后计算，不得用像素尺寸直接换算英寸。

### 9.2 pattern

第一版只支持：

- `patternUnits="userSpaceOnUse"`；
- pattern 内容只包含 rect、circle、ellipse、line、path、polygon、polyline；
- 不允许 pattern 嵌套 pattern；
- 不允许 pattern 内包含 text、image、filter、mask；
- patternTransform 只支持当前 Affine parser 已支持的变换；
- tile 数量必须受上限约束，超过上限转局部 PNG。

简单 pattern 的输出可使用重复原生 shape，但必须以 tile 边界裁切。无法保持 tile 边界的场景必须进入局部 raster fallback，不得重复铺满整张幻灯片。

### 9.3 mask

第一版只支持单节点引用的 mask：

- mask 内容只包含一个或多个基础几何节点；
- `maskUnits` 只支持 `userSpaceOnUse`；
- 支持 alpha mask 和 luminance mask；
- 不支持 mask 嵌套、mask 中 filter、mask 中 image；
- 不支持跨 SVG 文档引用。

mask 的视觉边界必须取“被遮罩节点 bbox 与 mask bbox 的交集”。边界扩展必须额外考虑 stroke-width 和 blur 扩展量，防止 fallback 图片边缘被裁掉。

### 9.4 filter

第一版只实现：

- `feGaussianBlur`：支持单输入、单输出；
- drop shadow：由 `feGaussianBlur` + `feOffset` + `feFlood` + `feComposite` + `feMerge` 组成的固定模式；
- 不实现任意 filter graph 的自动等价转换。

以下全部进入 raster fallback 或 REJECT：

- `feColorMatrix`；
- `feDisplacementMap`；
- lighting primitives；
- 多输入循环引用；
- 复杂 `feComposite` operator；
- filter region 超出安全限制的情况。

filter bbox 必须按 filter region 扩展。Gaussian blur 的边缘扩展必须由 stdDeviation 计算，并留出最小 3 倍标准差的安全边距，不能只使用原 shape bbox。

## 10. 精确文件改动清单

以下位置以当前工作树行号为准。每次编码前若前置改动导致行号漂移，必须先重新生成本清单。

### 10.1 `src/pptx_designer/compiler/_policy.py`

- 新文件，第 1 行创建。
- 只放 RenderLevel、FeatureDecision、FallbackBoundary、SVGFeaturePolicy 及纯决策函数。
- 不导入 python-pptx，不创建 shape，不读取文件。
- 该文件必须可被纯单元测试直接调用。

### 10.2 `src/pptx_designer/compiler/_assets.py`

- 新文件，第 1 行创建。
- 第 1–40 行：资源数据结构和资源限制。
- 第 41–120 行：data URI 解码、MIME 检查、大小检查。
- 第 121–200 行：显式本地路径 resolver。
- 禁止在此文件发起网络请求。

### 10.3 `src/pptx_designer/compiler/_raster.py`

- 新文件，第 1 行创建。
- 第 1–60 行：RasterAsset、RasterRenderError 和 renderer protocol。
- 第 61–150 行：SVG 子树转 PNG 的后端适配。
- 第 151–230 行：透明背景、DPI、bbox 扩展、临时文件清理。
- 第 231 行以后：只放后端注册和能力检测。

### 10.4 `src/pptx_designer/compiler/_pattern.py`

- 新文件，第 1 行创建。
- 第 1–80 行：pattern definition 解析和引用校验。
- 第 81–170 行：tile bounds 与 patternTransform 计算。
- 第 171–260 行：简单 pattern 的原生重复元素规划。
- 超过支持子集时返回结构化 decision，不直接抛通用异常。

### 10.5 `src/pptx_designer/compiler/_mask.py`

- 新文件，第 1 行创建。
- 第 1–70 行：mask 引用解析和 units 校验。
- 第 71–150 行：alpha/luminance mask 几何收集。
- 第 151–220 行：被遮罩节点和 mask 的交集 bbox 计算。
- 不在该文件创建 PPT shape；输出 mask render plan。

### 10.6 `src/pptx_designer/compiler/_filters.py`

- 新文件，第 1 行创建。
- 第 1–70 行：filter primitive 解析。
- 第 71–150 行：Gaussian blur 参数和 filter region 计算。
- 第 151–260 行：固定 drop shadow pattern 识别。
- 第 261 行以后：unsupported primitive 的结构化原因。

### 10.7 `src/pptx_designer/compiler/_ir.py`

- 当前 feature 常量在第 52–64 行，feature 分析在第 67–88 行。
- 在第 64 行 `_RASTER_ONLY_TAGS` 后增加 feature 分类常量。
- 在 `_features_for()` 当前第 67–88 行中增加 attribute-level 检测：`href`、`pattern`、`mask`、`filter`、`filter primitive`。
- 在 `SVGIRNode` 当前第 17–31 行中不增加可变字段；复杂计算结果应放在编译期 plan 中，保持 IR 不可变。

### 10.8 `src/pptx_designer/compiler/_sanitizer.py`

- 当前 `_STYLE_PROPS` 在第 22–44 行。
- 在当前第 44 行之后增加 `filter`、`mask`、`clip-path`、`fill`、`stroke` 引用值的格式校验，不把任意外部地址解析成文件路径。
- 在 `sanitize()` 当前第 118–156 行内，保持危险元素剥离先于资源解析。
- sanitizer 只规范化 XML，不加载图片、不栅格化、不访问网络。

### 10.9 `src/pptx_designer/compiler/_compiler.py`

- `SVGResult` 当前第 298–330 行：增加 diagnostics 字段。
- `SVGCompiler.__init__()` 当前第 336–350 行：增加可选 policy、asset resolver、rasterizer 参数，默认值必须维持现有行为。
- `compile()` 当前第 355–446 行：在第 381 行 IR 建立之后增加 plan 阶段；在第 421 行渲染完成之后汇总 decisions 和 fallback assets。
- `_feature_levels()` 当前第 559–577 行：改为使用 policy 结果，保留兼容字符串。
- `_walk()` 当前第 928–1010 行：只负责遍历和调用已决策的 renderer，不再对复杂节点直接跳过。
- `_render_shape()` 当前第 1012–1205 行：增加 pattern/mask/filter paint resolution 的调用点，但具体逻辑放到独立模块。
- `_add_freeform()` 当前第 1207–1268 行：保留开放路径修复；新增测试不得改变该方法的 close 条件。
- 新增 `_insert_raster_asset()` 必须紧接 `_add_freeform()` 当前结束位置之后，即当前第 1269 行附近；负责把 RasterAsset 放入 PPT，不负责生成资产。

### 10.10 `src/pptx_designer/tools/svg.py`

- 当前公共函数在第 23–94 行。
- 在第 23 行函数参数之后增加可选 policy、asset resolver 和 rasterizer 注入参数。
- 默认不打开网络访问、不改变现有 strict group opacity 行为。
- 文档字符串必须列出默认支持级别和 fallback 行为。

## 11. 测试实现规格

### 11.1 单元测试文件

新增以下文件，均从第 1 行创建：

- `tests/test_svg_policy.py`：测试四种 RenderLevel、decision reason 和 boundary 合并。
- `tests/test_svg_assets.py`：测试 data URI、非法协议、文件大小、MIME 和路径访问边界。
- `tests/test_svg_pattern.py`：测试简单 pattern、transform、嵌套拒绝和 tile 上限。
- `tests/test_svg_mask.py`：测试 alpha、luminance、bbox 交集和复杂 mask fallback。
- `tests/test_svg_filters.py`：测试 blur、固定 drop shadow、unsupported primitive 和 filter bbox 扩展。
- `tests/test_svg_render_regression.py`：测试 PPTX→PDF→PNG 的渲染产物。

### 11.2 现有测试修改位置

- `tests/test_svg_compiler_integration.py:211-237`：保留现有 unsupported tests，同时将断言从“跳过”升级为“明确 REJECT 或 RASTER_FALLBACK”。
- `tests/test_svg_compiler_integration.py:238-270`：RoundTrip 增加 fallback 图片存在且 PPTX 可重开的断言。
- `tests/test_svg_tools.py:153-211`：增加公共 `svg_chart()` 参数透传和默认兼容性测试。

### 11.3 视觉回归矩阵

每个 feature 至少准备以下三张参考：

1. 最小支持样例。
2. 边界条件样例。
3. 明确进入 fallback/REJECT 的复杂样例。

每个样例必须记录：SVG 输入、PPTX 输出、PDF 输出、PNG 输出、feature decisions、warnings、fallback 资产和人工检查结论。

视觉验收不能只判断文件存在，至少要检查：

- 预期区域存在非背景像素；
- 线条没有断裂或消失；
- 图片/回退对象没有越过 bbox；
- 透明区域没有出现白底；
- PowerPoint 和 LibreOffice 输出都能打开。

## 12. 任务拆分与依赖顺序

编码任务必须按以下顺序执行，不允许并行修改互相依赖的 renderer：

1. 基线测试与开放路径 PNG 回归。
2. Policy 和 diagnostics，不接入复杂 renderer。
3. Asset resolver，不接入网络，不改变现有图形。
4. image 原生 PPT 图片输出。
5. raster backend 与局部图片插入。
6. pattern 简单子集。
7. mask 有限子集。
8. filter blur/drop shadow。
9. 全量视觉回归和文档更新。

每个任务完成后必须独立通过当前阶段测试，才能进入下一任务。

## 13. 明确禁止的实现方式

- 不允许把整个 SVG 转成一张 PNG 作为默认方案。
- 不允许在异常时吞掉节点并只返回 `shape_count`。
- 不允许通过增大线宽、改变颜色或复制形状掩盖坐标错误。
- 不允许在 sanitizer 中执行网络下载或读取未授权本地路径。
- 不允许让 rasterizer 自己重新解释 SVG 坐标而绕过现有 `_to_inches()`。
- 不允许为了让测试通过而关闭视觉回归或删除 warning。
- 不允许在未增加对应测试的情况下扩展支持子集。

## 14. 审批后首个编码批次

审批通过后，首个批次只执行阶段 0 和阶段 1：

- 新增 `_policy.py`；
- 新增 `tests/test_svg_policy.py` 和 `tests/test_svg_render_regression.py`；
- 完善 `SVGResult` diagnostics；
- 固定现有开放路径和无填充路径回归；
- 不实现 image、pattern、mask、filter；
- 不修改现有图形脚本的视觉风格。

首个批次验收通过后，再审批是否进入 image 阶段。这样可以先验证架构和诊断链路，避免一次性引入多个复杂能力导致问题无法定位。

## 15. 方案自审结果与修订项

我对本方案按“能否直接交给开发者实施”的标准进行了复审，发现上一版存在以下不足，已在本版本补齐：

### 15.1 原方案缺少具体对象之间的调用契约

已增加 Policy、Asset、Raster、Pattern、Mask、Filter 五类模块的职责边界，并规定：Policy 只决策，Asset 只解析资源，Raster 只生成资产，Compiler 只负责调度和插入 PPT shape。这样可以避免把复杂逻辑继续堆到 `_compiler.py`。

### 15.2 原方案没有定义“成功但视觉错误”的处理方式

已增加四级结果：`NATIVE`、`NATIVE_APPROX`、`RASTER_FALLBACK`、`REJECT`。其中 `NATIVE_APPROX` 必须产生 warning，`REJECT` 必须进入 `rejected_features`，任何节点都不允许无 warning 地丢失。

### 15.3 原方案没有规定 fallback 后端

当前项目依赖中已有 Pillow 和 Shapely，但 Pillow 不能独立解析 SVG。实施阶段必须把 SVG rasterizer 定义为可选后端，不得假定 Pillow 能完成 SVG 渲染。

编码时必须在 `src/pptx_designer/compiler/_raster.py:61-150` 采用显式后端接口，并按以下顺序检测：

1. 调用方注入的 rasterizer；
2. 项目已安装且经过 capability check 的 SVG rasterizer；
3. 无可用后端时返回 `REJECT`，reason 必须包含缺失能力和安装/注入方式。

不得在运行时静默下载或自动安装 rasterizer。

### 15.4 原方案没有完整定义子树回退边界

fallback boundary 的根节点必须满足：

- 是第一个包含复杂 feature 的节点，或者是其最近的 SVG/g 祖先；
- 不跨越拥有独立 `id`、`clip-path`、`mask` 或 opacity 语义的兄弟子树；
- 视觉 bbox 必须包含 stroke、filter region、transform 和 clip 影响；
- 同一 boundary 内的节点只能生成一个临时资产，避免重复叠加。

如果一个复杂节点引用了外部 `<defs>`，boundary 必须把引用定义作为输入，但不能把 `<defs>` 本身插入 PPT。

### 15.5 原方案没有规定资源安全边界

已补充以下实施硬限制，位置固定为 `src/pptx_designer/compiler/_assets.py:1-200`：

- 只接受 data URI 和调用方显式允许的本地根目录；
- 拒绝所有网络协议、UNC 路径、路径穿越和符号链接逃逸；
- 限制单个资源字节数、解码后像素数和总资源数；
- 只允许 PNG、JPEG、WEBP 等明确 MIME；
- 任何资源错误都必须带 source id 和原始 href 摘要。

### 15.6 原方案没有解决图片透明度和 PPT 背景问题

`_insert_raster_asset()` 不得把透明 PNG 转成 RGB。必须保留 alpha 通道，并以无填充/透明背景方式插入 PPT 图片。PNG 资产的背景色不能从幻灯片背景猜测，否则换主题时会出现色块。

### 15.7 原方案对测试的要求仍然不够具体

已补充固定 fixture、边界样例和 PNG 验收矩阵。编码时每个新 feature 至少需要：

- 一个纯原生成功样例；
- 一个近似成功样例；
- 一个局部 fallback 样例；
- 一个明确 REJECT 样例；
- 一个 PowerPoint/LibreOffice 渲染检查样例。

测试不能只断言 `shape_count > 0`，还必须断言：feature decision、warning/rejected reason、fallback asset 数量、PPTX 重开和 PNG 非背景区域。

### 15.8 行号审查

当前文档中的生产文件行号已与当前工作树重新核对：

- `_compiler.py` 的 IR 建立在第 381 行；
- `_compiler.py` 的渲染汇总从第 421 行开始；
- `_compiler.py` 的开放路径保护在第 1236–1237 行；
- `_compiler.py` 的无填充路径调用在第 1116 行；
- `SVGResult` 在第 298–330 行；
- `_ir.py` 的 feature 常量和判断在第 52–88 行。

所有“新增文件第 N 行”的描述指新增文件自身的稳定行号；所有“修改现有文件第 N 行”的描述指当前工作树锚点。编码前若发生行号漂移，必须先暂停编码、重新核对并更新本文件。

### 15.9 审查结论

本方案现在具备实施所需的模块边界、调用顺序、支持范围、失败语义、资源安全和测试门槛，但仍然坚持分阶段开发。审批通过后不能直接实现四类复杂能力，必须先完成阶段 0 和阶段 1，并提交测试结果和 PNG 基线供下一阶段审批。
