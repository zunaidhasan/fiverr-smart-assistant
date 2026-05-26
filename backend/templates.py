from typing import Dict, List, Optional
from models import SituationType


# Tone definitions
TONES = {
    "professional": "Professional and formal, focusing on your expertise and reliability.",
    "friendly": "Warm and approachable, building rapport while staying professional.",
    "enthusiastic": "Energetic and excited about the project opportunity.",
    "consultative": "Advisory tone, positioning yourself as an expert solving their problem.",
    "urgent": "Quick, direct, and action-oriented for time-sensitive situations.",
    "confident": "Bold and assured, highlighting past success and capability.",
}


class ReplyTemplate:
    """A structured reply template with placeholders for personalization."""

    def __init__(
        self,
        name: str,
        situation_type: SituationType,
        subject: str,
        body_template: str,
        tone: str,
        questions: List[str],
        strength: float = 0.8,
    ):
        self.name = name
        self.situation_type = situation_type
        self.subject = subject
        self.body_template = body_template
        self.tone = tone
        self.questions = questions
        self.strength = strength

    def personalize(self, **kwargs) -> str:
        """Fill in template placeholders with provided values."""
        body = self.body_template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in body:
                body = body.replace(placeholder, str(value))
        return body


# --- Template Definitions ---

TECHNICAL_PROPOSAL = ReplyTemplate(
    name="technical_proposal",
    situation_type=SituationType.TECHNICAL_PROJECT,
    subject="Technical Proposal for {project_title}",
    body_template="""Hi {buyer_name},

Thank you for reaching out! I've reviewed your requirements for {project_title} and I'm confident I can deliver exactly what you need.

I have extensive experience in {category}, including {reference_project}. Here's my approach:

1. **Understanding Phase**: I'll start by clarifying all technical requirements and edge cases
2. **Development**: Build the solution with clean, well-documented code
3. **Testing**: Thorough testing to ensure everything works perfectly
4. **Delivery**: Hand off with documentation and a demo

**What I need from you:**
{questions_text}

**Estimated Quote:** ${estimated_budget} - ${estimated_budget_max}
**Timeline:** {timeline} days

I'm available to start {start_date}. Let me know if you'd like to discuss further!

Best regards,
{freelancer_name}""",
    tone="professional",
    questions=[
        "Do you have any specific technical requirements or preferences?",
        "Is there a deadline or timeline you're working with?",
        "Do you have any existing code or documentation I should review?",
        "What's your budget range for this project?",
    ],
    strength=0.9,
)


CREATIVE_PROPOSAL = ReplyTemplate(
    name="creative_proposal",
    situation_type=SituationType.CREATIVE_PROJECT,
    subject="Creative Concept for {project_title}",
    body_template="""Hi {buyer_name},

I love your vision for {project_title}! This is right up my alley.

I've worked on similar projects like {reference_project}, where I delivered {reference_outcome}. I believe in creating work that not only looks great but also achieves your goals.

**My creative process:**
1. Research & inspiration gathering
2. Concept development (2-3 initial directions)
3. Refinement based on your feedback
4. Final delivery in your preferred format

**To get started, I'd love to know:**
{questions_text}

**Investment:** ${estimated_budget}
**Turnaround:** {timeline} days

I'm excited about the possibility of working together on this!

Warmly,
{freelancer_name}""",
    tone="enthusiastic",
    questions=[
        "Do you have any brand guidelines or reference styles you love?",
        "What's the main goal or feeling you want to convey?",
        "Who is your target audience?",
        "Do you need any additional formats or variations?",
    ],
    strength=0.85,
)


URGENT_PROPOSAL = ReplyTemplate(
    name="urgent_proposal",
    situation_type=SituationType.URGENT_FIX,
    subject="URGENT: Can help with {project_title} right away",
    body_template="""Hi {buyer_name},

I can help with this right away. I've handled similar urgent {category} issues before, including {reference_project}.

**Here's what I'll do:**
1. Jump in immediately to diagnose the issue
2. Provide a fix within {timeline} hours
3. Test thoroughly to ensure no side effects
4. Brief you on what caused it and how to prevent it

**Quick questions:**
{questions_text}

**Urgent Fix Rate:** ${estimated_budget}
**Response Time:** Within 1 hour

Let me know and I'll get started immediately.

Best,
{freelancer_name}""",
    tone="urgent",
    questions=[
        "Can you provide access to your site/platform?",
        "When did the issue start?",
        "Do you have a backup I can work from?",
        "Any recent changes that might have caused this?",
    ],
    strength=0.9,
)


