"""Story Planner — content structure generation for FreeStyle mode.

Generates high-quality page structures based on:
- Query keyword analysis
- Industry-specific templates
- Design knowledge base (data/ module)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PagePlan:
    """Plan for a single slide."""

    position: int
    goal: str  # hook, problem, solution, features, data, code, exercise, cta, content, overview
    emotion: str = "confidence"
    title: str = ""
    subtitle: str = ""
    bullets: list[str] = field(default_factory=list)
    sparkline: str = "proof"


@dataclass
class StoryPlan:
    """Complete presentation plan."""

    strategy: str
    total_slides: int
    pages: list[PagePlan] = field(default_factory=list)
    title: str = ""
    emotion_arc: str = ""
    product_type: str = ""
    style_hint: str = ""


# ── Industry-specific templates ─────────────────────────────────────

_TEMPLATES: dict[str, dict[str, Any]] = {
    "pitch": {
        "name": "Startup Pitch Deck",
        "total": 8,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": "Revolutionizing the Industry"},
            {
                "goal": "problem",
                "title": "The Problem",
                "bullets": [
                    "Current solutions are slow and expensive",
                    "Users waste 10+ hours per week on manual tasks",
                    "Market growing 40% YoY with no good solution",
                ],
            },
            {
                "goal": "solution",
                "title": "Our Solution",
                "bullets": [
                    "AI-powered automation reduces time by 90%",
                    "One-click integration with existing tools",
                    "Enterprise-grade security and compliance",
                ],
            },
            {
                "goal": "features",
                "title": "Key Features",
                "bullets": [
                    "智能分析引擎",
                    "实时协作平台",
                    "自动化工作流",
                ],
            },
            {
                "goal": "data",
                "title": "Market Opportunity",
                "bullets": [
                    "TAM: $50B global market",
                    "SAM: $12B serviceable market",
                    "SOM: $2B obtainable in 3 years",
                ],
            },
            {
                "goal": "content",
                "title": "Traction",
                "bullets": [
                    "10,000+ active users",
                    "$2M ARR, 15% MoM growth",
                    "95% customer retention rate",
                ],
            },
            {
                "goal": "content",
                "title": "Team",
                "bullets": [
                    "CEO: 15 years industry experience",
                    "CTO: Former Google engineer",
                    " advisors: Top VCs and industry leaders",
                ],
            },
            {"goal": "cta", "title": "Join Our Journey", "subtitle": "Contact: hello@startup.com"},
        ],
        "style_hint": "professional",
    },
    "report": {
        "name": "Business Report",
        "total": 6,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": "Quarterly Review"},
            {
                "goal": "data",
                "title": "Key Metrics",
                "bullets": [
                    "Revenue: $12.8M (+23% YoY)",
                    "Customers: 2,500 (+15% QoQ)",
                    "NPS: 72 (Industry avg: 45)",
                ],
            },
            {
                "goal": "content",
                "title": "Performance Analysis",
                "bullets": [
                    "Strong growth in enterprise segment",
                    "Product adoption exceeding targets",
                    "Operational efficiency improved 18%",
                ],
            },
            {
                "goal": "content",
                "title": "Challenges & Risks",
                "bullets": [
                    "Supply chain delays in APAC region",
                    "Increased competition in mid-market",
                    "Talent acquisition in key roles",
                ],
            },
            {
                "goal": "content",
                "title": "Strategic Initiatives",
                "bullets": [
                    "Launch v2.0 with AI features",
                    "Expand to European market",
                    "Build partner ecosystem",
                ],
            },
            {"goal": "cta", "title": "Next Steps", "subtitle": "Questions? Let's discuss."},
        ],
        "style_hint": "corporate",
    },
    "product": {
        "name": "Product Launch",
        "total": 7,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": "Introducing the Future"},
            {
                "goal": "problem",
                "title": "Why This Matters",
                "bullets": [
                    "Existing tools create friction",
                    "Users demand better experience",
                    "Market gap waiting to be filled",
                ],
            },
            {
                "goal": "solution",
                "title": "Introducing Our Product",
                "bullets": [
                    "Seamless integration in 5 minutes",
                    "AI-powered recommendations",
                    "Beautiful, intuitive interface",
                ],
            },
            {
                "goal": "features",
                "title": "Core Capabilities",
                "bullets": [
                    "智能推荐系统",
                    "实时数据分析",
                    "多平台同步",
                ],
            },
            {
                "goal": "data",
                "title": "Early Results",
                "bullets": [
                    "3x faster than competitors",
                    "98% uptime guaranteed",
                    "SOC 2 Type II certified",
                ],
            },
            {
                "goal": "content",
                "title": "Customer Stories",
                "bullets": [
                    '"Game changer for our team" - TechCrunch',
                    '"Reduced costs by 40%" - Fortune 500',
                    '"Best tool we\'ve adopted this year" - Startup CEO',
                ],
            },
            {"goal": "cta", "title": "Get Started Today", "subtitle": "Free 14-day trial"},
        ],
        "style_hint": "modern",
    },
    "education": {
        "name": "Educational Course",
        "total": 8,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": "Learning Path"},
            {
                "goal": "overview",
                "title": "Course Overview",
                "bullets": [
                    "Duration: 8 weeks",
                    "Level: Intermediate to Advanced",
                    "Format: Video + Hands-on Labs",
                ],
            },
            {
                "goal": "content",
                "title": "Module 1: Foundations",
                "bullets": [
                    "Core concepts and terminology",
                    "Setting up your environment",
                    "First project walkthrough",
                ],
            },
            {
                "goal": "content",
                "title": "Module 2: Deep Dive",
                "bullets": [
                    "Advanced techniques",
                    "Best practices and patterns",
                    "Real-world case studies",
                ],
            },
            {
                "goal": "content",
                "title": "Module 3: Application",
                "bullets": [
                    "Building production systems",
                    "Performance optimization",
                    "Deployment strategies",
                ],
            },
            {
                "goal": "content",
                "title": "Module 4: Mastery",
                "bullets": [
                    "Architecture patterns",
                    "Scaling and maintenance",
                    "Future trends",
                ],
            },
            {
                "goal": "content",
                "title": "Learning Outcomes",
                "bullets": [
                    "Certificate of completion",
                    "Portfolio projects",
                    "Community access",
                ],
            },
            {"goal": "cta", "title": "Enroll Now", "subtitle": "Limited seats available"},
        ],
        "style_hint": "educational",
    },
    "technical": {
        "name": "Technical Presentation",
        "total": 7,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": "Technical Deep Dive"},
            {
                "goal": "overview",
                "title": "Architecture Overview",
                "bullets": [
                    "Microservices architecture",
                    "Event-driven communication",
                    "Cloud-native deployment",
                ],
            },
            {
                "goal": "features",
                "title": "Core Components",
                "bullets": [
                    "API Gateway",
                    "Message Queue",
                    "Data Pipeline",
                ],
            },
            {
                "goal": "code",
                "title": "Implementation",
                "bullets": [
                    "# Example code block",
                    "def process_data(input):",
                    "    return transform(input)",
                ],
            },
            {
                "goal": "data",
                "title": "Performance Metrics",
                "bullets": [
                    "Latency: p50=12ms, p99=45ms",
                    "Throughput: 10,000 req/s",
                    "Uptime: 99.99%",
                ],
            },
            {
                "goal": "content",
                "title": "Deployment Strategy",
                "bullets": [
                    "Kubernetes orchestration",
                    "Blue-green deployment",
                    "Automated rollback",
                ],
            },
            {"goal": "cta", "title": "Questions?", "subtitle": "Documentation: docs.example.com"},
        ],
        "style_hint": "tech",
    },
    "minimal": {
        "name": "Minimal Presentation",
        "total": 5,
        "structure": [
            {"goal": "hook", "title": "{query}", "subtitle": ""},
            {
                "goal": "content",
                "title": "Key Points",
                "bullets": [
                    "Point one",
                    "Point two",
                    "Point three",
                ],
            },
            {
                "goal": "content",
                "title": "Details",
                "bullets": [
                    "Elaboration on point one",
                    "Supporting data",
                ],
            },
            {
                "goal": "content",
                "title": "Summary",
                "bullets": [
                    "Main takeaway",
                ],
            },
            {"goal": "cta", "title": "Thank You", "subtitle": ""},
        ],
        "style_hint": "minimal",
    },
}

# ── Keyword → Template mapping ──────────────────────────────────────

_KEYWORD_MAP: list[tuple[list[str], str]] = [
    (["融资", "路演", "investor", "pitch", "seed", "series", "startup", "创业"], "pitch"),
    (["报告", "汇报", "report", "annual", "quarterly", "review", "季度", "年度"], "report"),
    (["产品", "发布", "product", "launch", "introduce", "介绍"], "product"),
    (["教育", "课程", "education", "course", "lesson", "培训", "training"], "education"),
    (["技术", "架构", "technical", "architecture", "系统", "system", "api", "code"], "technical"),
    (["简约", "简单", "minimal", "simple", "basic"], "minimal"),
]


def _detect_template(query: str) -> str:
    """Detect the best template based on query keywords."""
    q = query.lower()
    for keywords, template_name in _KEYWORD_MAP:
        if any(kw in q for kw in keywords):
            return template_name
    return "minimal"


def _expand_title(template_title: str, query: str) -> str:
    """Expand template title with query."""
    return template_title.replace("{query}", query)


class StoryPlanner:
    """Generates presentation structure from natural language query."""

    def plan(
        self,
        query: str,
        strategy_override: str | None = None,
        slide_count_override: int | None = None,
    ) -> StoryPlan:
        """Plan a presentation from a query.

        Args:
            query: Natural language description
            strategy_override: Force a specific template
            slide_count_override: Override slide count

        Returns:
            StoryPlan with pages
        """
        # Detect template
        template_name = strategy_override or _detect_template(query)
        template = _TEMPLATES.get(template_name, _TEMPLATES["minimal"])

        # Build pages
        structure = template["structure"]
        total = slide_count_override or template["total"]

        # Adjust slide count
        if total < len(structure):
            structure = structure[:total]
        elif total > len(structure):
            # Add content pages to fill
            while len(structure) < total:
                structure.append(
                    {
                        "goal": "content",
                        "title": f"Additional Point {len(structure) - template['total'] + 1}",
                        "bullets": ["Detail 1", "Detail 2", "Detail 3"],
                    }
                )

        # Create PagePlan objects
        pages = []
        for i, page_def in enumerate(structure):
            page = PagePlan(
                position=i + 1,
                goal=page_def.get("goal", "content"),
                emotion=_goal_to_emotion(page_def.get("goal", "content")),
                title=_expand_title(page_def.get("title", ""), query),
                subtitle=page_def.get("subtitle", ""),
                bullets=page_def.get("bullets", []),
                sparkline="hook" if i == 0 else ("action" if i == len(structure) - 1 else "proof"),
            )
            pages.append(page)

        return StoryPlan(
            strategy=template["name"],
            total_slides=len(pages),
            pages=pages,
            title=_expand_title(structure[0].get("title", query), query),
            emotion_arc=" → ".join(p.emotion for p in pages),
            product_type=template_name,
            style_hint=template.get("style_hint", "professional"),
        )


def _goal_to_emotion(goal: str) -> str:
    """Map goal to emotional tone."""
    emotions = {
        "hook": "curiosity",
        "problem": "urgency",
        "solution": "hope",
        "features": "confidence",
        "data": "trust",
        "code": "clarity",
        "exercise": "engagement",
        "cta": "excitement",
        "content": "confidence",
        "overview": "clarity",
    }
    return emotions.get(goal, "confidence")
