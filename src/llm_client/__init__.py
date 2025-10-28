"""LLM Client package for T8 configuration analysis."""

from llm_client.groq_client import GroqLLMClient

# Componentes opcionales de fragmentación
try:
    from llm_client.api_doc_fragmenter import ApiDocFragmenter
    from llm_client.cache import ChunkCache
    from llm_client.chunked_analyzer import ChunkedAnalyzer
    from llm_client.chunking import ConfigChunk, ConfigChunker
    from llm_client.model_selector import ModelSelector

    __all__ = [
        "GroqLLMClient",
        "ChunkedAnalyzer",
        "ConfigChunker",
        "ConfigChunk",
        "ChunkCache",
        "ModelSelector",
        "ApiDocFragmenter",
    ]
except ImportError:
    __all__ = ["GroqLLMClient"]
