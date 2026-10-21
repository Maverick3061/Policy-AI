# Corpus audit — expanded policy documents

- Source documents: **10 Markdown policy files** in `policies/`.
- Combined word count: **11,591** words.
- Reproducible A4 PDF export: **32 pages**, file `CORPUS_10_POLICIES.pdf`.
- Source-of-truth for RAG ingestion: **Markdown files**; PDF is an evidence/export artifact and is deliberately stored at the project root to prevent duplicate ingestion.
- Corpus content: synthetic, fictional, and extended with policy-specific procedures and worked examples.
- Existing policy thresholds and entitlements were retained.
- **Evaluation caveat:** the 25-answer JSON results in `eval/` were obtained against the earlier, shorter corpus. They are retained as historical baseline only and MUST be rerun after `python ingest.py`. Do not claim the old results measure this expanded corpus.
