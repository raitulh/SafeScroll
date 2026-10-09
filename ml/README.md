# SafeScroll ML

SafeScroll uses two ML paths:

1. **Small Mode:** a tiny hashed-character linear classifier shipped for browser-local inference. It is intentionally small enough for constrained devices.
2. **Enhanced Mode:** optional Qwen3:1.7B via Ollama for harder cases and explanations.

The repository includes a bootstrap model trained from `ml/data/seed.jsonl`. It is not a claim of production-grade generalization. Before public launch, run `ml/fetch_public_data.py`, retrain, and require the benchmark gate to pass. The UCI SMS Spam Collection contains 5,574 labeled messages and is licensed CC BY 4.0; it is a spam benchmark, not a complete scam taxonomy. Treat it as one ingredient, not the whole training corpus.
