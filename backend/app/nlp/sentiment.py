from typing import Tuple

POSITIVE_WORDS = {
    "bueno", "buenísimo", "genial", "excelente", "maravilloso",
    "increíble", "emocionante", "bonito", "hermoso", "interesante",
    "divertido", "fascinante", "romántico"
}

NEGATIVE_WORDS = {
    "malo", "malísimo", "horrible", "terrible", "aburrido", "lento",
    "tedioso", "feo", "decepcionante", "confuso", "oscuro"
}


def analyze_sentiment(text: str) -> Tuple[str, float]:
    text_lower = text.lower()

    pos_count = sum(word in text_lower for word in POSITIVE_WORDS)
    neg_count = sum(word in text_lower for word in NEGATIVE_WORDS)

    score = pos_count - neg_count

    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"

    total_hits = pos_count + neg_count
    if total_hits > 0:
        norm_score = score / total_hits
    else:
        norm_score = 0.0

    return label, float(norm_score)
