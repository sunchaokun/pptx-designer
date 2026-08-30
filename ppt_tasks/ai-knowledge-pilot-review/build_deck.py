"""Build an editable management review deck for the theme-integration evaluation.

All business figures are deliberately illustrative.  The deck verifies the
locked warm-editorial theme in a realistic Chinese management-review scenario.
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.renderer.theme import ThemeComposer
from pptx_designer.tools.cards import kpi_card
from pptx_designer.tools.layout import page_header, page_number, top_bar
from pptx_designer.tools.shapes import arrow, oval, rect, rrect
from pptx_designer.tools.text import multiline, text

TASK_ROOT = Path(__file__).parent
OUTPUT = TASK_ROOT / "output" / "ai-knowledge-pilot-review.pptx"
THEME = ThemeComposer().compose(
    style="warm-elegant",
    palette="golden-luxury",
    fonts="serif-editorial",
    decoration="gold-trim",
    layout="centered",
    seed=17,
)


def add_base(prs, number: int, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background")
    top_bar(slide, "accent", height=0.035)
    page_header(slide, title, subtitle)
    page_number(slide, number, 8, style="gold")
    text(slide, 0.65, 7.04, 2.8, 0.22, "演示数据 · 主题效果评估案例", font_size=9, color="text_muted")
    return slide


def card(slide, x, y, w, h, title, body, accent="accent"):
    rrect(slide, x, y, w, h, "card", line="border")
    rect(slide, x, y, w, 0.055, accent)
    text(slide, x + 0.22, y + 0.23, w - 0.44, 0.34, title, font_size=17, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
    multiline(slide, x + 0.22, y + 0.72, w - 0.44, h - 0.85, body, font_size=12, color="text_body", line_spacing=4)


def cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background")
    top_bar(slide, "accent", height=0.04)
    for name, args in (
        ("Background Decoration 1", (10.2, -0.9, 4.7, 4.7, "primary")),
        ("Background Decoration 2", (11.2, 0.2, 3.2, 3.2, "accent")),
        ("Background Decoration 3", (-1.4, 5.7, 3.4, 3.4, "secondary")),
    ):
        ornament = oval(slide, *args)
        ornament.name = name
    rect(slide, 0.8, 1.25, 1.45, 0.055, "accent")
    text(slide, 0.8, 1.55, 8.4, 1.55, "企业 AI 知识助手\n试点复盘", font_size=42, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
    text(slide, 0.83, 3.3, 7.8, 0.42, "从“能回答”走向“可运营的知识供给能力”", font_size=20, color="text_body")
    rrect(slide, 0.83, 4.12, 2.25, 0.42, "card", line="border")
    text(slide, 1.0, 4.23, 1.9, 0.18, "管理层决策简报 · 演示数据", font_size=10, color="text_muted", align="center")
    text(slide, 0.83, 6.72, 3.0, 0.22, "2026 / 试点第 6 周", font_size=11, color="text_muted")


def executive_summary(prs):
    slide = add_base(prs, 2, "建议：批准 12 周扩围", "试点已证明价值，但规模化必须把知识质量与人工复核一起产品化")
    text(slide, 0.8, 1.65, 3.2, 0.32, "三条管理层结论", font_size=13, color="accent", bold=True)
    card(slide, 0.8, 2.1, 3.75, 2.55, "01 价值已被验证", ["首次响应时间显著缩短", "一线采用率达到 72%", "高频知识场景贡献最大"])
    card(slide, 4.78, 2.1, 3.75, 2.55, "02 质量不能后置", ["必须标注知识来源", "低置信答案进入人工确认", "每周复盘失效知识"], accent="secondary")
    card(slide, 8.76, 2.1, 3.75, 2.55, "03 决策请求", ["批准扩围至 3 个服务团队", "投入 1 名知识运营负责人", "以 12 周里程碑决定长期预算"], accent="primary")
    rrect(slide, 0.8, 5.25, 11.7, 0.9, "surface", line="border")
    text(slide, 1.05, 5.52, 2.0, 0.2, "推荐动作", font_size=12, color="accent", bold=True)
    text(slide, 3.0, 5.45, 8.9, 0.32, "以“可审计、可复盘、可退出”为条件，进入受控扩围。", font_size=18, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])


def problem(prs):
    slide = add_base(prs, 3, "问题不在“缺人”，而在“找不到可信答案”", "一线服务人员每天重复地在多个系统间检索、判断和补洞")
    labels = [("知识分散", "答案散落在 FAQ、工单、群聊和旧文档", "primary"), ("判断重复", "同一问题被不同人员反复确认与转交", "accent"), ("更新滞后", "政策与产品变化无法及时回流到一线", "secondary")]
    for index, (title, body, color) in enumerate(labels):
        x = 0.85 + index * 4.12
        oval(slide, x, 2.1, 0.62, 0.62, color)
        text(slide, x + 0.18, 2.22, 0.25, 0.24, f"{index + 1}", font_size=12, color="on_primary", bold=True, align="center")
        text(slide, x, 2.95, 3.0, 0.35, title, font_size=21, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
        multiline(slide, x, 3.52, 3.2, 0.85, [body], font_size=13, color="text_body")
        if index < 2:
            arrow(slide, x + 3.25, 3.15, 0.45, 0.18, "border")
    rect(slide, 0.85, 5.28, 11.55, 0.02, "border")
    text(slide, 0.85, 5.58, 2.2, 0.25, "业务后果", font_size=12, color="accent", bold=True)
    text(slide, 3.05, 5.5, 8.9, 0.42, "客户等待更久，一线更依赖经验，管理层看不见知识缺口。", font_size=19, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])


def results(prs):
    slide = add_base(prs, 4, "6 周试点：速度与解决质量同时改善", "覆盖 48 名一线人员、3 个高频咨询场景；以下均为演示数据")
    text(slide, 0.9, 1.65, 4.0, 0.28, "试点前后对比", font_size=13, color="accent", bold=True)
    comparisons = [("首次响应", "11 分钟", "4 分钟", 0.78, 0.28), ("一次解决率", "61%", "74%", 0.61, 0.74), ("知识查找", "8 分钟", "3 分钟", 0.68, 0.25)]
    for index, (label, before, after, before_w, after_w) in enumerate(comparisons):
        y = 2.25 + index * 1.05
        text(slide, 0.9, y, 1.4, 0.25, label, font_size=13, color="text_body", bold=True)
        rrect(slide, 2.45, y + 0.02, 3.0, 0.18, "surface")
        rrect(slide, 2.45, y + 0.02, 3.0 * before_w, 0.18, "secondary")
        text(slide, 5.62, y - 0.02, 0.8, 0.22, before, font_size=12, color="text_muted")
        rrect(slide, 6.65, y + 0.02, 3.0, 0.18, "surface")
        rrect(slide, 6.65, y + 0.02, 3.0 * after_w, 0.18, "accent")
        text(slide, 9.82, y - 0.02, 0.8, 0.22, after, font_size=12, color="text_dark", bold=True)
    text(slide, 2.45, 5.55, 1.1, 0.18, "试点前", font_size=10, color="text_muted")
    text(slide, 6.65, 5.55, 1.1, 0.18, "试点后", font_size=10, color="accent", bold=True)
    kpi_card(slide, 10.4, 1.8, 2.0, 1.5, "72%", "周活跃采用率", "+18pp", True)
    kpi_card(slide, 10.4, 3.55, 2.0, 1.5, "4.6/5", "一线满意度", "+0.8", True)
    rrect(slide, 0.9, 6.05, 11.5, 0.48, "card", line="border")
    text(slide, 1.15, 6.14, 10.8, 0.25, "改善来自更快地定位可信知识，而不是减少人工判断。", font_size=13, color="text_body", align="center")


def workflow(prs):
    slide = add_base(prs, 5, "工作流：检索、建议、确认、回流形成闭环", "助手把知识工作拆解为可观测的步骤，而不是替代责任人")
    steps = [("01", "检索", "定位来源", "secondary"), ("02", "建议", "生成候选答复", "accent"), ("03", "确认", "人工判断与发送", "primary"), ("04", "回流", "沉淀缺口与新知识", "accent")]
    for index, (num, title, desc, color) in enumerate(steps):
        x = 0.8 + index * 3.1
        rrect(slide, x, 2.35, 2.35, 1.9, "card", line="border")
        oval(slide, x + 0.18, 2.58, 0.45, 0.45, color)
        text(slide, x + 0.12, 2.67, 0.42, 0.2, num, font_size=9, color="on_primary", bold=True, align="center")
        text(slide, x + 0.2, 3.25, 1.9, 0.32, title, font_size=20, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
        text(slide, x + 0.2, 3.75, 1.9, 0.28, desc, font_size=12, color="text_body")
        if index < 3:
            arrow(slide, x + 2.43, 3.12, 0.42, 0.18, "border")
    rrect(slide, 2.05, 5.25, 9.2, 0.7, "surface", line="border")
    text(slide, 2.35, 5.48, 1.75, 0.2, "责任边界", font_size=12, color="accent", bold=True)
    text(slide, 4.15, 5.42, 6.7, 0.28, "模型提供建议；人负责判断；运营团队负责让知识持续变好。", font_size=15, color="text_dark", bold=True)


def operations(prs):
    slide = add_base(prs, 6, "运营证据：采用率持续上升，价值集中在高频场景", "第 6 周日均使用 35 次；运营团队每周复盘未命中问题")
    text(slide, 0.9, 1.65, 4.0, 0.28, "每周活跃采用率", font_size=13, color="accent", bold=True)
    values = [28, 41, 49, 58, 66, 72]
    for index, value in enumerate(values):
        x = 1.1 + index * 0.77
        rect(slide, x, 5.4 - value * 0.035, 0.42, value * 0.035, "accent")
        text(slide, x - 0.05, 5.53, 0.52, 0.22, f"W{index + 1}", font_size=9, color="text_muted", align="center")
    rect(slide, 0.95, 5.42, 4.75, 0.02, "border")
    text(slide, 1.05, 1.9, 1.5, 0.62, "72%", font_size=36, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
    text(slide, 2.62, 2.32, 2.4, 0.2, "第 6 周活跃采用率", font_size=12, color="text_muted")
    rrect(slide, 6.35, 1.7, 5.8, 3.9, "card", line="border")
    text(slide, 6.7, 2.0, 3.2, 0.28, "价值集中场景", font_size=17, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
    scenes = [("订单与退款", 0.84, "84%"), ("账号与权限", 0.63, "63%"), ("产品配置", 0.51, "51%")]
    for index, (label, ratio, value) in enumerate(scenes):
        y = 2.75 + index * 0.72
        text(slide, 6.7, y, 1.25, 0.2, label, font_size=11, color="text_body")
        rrect(slide, 8.15, y + 0.02, 2.8, 0.2, "surface")
        rrect(slide, 8.15, y + 0.02, 2.8 * ratio, 0.2, "accent")
        text(slide, 11.05, y, 0.7, 0.22, value, font_size=11, color="text_dark", bold=True, align="right")
    text(slide, 6.7, 5.05, 4.8, 0.22, "结论：先扩围高频、规则清晰的知识场景。", font_size=12, color="accent", bold=True)


def safeguards(prs):
    slide = add_base(prs, 7, "扩围的前提：把质量控制嵌入每一次回答", "风险不靠“提醒模型”，而靠可执行的规则、阈值和复盘节奏")
    safeguards = [("来源可见", "每个建议附带知识来源与更新时间", "100% 可追溯", "primary"), ("低置信复核", "置信度不足时自动进入人工确认", "< 0.78 必复核", "accent"), ("知识周复盘", "将未命中与纠错沉淀为运营待办", "每周闭环", "secondary")]
    for index, (title, body, threshold, color) in enumerate(safeguards):
        x = 0.9 + index * 4.1
        rrect(slide, x, 2.0, 3.55, 3.2, "card", line="border")
        rect(slide, x, 2.0, 3.55, 0.07, color)
        text(slide, x + 0.25, 2.42, 2.9, 0.34, title, font_size=20, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
        multiline(slide, x + 0.25, 3.08, 2.92, 0.75, [body], font_size=13, color="text_body")
        rrect(slide, x + 0.25, 4.25, 2.45, 0.43, "surface")
        text(slide, x + 0.4, 4.37, 2.1, 0.18, threshold, font_size=11, color=color, bold=True, align="center")
    text(slide, 0.95, 5.85, 11.2, 0.34, "可控扩围的本质：让每个答案都有“证据、边界与改进入口”。", font_size=18, color="text_dark", bold=True, align="center", font_name=THEME["typography"]["heading"])


def decision(prs):
    slide = add_base(prs, 8, "需要的不是一次性预算，而是一段可验证的 12 周承诺", "批准扩围至 3 个团队；每 4 周依据质量、采用和业务结果重新决策")
    milestones = [("第 0–4 周", "扩围与知识清理", "覆盖 3 个团队"), ("第 5–8 周", "运营机制稳定", "采用率 ≥ 70%"), ("第 9–12 周", "规模化评估", "决定长期预算")]
    for index, (period, title, proof) in enumerate(milestones):
        x = 0.95 + index * 4.1
        oval(slide, x, 2.15, 0.55, 0.55, "accent")
        text(slide, x + 0.17, 2.29, 0.2, 0.2, str(index + 1), font_size=10, color="on_primary", bold=True, align="center")
        text(slide, x + 0.75, 2.18, 2.8, 0.2, period, font_size=11, color="accent", bold=True)
        text(slide, x + 0.75, 2.62, 2.85, 0.32, title, font_size=18, color="text_dark", bold=True, font_name=THEME["typography"]["heading"])
        text(slide, x + 0.75, 3.15, 2.85, 0.24, proof, font_size=12, color="text_body")
        if index < 2:
            rect(slide, x + 3.35, 2.4, 0.75, 0.025, "border")
    rrect(slide, 0.95, 5.05, 11.45, 1.12, "primary", line="primary")
    text(slide, 1.3, 5.34, 2.0, 0.25, "今日决策", font_size=12, color="on_primary", bold=True)
    text(slide, 3.35, 5.27, 8.3, 0.36, "批准 12 周受控扩围，并以护栏指标决定下一阶段投入。", font_size=20, color="on_primary", bold=True, font_name=THEME["typography"]["heading"])


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation(theme=THEME)
    cover(prs)
    executive_summary(prs)
    problem(prs)
    results(prs)
    workflow(prs)
    operations(prs)
    safeguards(prs)
    decision(prs)
    prs.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
