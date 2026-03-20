import httpx

from conf.settings import settings


class QwenEmbeddingClient:
    def __init__(self):
        self.api_key = settings.qwen_api_key.strip()
        self.base_url = settings.qwen_base_url
        self.model = settings.qwen_embedding_model
        self.dimensions = settings.ai_recommendation_embedding_dimensions
        self.timeout = settings.ai_recommendation_request_timeout
        self.batch_size = 10

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if not self.is_enabled:
            raise RuntimeError("Qwen API key is not configured.")

        embeddings: list[list[float]] = []
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start:start + self.batch_size]
                payload = {
                    "model": self.model,
                    "input": batch,
                }
                if self.dimensions:
                    payload["dimensions"] = self.dimensions

                try:
                    response = await client.post(
                        f"{self.base_url}/embeddings",
                        headers=headers,
                        json=payload,
                    )
                except httpx.HTTPError as exc:
                    raise RuntimeError(
                        f"Qwen embedding request failed to connect to {self.base_url}: {exc}"
                    ) from exc

                if response.is_error:
                    detail = response.text
                    try:
                        error_payload = response.json()
                        detail = error_payload.get("error", {}).get("message", detail)
                    except ValueError:
                        pass
                    raise RuntimeError(f"Qwen embedding request failed: {detail}")

                data = response.json().get("data", [])
                ordered_items = sorted(data, key=lambda item: item.get("index", 0))
                embeddings.extend(item["embedding"] for item in ordered_items)

        if len(embeddings) != len(texts):
            raise RuntimeError("Qwen embedding result length does not match input length.")

        return embeddings
