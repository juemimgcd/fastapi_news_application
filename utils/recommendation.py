import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from conf.settings import settings
from crud import recommendation as recommendation_crud
from models.news import News, NewsEmbedding
from schemas.recommendation import RecommendationListResponse, RecommendationNewsItemResponse
from utils.qwen_client import QwenEmbeddingClient


EMBEDDING_EXCERPT_CHARS = 1200


@dataclass
class BehaviorSignal:
    news: News
    source: str
    weight: float
    event_time: datetime


def _build_embedding_text(news: News) -> str:
    content_excerpt = (news.content or "")[:EMBEDDING_EXCERPT_CHARS]
    parts = [f"标题：{news.title}"]
    if news.description:
        parts.append(f"摘要：{news.description}")
    if content_excerpt:
        parts.append(f"正文：{content_excerpt}")
    return "\n".join(parts)


def _build_content_hash(news: News) -> str:
    raw_text = "||".join([
        news.title or "",
        news.description or "",
        news.content or "",
        str(news.category_id),
    ])
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _weighted_average(vectors: list[tuple[list[float], float]]) -> list[float]:
    if not vectors:
        return []

    total_weight = sum(weight for _, weight in vectors)
    if total_weight <= 0:
        return []

    dimensions = len(vectors[0][0])
    values = [0.0] * dimensions
    for vector, weight in vectors:
        for index, item in enumerate(vector):
            values[index] += item * weight

    return [value / total_weight for value in values]


def _build_behavior_signals(
        history_rows: list[tuple[News, datetime]],
        favorite_rows: list[tuple[News, datetime]]
) -> list[BehaviorSignal]:
    signal_map: dict[int, BehaviorSignal] = {}

    def consume(rows: list[tuple[News, datetime]], source: str, base_weight: float) -> None:
        for index, (news, event_time) in enumerate(rows):
            decay = max(0.55, 1 - index * 0.08)
            current_weight = base_weight * decay
            existing = signal_map.get(news.id)
            if existing:
                existing.weight += current_weight
                if source == "favorite":
                    existing.source = "favorite"
                if event_time > existing.event_time:
                    existing.event_time = event_time
                continue

            signal_map[news.id] = BehaviorSignal(
                news=news,
                source=source,
                weight=current_weight,
                event_time=event_time,
            )

    consume(favorite_rows, "favorite", 1.45)
    consume(history_rows, "history", 1.0)

    return sorted(signal_map.values(), key=lambda item: item.weight, reverse=True)


def _build_category_weights(signals: list[BehaviorSignal]) -> dict[int, float]:
    scores: dict[int, float] = defaultdict(float)
    total_weight = 0.0
    for signal in signals:
        scores[signal.news.category_id] += signal.weight
        total_weight += signal.weight

    if total_weight <= 0:
        return {}

    return {category_id: weight / total_weight for category_id, weight in scores.items()}


def _freshness_bonus(news: News) -> float:
    if not news.publish_time:
        return 0.01

    age_days = max((datetime.now() - news.publish_time).days, 0)
    freshness = max(0.0, 1 - age_days / 30)
    return freshness * 0.08


def _popularity_bonus(news: News) -> float:
    return min(math.log1p(max(news.views, 0)) / 18, 0.12)


def _short_title(title: str, limit: int = 18) -> str:
    if len(title) <= limit:
        return title
    return f"{title[:limit]}..."


def _build_reason(news: News, reference: BehaviorSignal | None, used_ai: bool) -> str:
    if reference:
        action = "收藏过" if reference.source == "favorite" else "浏览过"
        ref_title = _short_title(reference.news.title)
        if news.category_id == reference.news.category_id:
            return f"你最近{action}《{ref_title}》，这篇同类内容更贴近你的兴趣"
        if used_ai:
            return f"你最近{action}《{ref_title}》，这篇在语义主题上和你的兴趣更接近"
        return f"你最近{action}《{ref_title}》，推荐你继续看看相关主题"

    if used_ai:
        return "结合你的浏览和收藏习惯，推荐这篇内容给你"
    return "根据新闻热度和发布时间推荐"


def _to_response_item(news: News, score: float, reason: str) -> RecommendationNewsItemResponse:
    return RecommendationNewsItemResponse.model_validate({
        "id": news.id,
        "title": news.title,
        "description": news.description,
        "image": news.image,
        "author": news.author,
        "categoryId": news.category_id,
        "views": news.views,
        "publishedTime": news.publish_time,
        "score": round(score, 4),
        "reason": reason,
    })


async def _ensure_news_embeddings(
        db: AsyncSession,
        client: QwenEmbeddingClient,
        news_list: list[News]
) -> dict[int, list[float]]:
    if not news_list:
        return {}

    unique_news = {news.id: news for news in news_list}
    existing_records = await recommendation_crud.get_news_embedding_records(db, list(unique_news))

    vectors: dict[int, list[float]] = {}
    pending_news: list[News] = []
    pending_hashes: list[str] = []

    for news in unique_news.values():
        content_hash = _build_content_hash(news)
        record = existing_records.get(news.id)
        if record and record.content_hash == content_hash and record.embedding:
            vectors[news.id] = list(record.embedding)
            continue

        pending_news.append(news)
        pending_hashes.append(content_hash)

    if not pending_news:
        return vectors

    embeddings = await client.embed_texts([_build_embedding_text(news) for news in pending_news])
    now = datetime.utcnow()

    for news, content_hash, embedding in zip(pending_news, pending_hashes, embeddings):
        record = existing_records.get(news.id)
        if record:
            record.content_hash = content_hash
            record.embedding_model = client.model
            record.embedding = embedding
            record.generated_at = now
            record.updated_time = now
        else:
            db.add(NewsEmbedding(
                news_id=news.id,
                content_hash=content_hash,
                embedding_model=client.model,
                embedding=embedding,
                generated_at=now,
                updated_time=now,
            ))
        vectors[news.id] = embedding

    await db.flush()
    return vectors


