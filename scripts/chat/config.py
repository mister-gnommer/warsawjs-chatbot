TOP_K = 5
# TODO: investigate scoring — exact title match scores only ~0.60
#       (e.g. "Multi-Agent AI System in JavaScript?" matches itself at 0.60).
#       May need a different similarity function or hybrid search.
SIMILARITY_THRESHOLD = 0.5
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "qwen2.5:3b"
