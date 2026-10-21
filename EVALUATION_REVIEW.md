# PolicyAI - Final Evaluation Review (25 of 25)

This report uses the uploaded `results(1).json` and `summary(1).json` (preserved verbatim under `eval/original_uploads/`). No new Groq requests were made.

## Measured results

| Measure | Result |
|---|---:|
| Completed questions | 25 / 25 |
| HTTP 200 responses | 25 / 25 (100%) |
| Responses with citations | 25 / 25 |
| Citation IDs matching returned evidence (recomputed) | 25 / 25 |
| Requests requiring retries | 7 |
| p50 final-attempt latency | 1,192.84 ms |
| p95 final-attempt latency | 46,397.96 ms |
| Mean final-attempt latency | 7,966.85 ms |
| p50 total elapsed time | 1,612.65 ms |
| p95 total elapsed time | 46,398.05 ms |

The uploaded summary reported 13 citation-ID matches because older resumed results did not contain the newer computed metadata. Re-extracting bracketed citation IDs from all 25 answers and comparing them with the returned citation IDs gives 25/25. This is an ID consistency check, not a semantic quality score.

## Assistant review of cited evidence

All 25 responses were inspected against the cited evidence passages included in the uploaded records. The factual answers are supported by those passages, including the final legal-hold question: `data-retention.md::2` states that legal holds suspend routine deletion until legal counsel releases the hold. **Assistant-reviewed groundedness: 25/25; assistant-reviewed citation support: 25/25.** These are not independent human-graded scores and should not be represented as such. The original `groundedness_manual` and `citation_accuracy_manual` fields remain null.

## Caveats

The reported latency percentiles include only successful final HTTP attempts. `total_elapsed_ms` includes waiting and retry time. The 100,845 ms annual-leave question and 53,881 ms legal-hold question produce a long tail. The synthetic ten-document corpus appears shorter than the assignment's 30-120-page requirement and needs substantive expansion and page-count verification. CI status, grader repository access, and the demo link are not verified.
