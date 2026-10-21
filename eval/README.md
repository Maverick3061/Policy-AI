# Evaluation status

The 25-question evaluation in `baseline_pre_expansion/` predates the corpus expansion. These metrics are **historical baseline only**, not evidence for the updated corpus.

After installing requirements and setting `GROQ_API_KEY`, run `python ingest.py`, start `python app.py` in another terminal, and run `python evaluate.py --fresh`. The resulting `eval/results.json` and `eval/summary.json` represent the expanded corpus. Check answer support manually before publishing groundedness and citation-accuracy rates.
