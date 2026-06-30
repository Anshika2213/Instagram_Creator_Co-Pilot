import re
import spacy
from transformers import pipeline

# ── Load models once at import time ──────────────────
print("Loading NLP models...")
nlp = spacy.load("en_core_web_sm")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,
    max_length=512
)
print("✅ NLP models loaded!")

# ── Constants ─────────────────────────────────────────
COMMON_CTAS = [
    'save', 'share', 'comment', 'tag', 'follow', 'like',
    'click', 'check', 'link in bio', 'dm', 'subscribe',
    'turn on notifications', 'double tap', 'hit the'
]

FILLER_WORDS = [
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on',
    'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was',
    'i', 'my', 'me', 'this', 'that', 'it', 'be'
]

NICHE_HASHTAGS = {
    'Fitness': [
        '#fitness', '#workout', '#gym', '#fitnessmotivation',
        '#health', '#training', '#fit', '#exercise',
        '#bodybuilding', '#healthylifestyle'
    ],
    'Food': [
        '#food', '#foodie', '#recipe', '#cooking', '#eat',
        '#homemade', '#delicious', '#foodphotography',
        '#yummy', '#instafood'
    ],
    'Fashion': [
        '#fashion', '#style', '#ootd', '#outfit', '#clothes',
        '#trendy', '#fashionista', '#streetstyle',
        '#accessories', '#shopping'
    ],
    'Travel': [
        '#travel', '#wanderlust', '#explore', '#adventure',
        '#vacation', '#trip', '#travelphotography',
        '#travelgram', '#instatravel', '#tourism'
    ],
    'Technology': [
        '#technology', '#tech', '#coding', '#programming',
        '#software', '#ai', '#innovation', '#developer',
        '#gadgets', '#startup'
    ],
    'Beauty': [
        '#beauty', '#makeup', '#skincare', '#cosmetics',
        '#glam', '#beautyblogger', '#selfcare', '#glow',
        '#lipstick', '#skincareroutine'
    ],
    'Lifestyle': [
        '#lifestyle', '#life', '#motivation', '#inspiration',
        '#positivity', '#mindset', '#daily', '#living',
        '#selfimprovement', '#goals'
    ],
    'Music': [
        '#music', '#musician', '#song', '#singer',
        '#guitar', '#piano', '#hiphop', '#newmusic',
        '#producer', '#musicproducer'
    ],
    'Comedy': [
        '#funny', '#comedy', '#humor', '#laugh', '#meme',
        '#jokes', '#lol', '#hilarious', '#fun', '#trending'
    ],
    'Photography': [
        '#photography', '#photo', '#photographer', '#camera',
        '#photoshoot', '#portrait', '#landscape',
        '#photooftheday', '#naturephotography', '#art'
    ]
}


# ── 1. Sentiment Analysis ─────────────────────────────
def analyze_sentiment(caption: str) -> dict:
    if not caption or len(caption.strip()) < 3:
        return {
            "label": "Neutral",
            "confidence": 0.0,
            "display": "Neutral (caption too short to analyze)"
        }

    result = sentiment_pipeline(caption[:512])[0]
    label = result['label']
    score = round(result['score'] * 100, 1)

    # DistilBERT returns POSITIVE/NEGATIVE — map to our 3-class system
    if label == 'POSITIVE' and score >= 70:
        mapped = 'Positive'
    elif label == 'NEGATIVE' and score >= 70:
        mapped = 'Negative'
    else:
        mapped = 'Neutral'

    return {
        "label": mapped,
        "confidence": score,
        "display": f"{mapped} ({score}% confidence)"
    }