def _rank_candidates_with_ai(
        candidates: list[News],
        signals: list[BehaviorSignal],
        candidate_vectors: dict[int, list[float]],
        behavior_vectors: dict[int, list[float]],
        limit: int
) -> list[RecommendationNewsItemResponse]:
    weighted_vectors = [
        (behavior_vectors[signal.news.id], signal.weight)
        for signal in signals
        if signal.news.id in behavior_vectors
    ]
    user_vector = _weighted_average(weighted_vectors)
    if not user_vector:
        return []

    category_weights = _build_category_weights(signals)
    ranked_items: list[tuple[float, News, BehaviorSignal | None]] = []

    for news in candidates:
        vector = candidate_vectors.get(news.id)
        if not vector:
            continue

        semantic_score = _cosine_similarity(user_vector, vector)
        category_bonus = min(category_weights.get(news.category_id, 0.0) * 0.18, 0.18)
        score = semantic_score * 0.8 + category_bonus + _popularity_bonus(news) + _freshness_bonus(news)

        reference_signal = None
        reference_score = -1.0
        for signal in signals:
            behavior_vector = behavior_vectors.get(signal.news.id)
            if not behavior_vector:
                continue
            current_score = _cosine_similarity(vector, behavior_vector) * signal.weight
            if current_score > reference_score:
                reference_score = current_score
                reference_signal = signal

        ranked_items.append((score, news, reference_signal))

    ranked_items.sort(key=lambda item: item[0], reverse=True)
    return [
        _to_response_item(news, score, _build_reason(news, reference, used_ai=True))
        for score, news, reference in ranked_items[:limit]
    ]


def _rank_candidates_without_ai(
        candidates: list[News],
        signals: list[BehaviorSignal],
        limit: int
) -> list[RecommendationNewsItemResponse]:
    category_weights = _build_category_weights(signals)
    reference_by_category: dict[int, BehaviorSignal] = {}
    default_reference = signals[0] if signals else None

    for signal in signals:
        reference_by_category.setdefault(signal.news.category_id, signal)

    ranked_items: list[tuple[float, News, BehaviorSignal | None]] = []
    for news in candidates:
        category_bonus = min(category_weights.get(news.category_id, 0.0) * 0.42, 0.42)
        score = category_bonus + _popularity_bonus(news) + _freshness_bonus(news)
        reference = reference_by_category.get(news.category_id, default_reference)
        ranked_items.append((score, news, reference))

    ranked_items.sort(key=lambda item: item[0], reverse=True)
    return [
        _to_response_item(news, score, _build_reason(news, reference, used_ai=False))
        for score, news, reference in ranked_items[:limit]
    ]


async def get_personalized_recommendations(
        db: AsyncSession,
        user_id: int,
        limit: int
) -> RecommendationListResponse:
    history_rows = await recommendation_crud.get_user_history_news(
        db, user_id, settings.ai_recommendation_profile_history_limit
    )
    favorite_rows = await recommendation_crud.get_user_favorite_news(
        db, user_id, settings.ai_recommendation_profile_favorite_limit
    )
    signals = _build_behavior_signals(history_rows, favorite_rows)

    if not signals:
        popular_news = await recommendation_crud.get_latest_popular_news(db, limit)
        items = [
            _to_response_item(news, _popularity_bonus(news) + _freshness_bonus(news), "根据新闻热度和发布时间推荐")
            for news in popular_news
        ]
        return RecommendationListResponse(
            list=items,
            total=len(items),
            profile_source="popular_fallback",
            generated_at=datetime.now(),
        )

    candidate_limit = max(limit * 4, settings.ai_recommendation_candidate_limit)
    candidates = await recommendation_crud.get_candidate_news(db, user_id, candidate_limit)
    if not candidates:
        return RecommendationListResponse(
            list=[],
            total=0,
            profile_source="behavior_fallback",
            generated_at=datetime.now(),
        )

    client = QwenEmbeddingClient()
    if client.is_enabled:
        try:
            behavior_vectors = await _ensure_news_embeddings(db, client, [signal.news for signal in signals])
            candidate_vectors = await _ensure_news_embeddings(db, client, candidates)
            ai_items = _rank_candidates_with_ai(candidates, signals, candidate_vectors, behavior_vectors, limit)
            if ai_items:
                return RecommendationListResponse(
                    list=ai_items,
                    total=len(ai_items),
                    profile_source="qwen_embedding",
                    generated_at=datetime.now(),
                )
        except Exception:
            pass

    fallback_items = _rank_candidates_without_ai(candidates, signals, limit)
    return RecommendationListResponse(
        list=fallback_items,
        total=len(fallback_items),
        profile_source="behavior_fallback",
        generated_at=datetime.now(),
    )
