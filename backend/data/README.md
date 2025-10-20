Place embeddings.jsonl here.

Expected JSONL fields per line:
- text (string, required)
- title (string, optional)
- url (string, optional)
- embedding (number[], optional)

If embedding is missing, search will fall back to lexical keyword overlap.