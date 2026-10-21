# PolicyAI — RAG Company Policy Assistant

A Flask-based Retrieval-Augmented Generation (RAG) application using local sentence-transformer embeddings, ChromaDB and the Groq chat-completions API. Includes **10 fictional policies**. No real organizational policies or private data are included.

## Local setup

Requires Python 3.11 and internet access for first-time model download and LLM requests.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
```

Replace `GROQ_API_KEY` in `.env` with your own key. Then:

```bash
python ingest.py
python app.py
```

Visit http://127.0.0.1:5000. The API supports `GET /health`, `POST /chat` with `{"question":"How many annual leave days do I receive?"}`, and `GET /sources/<filename>`.

## Tests

```bash
pytest -q
```

## Evaluation

Run `python evaluate.py` after indexing and configuring the API. This produces `eval/results.json`. Groundedness and citation accuracy must be **manually scored** against the retrieved passages using `eval/questions.json`; do not present unverified model output as a measured result. Report p50/p95 request latency after at least 10 queries.

## Deployment

Optional: configure a Python web service on Render with build command `pip install -r requirements.txt && python ingest.py` and start command `gunicorn app:app` (install gunicorn). Persist ChromaDB on a disk if your host supports it, or rebuild the index on every deploy. Set GROQ_API_KEY as a secret environment variable. Free-tier availability and limits may change.

## Limitations

The relevance threshold is heuristic, and an LLM can still produce unsupported statements. Citation IDs are checked for presence, not factual correctness; manually evaluate both. Scanned/image-only PDFs require OCR, which this starter does not implement. This is a demonstration system, not a production policy compliance service.

## Submission status
See `SUBMISSION_CHECKLIST.md`, `DEMO_SCRIPT.md`, and `design-and-evaluation.md` for remaining work. The evaluation results included in the originally supplied ZIP were stale; replace them with your current run before submitting. Verify the 30-120-page corpus requirement.

## Expanded policy corpus (32 pages)

The ten source Markdown policies contain 11,591 words, including policy-specific worked examples and workflow guidance. `CORPUS_10_POLICIES.pdf` is a 32-page A4 export for corpus-size verification; the ingestion script reads `policies/*.md`, not the PDF export. See `CORPUS_AUDIT.md`.

**Important:** `eval/baseline_pre_expansion/` contains historical results for the shorter corpus. Run `python ingest.py` after any policy change, then rerun `python evaluate.py --fresh` against a running Flask app before reporting current accuracy or latency.

The GitHub repository, grader collaborator invitation, demo recording, CI run and live Groq evaluation require your own account or API key; they are not claimed to have been completed in this offline package.
