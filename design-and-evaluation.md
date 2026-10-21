# PolicyAI - Design and Evaluation

## Architecture
Flask exposes `/`, `/chat`, `/health`, and `/sources/<filename>`. Ten synthetic Markdown policy documents are parsed, normalized and divided into approximately 1,100-character chunks with 180-character overlap. `all-MiniLM-L6-v2` embeds the chunks in a local ChromaDB collection configured for cosine distance. Each question retrieves up to four passages. The Groq chat-completions API generates an answer constrained to retrieved passages and exact source IDs. The API returns answer text, source passages and latency.

## Design rationale
Local sentence-transformer embeddings avoid paid embedding calls. ChromaDB provides persistent vector search. Overlapping chunks preserve context near boundaries. Top-4 retrieval limits prompt size. A distance threshold of 0.75, input validation, evidence-only prompt, and exact citation-ID presence check are safeguards, not guarantees of factual correctness. Alternative citation brackets are normalized before validation.

## Evaluation method
`eval/questions.json` contains 25 policy questions. `python evaluate.py` runs the Flask test client, stores responses in `eval/results.json`, and generates `eval/summary.json`. It retries transient HTTP failures with exponential backoff and resumes completed responses. HTTP success and presence of citations are operational metrics, not groundedness scores. Citation-ID consistency only checks formatting/ID agreement.

Manual scoring: for every question, mark `groundedness_manual` true only if every substantive claim is supported by policy evidence; mark `citation_accuracy_manual` true only if cited passages directly support the answer. Count failed, unsupported, or uncited factual answers as false. Calculate percentages over the entire 25-question set and explain any unanswered questions. The summary's automatically calculated manual percentages use reviewed cases as the denominator, so do not report them as corpus-wide scores unless all 25 are reviewed.

Latency: `latency_ms` records the final attempt; `total_elapsed_ms` includes retries and backoff. p50/p95 in the script are computed on successful responses, so report the successful-response denominator and distinguish total elapsed latency.

## Results - final 25-question evaluation
All 25 questions returned HTTP 200 and all 25 answers included citations. Seven requests required retries following upstream rate limits. Final-attempt p50/p95 latency was 1,192.84/46,397.96 ms; total-elapsed p50/p95 was 1,612.65/46,398.05 ms. Citation ID consistency was recomputed as 25/25; the original summary's 13/25 was incomplete due to reused cached results without the newer metadata. An assistant review of the 25 stored answers and their retrieved passages found 25/25 supported answers and citations, but the human/manual review fields remain unscored. See `EVALUATION_REVIEW.md` and `eval/original_uploads/` for provenance.

## Limitations
The ten synthetic Markdown policies total roughly 4,248 words and may not meet the assignment's 30-120-page corpus requirement; verify the required page count and expand with meaningful, internally consistent synthetic policies if necessary. No OCR for image-only PDFs. Semantic threshold is heuristic. Citation matching does not prove factual support. Groq rate limits can delay or interrupt batch evaluation. Production deployment would require authentication, rate limiting, monitoring, and stricter source access control.
