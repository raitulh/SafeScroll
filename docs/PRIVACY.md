# Privacy Model

ZERO mode is local-first. The extension does not need an account or cloud AI for its basic scanner.

Enhanced Mode is explicitly opt-in. When enabled, selected text can be sent to the configured FastAPI/Ollama service. If hosted URL reputation is enabled, queried URLs can be sent to the configured threat-intelligence provider.

Raw scan content is not persisted by the API. Analytics store minimal scan metadata only.
