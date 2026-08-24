# SVG P2b 深度审查与真实 PPTX 验证

> 审查日期：2026-08-24
> 范围：`src/pptx_designer/compiler/` 的 P2b 增量 IR、CSS/文本链路及真实 PPTX 输出
> 状态更新：报告所列 P0/P1/P2 已修复并完成严格回归。P2b 的“只读 IR + 报告接入”实现可用；`group opacity` 在尚无 raster fallback 前会安全拒绝，而不会产出错误的原生形状。

## 一、执行的验证

- 完整回归：`pytest -q`，129 项通过；
- 静态检查：新增 IR 模块和 IR/集成测试通过；`tests/test_compiler/test_css.py` 存在 3 项既有 import 排序告警；全量 `_compiler.py` 另有既有格式/命名告警；
- 真实文件：用 `scripts/svg_p2b_smoke.py` 生成两页 PPTX，覆盖 CSS 变量/class、渐变、`clipPath`、`use`、文本、元素 opacity、隐藏节点、`filter` 能力识别及 `image` 告警；
- 可打开性：生成文件可由 `python-pptx` 重新打开，OOXML 中有 2 个 slide XML；LibreOffice 无错误地导出为 2 页 PDF；
- 视觉检查：将 PDF 按 144 DPI 渲染为 PNG，逐页检查版面。

产物：

- `output/svg-p2b-real-smoke.pptx`
- `output/svg-p2b-real-smoke.pdf`
- `output/svg-p2b-render/slide-1.png`
- `output/svg-p2b-render/slide-2.png`

## 二、发现的问题与修复结果

| 优先级 | 问题 | 证据与影响 |
|---|---|---|
| P0 | 文本宽度测量与实际输出字号不一致 | 已修复：找不到真实字体时不再使用 Pillow 固定字号默认字体，改用按目标字号估算的测量器。真实 PDF 中逐词/逐字换行消失。 |
| P1 | `<g opacity>` 未按 SVG 组合语义应用 | 已修复为安全失败：IR 标记 `group_opacity`，编译在创建任何 shape 前抛出要求 raster fallback 的明确错误；不再静默输出全不透明结果。 |
| P1 | 节点资源上限在 IR 构建之后才检查 | 已修复：节点数、路径命令数和新增树深度限制均在 `build_svg_ir()` 前检查。 |
| P2 | `source_index` 对嵌套重复 id 的顺序与源顺序相反 | 已修复：节点登记改为递归子节点前执行，重复 id 按 preorder/source order 返回。 |
| P2 | `tspan` 字号没有使用 SVG→PPT 的比例缩放 | 已修复：所有 tspan run/outline/spacer 统一使用 SVG→PPT point scale。 |

## 三、真实 PPTX 结果

结构性结果是正常的：两页 PPTX 被重新打开后 shape 数与编译报告一致；`<image>` 被跳过并报告 warning；`filter` 被 IR 标记为 `RASTER_FALLBACK_CANDIDATE`。

修复后视觉结果合格：两页文本均正常可读，无逐词/逐字换行、裁切或乱码；示例只保留预期的 `<image>` 跳过 warning。标题因版面宽度自然换为两行，但未发生非预期词内断行。

## 四、P2b 本身的完成度

已确认的实现：

- `SVGIRNode` 不暴露可变 XML；
- IR 在 CSS 样式物化和 sanitizer 之后构建；
- 报告包含 `ir_document`、`ir_node_count`、`ir_build_ms`；
- 原有 `_walk()` 继续作为渲染后端，P2b 未意外切换渲染模型；
- IR 能提前标记 `image/filter/mask/pattern/marker` 为 raster fallback 候选；
- `use`、隐藏节点及 source-to-output 映射的现有回归测试仍通过。

因此，P2b 的架构方向正确，但不能因 129 项单元/集成测试全部通过就认为复杂 SVG 输出已经稳定：这些测试没有视觉回归断言，也没有对 group opacity、字体回退、tspan 缩放或限制检查顺序建模。

## 五、持续门禁

- 每次变更运行 `pytest -q`、目标模块 `ruff check` 和 `git diff --check`；
- 对文本、`use`、渐变、裁剪和 capability report 变更，运行 `scripts/svg_p2b_smoke.py`，重新打开 PPTX 并以 LibreOffice 导出 PDF 做视觉检查；
- Phase 3a 实现 raster fallback 后，将 `group_opacity` 从安全拒绝升级为实际降级，并补充像素/视觉 golden 样本。