STANDARD_PROPOSAL = ReplyTemplate(
    name="standard_proposal",
    situation_type=SituationType.GENERAL,
    subject="Proposal: {project_title}",
    body_template="""Hi {buyer_name},

Thank you for considering me for {project_title}. I've reviewed your brief and I believe my experience in {category} makes me a great fit for this project.

I've completed similar projects like {reference_project} with excellent results. My approach is straightforward:

1. **Scope clarification** - Ensure we're aligned on deliverables
2. **Execution** - Work efficiently with regular updates
3. **Review & revision** - Incorporate your feedback
4. **Delivery** - Hand off with everything you need

**A few questions to get started:**
{questions_text}

**Estimated Budget:** ${estimated_budget}
**Timeline:** {timeline} days

Looking forward to your thoughts!

Best regards,
{freelancer_name}""",
    tone="friendly",
    questions=[
        "What's your preferred timeline for this project?",
        "Do you have any examples or references I should consider?",
        "Is there a specific budget range you're working with?",
        "How would you like to communicate updates?",
    ],
    strength=0.75,
)


QUICK_REPLY = ReplyTemplate(
    name="quick_reply",
    situation_type=SituationType.GENERAL,
    subject="Re: {project_title}",
    body_template="""Hi {buyer_name},

Thanks for your message! I can definitely help with {project_title}.

I've done {reference_project} before with great results. Based on your brief:

**Quote:** ${estimated_budget}
**Delivery:** {timeline} days

**Quick questions:**
{questions_text}

Let me know if you'd like to move forward!

Best,
{freelancer_name}""",
    tone="friendly",
    questions=[
        "Is this timeline workable for you?",
        "Any specific requirements I should know about?",
    ],
    strength=0.7,
)


CONSULTING_PROPOSAL = ReplyTemplate(
    name="consulting_proposal",
    situation_type=SituationType.CONSULTING,
    subject="Consulting Proposal: {project_title}",
    body_template="""Hi {buyer_name},

I appreciate you reaching out about {project_title}. After reviewing your needs, I believe I can provide valuable guidance based on my experience with {reference_project}.

**My consulting approach:**
1. **Discovery** - Deep dive into your current situation and goals
2. **Analysis** - Identify opportunities and challenges
3. **Recommendations** - Actionable plan with clear next steps
4. **Implementation support** - Help execute if needed

**To prepare, please share:**
{questions_text}

**Consulting Fee:** ${estimated_budget}
**Timeline:** {timeline} days

Looking forward to helping you achieve your goals!

Best regards,
{freelancer_name}""",
    tone="consultative",
    questions=[
        "What specific challenges are you facing right now?",
        "What have you tried so far?",
        "What's the primary outcome you're looking for?",
        "Is there a budget allocated for this engagement?",
    ],
    strength=0.8,
)


# --- Template Registry ---

TEMPLATE_REGISTRY: Dict[str, ReplyTemplate] = {
    t.name: t
    for t in [
        TECHNICAL_PROPOSAL,
        CREATIVE_PROPOSAL,
        URGENT_PROPOSAL,
        STANDARD_PROPOSAL,
        QUICK_REPLY,
        CONSULTING_PROPOSAL,
    ]
}


def get_templates_for_situation(situation_type: SituationType) -> List[ReplyTemplate]:
    """Get all templates matching a situation type, sorted by strength."""
    matching = [
        t for t in TEMPLATE_REGISTRY.values()
        if t.situation_type == situation_type
    ]
    if not matching:
        matching = [t for t in TEMPLATE_REGISTRY.values() if t.situation_type == SituationType.GENERAL]
    return sorted(matching, key=lambda t: t.strength, reverse=True)


def detect_situation_type(message: str) -> SituationType:
    """Auto-detect situation type from a client message."""
    message_lower = message.lower()

    # Check for urgency signals
    urgent_keywords = ["urgent", "asap", "emergency", "critical", "broken", "quick fix", "immediately", "right away"]
    if any(kw in message_lower for kw in urgent_keywords):
        return SituationType.URGENT_FIX

    # Check for creative signals
    creative_keywords = ["design", "creative", "logo", "brand", "ui", "ux", "visual", "art", "illustration", "graphic"]
    if any(kw in message_lower for kw in creative_keywords):
        return SituationType.CREATIVE_PROJECT

    # Check for technical signals
    technical_keywords = ["develop", "build", "code", "api", "backend", "frontend", "database", "script", "automation", "integrate", "pipeline", "architecture"]
    if any(kw in message_lower for kw in technical_keywords):
        return SituationType.TECHNICAL_PROJECT

    # Check for consulting signals
    consulting_keywords = ["consult", "advise", "strategy", "review", "audit", "recommend", "optimize", "improve"]
    if any(kw in message_lower for kw in consulting_keywords):
        return SituationType.CONSULTING

    # Check for ongoing support
    support_keywords = ["ongoing", "monthly", "retainer", "long term", "regular", "support", "maintenance"]
    if any(kw in message_lower for kw in support_keywords):
        return SituationType.ONGOING_SUPPORT

    return SituationType.GENERAL