# ── 2. Caption Quality Scorer ─────────────────────────
def score_caption(caption: str) -> dict:
    issues = []
    positives = []
    score = 0
    max_score = 10

    if not caption or len(caption.strip()) == 0:
        return {
            "score": 0,
            "max_score": max_score,
            "grade": "F",
            "issues": ["❌ No caption provided"],
            "positives": [],
            "suggestions": ["💡 Always write a caption — captions with 15-25 words perform best"]
        }

    doc = nlp(caption)
    words = [
        token.text.lower() for token in doc
        if not token.is_punct and token.text.lower() not in FILLER_WORDS
    ]
    word_count = len(caption.split())
    sentences = list(doc.sents)
    emojis = re.findall(
        u'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        u'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF'
        u'\U00002702-\U000027B0\U000024C2-\U0001F251]+',
        caption
    )
    has_question = '?' in caption
    has_cta = any(cta in caption.lower() for cta in COMMON_CTAS)
    has_hashtags = '#' in caption
    hashtag_list = re.findall(r'#\w+', caption.lower())

    # ── Scoring criteria ──────────────────────────────

    # 1. Word count (2 points)
    if word_count >= 15:
        score += 2
        positives.append(f"✅ Good caption length ({word_count} words)")
    elif word_count >= 8:
        score += 1
        issues.append(f"⚠️ Caption is a bit short ({word_count} words) — aim for 15-25 words")
    else:
        issues.append(f"❌ Caption too short ({word_count} words) — avg performing captions are 15-25 words")

    # 2. Emojis (1 point)
    if len(emojis) >= 1:
        score += 1
        positives.append(f"✅ Emojis detected ({len(emojis)}) — increases engagement")
    else:
        issues.append("❌ No emojis — captions with emojis get higher engagement rates")

    # 3. Question (2 points)
    if has_question:
        score += 2
        positives.append("✅ Question detected — drives comments and conversation")
    else:
        issues.append("❌ No question — adding a question significantly increases comments")

    # 4. CTA (2 points)
    if has_cta:
        score += 2
        positives.append("✅ Call-to-Action detected — measurably improves engagement")
    else:
        issues.append("❌ No Call-to-Action — try ending with 'Save this!', 'Tag a friend', or 'Comment below'")

    # 5. Sentence structure (1 point)
    if len(sentences) >= 2:
        score += 1
        positives.append("✅ Multiple sentences — good caption structure")
    else:
        issues.append("⚠️ Single sentence caption — try breaking it into 2-3 lines for readability")

    # 6. Hashtags in caption (1 point)
    if has_hashtags and len(hashtag_list) > 0:
        score += 1
        positives.append(f"✅ {len(hashtag_list)} hashtag(s) in caption")
    else:
        issues.append("⚠️ No hashtags in caption — add niche-relevant hashtags for discoverability")

    # 7. Not too generic (1 point)
    generic_phrases = [
        'new post', 'check this out', 'follow me',
        'like and follow', 'follow for follow'
    ]
    is_generic = any(p in caption.lower() for p in generic_phrases)
    if not is_generic:
        score += 1
        positives.append("✅ Original caption — not using generic filler phrases")
    else:
        issues.append("❌ Generic phrase detected — write something specific to your content")

    # ── Grade ─────────────────────────────────────────
    pct = (score / max_score) * 100
    if pct >= 80:
        grade = 'A'
    elif pct >= 60:
        grade = 'B'
    elif pct >= 40:
        grade = 'C'
    elif pct >= 20:
        grade = 'D'
    else:
        grade = 'F'

    # ── Suggestions ───────────────────────────────────
    suggestions = []
    if not has_question:
        suggestions.append("💡 End with a question like 'Which one would you try?' to boost comments")
    if not has_cta:
        suggestions.append("💡 Add a CTA: 'Save this for later!' or 'Tag someone who needs this!'")
    if len(emojis) == 0:
        suggestions.append("💡 Add 2-3 relevant emojis to make your caption more engaging")
    if word_count < 15:
        suggestions.append("💡 Expand your caption — share a short story or tip related to your content")
    if is_generic:
        suggestions.append("💡 Replace generic phrases with specific value — what does this post teach or show?")

    return {
        "score": score,
        "max_score": max_score,
        "grade": grade,
        "percentage": round(pct, 1),
        "word_count": word_count,
        "emoji_count": len(emojis),
        "has_question": has_question,
        "has_cta": has_cta,
        "hashtag_count": len(hashtag_list),
        "issues": issues,
        "positives": positives,
        "suggestions": suggestions
    }


# ── 3. Hashtag Relevance Checker ──────────────────────
def check_hashtag_relevance(hashtags: list, category: str) -> dict:
    if not hashtags or not category:
        return {
            "relevant": [],
            "irrelevant": [],
            "suggested": [],
            "relevance_score": 0
        }

    niche_tags = NICHE_HASHTAGS.get(category, [])
    hashtags_lower = [
        h.lower() if h.startswith('#') else f'#{h.lower()}'
        for h in hashtags
    ]

    relevant = []
    irrelevant = []

    for tag in hashtags_lower:
        # Check if tag is in niche list or contains niche keywords
        niche_keywords = [t.replace('#', '') for t in niche_tags]
        tag_word = tag.replace('#', '')
        is_relevant = any(
            kw in tag_word or tag_word in kw
            for kw in niche_keywords
        )
        if is_relevant:
            relevant.append(tag)
        else:
            irrelevant.append(tag)

    # Suggest tags from niche not already used
    used = set(hashtags_lower)
    suggested = [t for t in niche_tags if t not in used][:5]

    relevance_score = round(
        (len(relevant) / len(hashtags_lower)) * 100
        if hashtags_lower else 0, 1
    )

    return {
        "relevant": relevant,
        "irrelevant": irrelevant,
        "suggested": suggested,
        "relevance_score": relevance_score,
        "summary": (
            f"{len(relevant)}/{len(hashtags_lower)} hashtags are relevant to {category}"
        )
    }


# ── Main analyzer (combines all 3) ────────────────────
def analyze_caption(caption: str, hashtags: list = None, category: str = None) -> dict:
    sentiment = analyze_sentiment(caption)
    quality = score_caption(caption)
    hashtag_analysis = check_hashtag_relevance(
        hashtags or [], category or ''
    )

    return {
        "sentiment": sentiment,
        "caption_quality": quality,
        "hashtag_analysis": hashtag_analysis
    }