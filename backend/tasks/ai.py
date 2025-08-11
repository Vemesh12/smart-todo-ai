from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional
    requests = None


# ----------------------------
# Basic NLP heuristics
# ----------------------------

URGENCY_KEYWORDS: Dict[str, float] = {
    'urgent': 1.0,
    'asap': 0.95,
    'today': 0.85,
    'tomorrow': 0.65,
    'immediately': 1.0,
    'deadline': 0.9,
    'overdue': 1.0,
}

CONTEXT_KEYWORDS_CATEGORY: Dict[str, str] = {
    'email': 'Communication',
    'inbox': 'Communication',
    'meeting': 'Meetings',
    'schedule': 'Meetings',
    'report': 'Work',
    'assignment': 'Work',
    'deploy': 'DevOps',
    'bug': 'Bugfix',
    'shopping': 'Personal',
    'groceries': 'Personal',
}

POSITIVE_WORDS = {'good', 'great', 'thanks', 'appreciate', 'happy'}
NEGATIVE_WORDS = {'issue', 'problem', 'delay', 'blocked', 'angry', 'urgent'}


def extract_keywords(text: str, top_k: int = 8) -> List[Tuple[str, int]]:
    tokens = [t.strip('.,:;!?()[]{}').lower() for t in text.split()]
    counts: Dict[str, int] = {}
    for t in tokens:
        if not t or len(t) <= 2:
            continue
        if t in {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has'}:
            continue
        counts[t] = counts.get(t, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_k]


def analyze_sentiment(text: str) -> float:
    text_l = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_l)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_l)
    # score in [-1, 1]
    if pos == neg == 0:
        return 0.0
    return (pos - neg) / max(pos + neg, 1)


def compute_complexity(description: str) -> float:
    hints = {
        'research': 0.8,
        'integrate': 0.9,
        'migrate': 1.0,
        'refactor': 0.7,
        'write': 0.4,
        'email': 0.2,
        'meeting': 0.3,
        'setup': 0.6,
        'debug': 0.7,
    }
    d = description.lower()
    score = 0.3  # base
    for k, w in hints.items():
        if k in d:
            score = max(score, w)
    return min(max(score, 0.1), 1.2)


def naive_keyword_priority(title: str, description: str, context_texts: List[str]) -> float:
    text = f"{title} {description}".lower()
    score = 0.0
    for word, weight in URGENCY_KEYWORDS.items():
        if word in text:
            score += weight
    # context urgency influence
    for ctx in context_texts:
        for word, weight in URGENCY_KEYWORDS.items():
            if word in ctx.lower():
                score += weight * 0.15
    return min(score, 2.0)


def suggest_deadline(base_priority: float, complexity: float, current_task_load: Dict[str, Any] | None) -> datetime:
    # Convert priority/complexity into days offset
    # More priority -> sooner; more complexity -> later
    load_factor = 0.0
    if current_task_load:
        num_active = float(current_task_load.get('num_active_tasks', 0) or 0)
        load_factor = min(num_active / 10.0, 1.0)  # scale 0..1

    # Base window in days
    days = 5.0 - 2.5 * min(base_priority, 2.0) + 3.0 * min(complexity, 1.2) + 2.0 * load_factor
    days = max(1.0, min(days, 14.0))
    return datetime.utcnow() + timedelta(days=int(round(days)))


def auto_category_from_context(text: str) -> str | None:
    t = text.lower()
    for key, value in CONTEXT_KEYWORDS_CATEGORY.items():
        if key in t:
            return value
    return None


def enhance_description_with_context(title: str, description: str, context_texts: List[str]) -> str:
    # Include top context keywords and the most relevant snippet
    joined = " \n".join(context_texts)
    kw = ", ".join([k for k, _ in extract_keywords(joined, top_k=6)])
    snippet = next((c.strip() for c in context_texts if title.lower()[:12] in c.lower()), '')
    extras = []
    if kw:
        extras.append(f"Keywords: {kw}")
    if snippet:
        extras.append(f"Related: {snippet[:120]}")
    if extras:
        return f"{description}\n\nContext → {"; ".join(extras)}"
    return description


def lm_studio_enhance(prompt: str) -> str | None:
    base_url = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
    model = os.getenv('LM_STUDIO_MODEL', 'qwen2.5:latest')
    if not requests:
        return None
    try:
        r = requests.post(
            f"{base_url}/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You assist with task triage and context-aware suggestions."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 256,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def suggest_tasks_and_priorities(
    tasks: List[Dict[str, Any]],
    context_entries: List[Dict[str, Any]],
    user_preferences: Dict[str, Any] | None = None,
    current_task_load: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    # Aggregate context
    context_texts = [str(c.get('content', '')) for c in context_entries]
    joined_context = "\n".join(context_texts)
    context_sentiment = analyze_sentiment(joined_context)

    suggestions: List[Dict[str, Any]] = []
    for task in tasks:
        title = task.get('title', '')
        description = task.get('description', '')

        # Compute components
        urgency_score = naive_keyword_priority(title, description, context_texts)
        complexity = compute_complexity(description)
        # sentiment effect: negative context pushes urgency a bit up
        urgency_score += max(context_sentiment * 0.2, 0) * (-1)  # if negative -> increase
        urgency_score = max(0.0, min(urgency_score, 2.0))

        # Personalization knobs
        if user_preferences:
            preferred_category = user_preferences.get('preferred_category')
            if preferred_category and preferred_category.lower() in (title + ' ' + description).lower():
                urgency_score += 0.1

        deadline_dt = suggest_deadline(urgency_score, complexity, current_task_load or {})
        cat = auto_category_from_context(" ".join([title, description, joined_context]))

        # Heuristic enhancement
        enhanced = enhance_description_with_context(title, description, context_texts)

        # Optional LM Studio enhancement (non-blocking)
        if os.getenv('AI_PROVIDER', '').lower() == 'lm_studio':
            prompt = (
                f"Task: {title}\nDescription: {description}\nContext: {joined_context[:2000]}\n"
                f"Provide: refined description in 2-3 bullet points.")
            llm_text = lm_studio_enhance(prompt)
            if llm_text:
                enhanced = f"{enhanced}\n\nAI: {llm_text}"

        suggestions.append({
            'title': title,
            'suggested_priority_score': round(urgency_score + complexity * 0.2, 3),
            'suggested_deadline': deadline_dt.isoformat() + 'Z',
            'suggested_category_name': cat,
            'enhanced_description': enhanced,
        })

    # Suggest derived follow-ups from context
    derived: List[Dict[str, Any]] = []
    for ctx in context_texts:
        ctx_l = ctx.lower()
        if any(k in ctx_l for k in ['follow up', 'follow-up', 'action items']):
            derived.append({
                'title': 'Follow up on recent thread',
                'suggested_priority_score': 0.8,
                'suggested_deadline': (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
                'suggested_category_name': auto_category_from_context(ctx) or 'General',
                'enhanced_description': ctx[:200],
            })

    return {
        'suggestions': suggestions,
        'derived_tasks': derived,
    }


