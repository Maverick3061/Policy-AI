"""PolicyAI evaluation runner.

Run from the project root: python evaluate.py
Resume incomplete runs: python evaluate.py
Start a fresh run: python evaluate.py --fresh
"""

import argparse
import json
import random
import re
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

from app import app  # noqa: E402 - load .env before importing app

QUESTIONS_FILE = ROOT / 'eval' / 'questions.json'
RESULTS_FILE = ROOT / 'eval' / 'results.json'
SUMMARY_FILE = ROOT / 'eval' / 'summary.json'

MAX_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 6
MAX_BACKOFF_SECONDS = 90
RETRYABLE_STATUSES = {429, 502, 503, 504}
FALLBACK_TEXT = 'The retrieved policies did not yield a verifiably cited answer'
CITATION_PATTERN = re.compile(r'\[([^\[\]\n]+::\d+)\]')


def percentile(values, fraction):
    """Return a linearly interpolated percentile, or None if no values."""
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return round(values[lower] + (values[upper] - values[lower]) * (position - lower), 2)


def normalize_citation_brackets(answer):
    """Normalize alternate citation delimiters for reporting/validation.

    The application should ideally normalize these before validating citations.
    This function cannot rescue a fallback response already returned by the API.
    """
    if not isinstance(answer, str):
        return answer
    return re.sub(r'【\s*([^【】\[\]\n]+::\d+)\s*】', r'[\1]', answer)


def valid_result(row):
    """Whether a cached row can be reused safely on resume.

    Do not reuse failures, known citation fallbacks, or factual responses
    with no citation. Explicit out-of-scope/insufficient-evidence answers
    may be reused if they do not claim policy facts.
    """
    if row.get('status') != 200:
        return False
    answer = row.get('answer')
    if not isinstance(answer, str) or not answer.strip():
        return False
    if FALLBACK_TEXT.lower() in answer.lower():
        return False
    citations = row.get('citations') or []
    if citations:
        return True
    refusal_phrases = (
        'could not find relevant evidence',
        'do not specify',
        'does not specify',
        'only answer questions supported',
        'outside the company policies',
        'not covered by the provided policies',
    )
    return any(phrase in answer.lower() for phrase in refusal_phrases)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    temporary.replace(path)


def evaluate_case(client, case):
    attempts = []
    overall_start = time.perf_counter()
    final_status = 0
    final_data = {}

    for attempt_number in range(1, MAX_ATTEMPTS + 1):
        started = time.perf_counter()
        try:
            response = client.post('/chat', json={'question': case['question']})
            status = response.status_code
            data = response.get_json(silent=True)
            if not isinstance(data, dict):
                data = {'error': 'Non-JSON or unexpected API response'}
        except Exception as exc:
            status = 0
            data = {'error': f'{type(exc).__name__}: {exc}'}

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        attempts.append({
            'attempt': attempt_number,
            'status': status,
            'latency_ms': elapsed_ms,
            'error': data.get('error'),
        })
        final_status, final_data = status, data

        if status == 200 or status not in RETRYABLE_STATUSES or attempt_number == MAX_ATTEMPTS:
            break

        delay = min(MAX_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * 2 ** (attempt_number - 1))
        delay += random.uniform(0, 1)
        print(f'  Transient HTTP {status}; retry {attempt_number}/{MAX_ATTEMPTS - 1} in {delay:.1f}s', flush=True)
        time.sleep(delay)

    answer = normalize_citation_brackets(final_data.get('answer'))
    citations = final_data.get('citations') or []
    if not isinstance(citations, list):
        citations = []
    returned_ids = {str(c.get('id')) for c in citations if isinstance(c, dict) and c.get('id')}
    answer_ids = set(CITATION_PATTERN.findall(answer or '')) if isinstance(answer, str) else set()

    return {
        **case,
        'status': final_status,
        'answer': answer,
        'citations': citations,
        'error': final_data.get('error'),
        'latency_ms': attempts[-1]['latency_ms'],
        'total_elapsed_ms': round((time.perf_counter() - overall_start) * 1000, 2),
        'attempt_count': len(attempts),
        'attempts': attempts,
        'citation_ids_in_answer': sorted(answer_ids),
        'citation_ids_returned': sorted(returned_ids),
        'citation_ids_consistent': bool(answer_ids) and answer_ids == returned_ids,
        'groundedness_manual': None,
        'citation_accuracy_manual': None,
    }


def summarize(results):
    successful = [r for r in results if r.get('status') == 200]
    failed = [r for r in results if r.get('status') != 200]
    latencies = [r['latency_ms'] for r in successful if isinstance(r.get('latency_ms'), (int, float))]
    end_to_end = [r['total_elapsed_ms'] for r in successful if isinstance(r.get('total_elapsed_ms'), (int, float))]
    manually_grounded = [r['groundedness_manual'] for r in results if isinstance(r.get('groundedness_manual'), bool)]
    manually_cited = [r['citation_accuracy_manual'] for r in results if isinstance(r.get('citation_accuracy_manual'), bool)]
    return {
        'total_questions': len(results),
        'http_successful': len(successful),
        'http_failed': len(failed),
        'http_success_rate_pct': round(100 * len(successful) / len(results), 2) if results else 0,
        'responses_with_citations': sum(bool(r.get('citations')) for r in successful),
        'citation_id_consistency_count': sum(r.get('citation_ids_consistent') is True for r in successful),
        'requests_requiring_retries': sum(r.get('attempt_count', 1) > 1 for r in results),
        'p50_latency_ms': percentile(latencies, 0.50),
        'p95_latency_ms': percentile(latencies, 0.95),
        'mean_latency_ms': round(statistics.mean(latencies), 2) if latencies else None,
        'p50_total_elapsed_ms': percentile(end_to_end, 0.50),
        'p95_total_elapsed_ms': percentile(end_to_end, 0.95),
        'groundedness_reviewed': len(manually_grounded),
        'groundedness_passed': sum(manually_grounded),
        'citation_accuracy_reviewed': len(manually_cited),
        'citation_accuracy_passed': sum(manually_cited),
        'groundedness_rate_pct': round(100 * sum(manually_grounded) / len(manually_grounded), 2) if manually_grounded else None,
        'citation_accuracy_rate_pct': round(100 * sum(manually_cited) / len(manually_cited), 2) if manually_cited else None,
        'notes': [
            'HTTP 200 does not guarantee a correct or grounded answer.',
            'Citation ID consistency is a format check, not evidence that the citation supports the claim.',
            'Latency percentiles include only HTTP 200 final attempts; total_elapsed_ms includes retries and waiting.',
            'Manual groundedness and citation accuracy require evidence review.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate PolicyAI RAG responses')
    parser.add_argument('--fresh', action='store_true', help='Discard cached results and rerun all questions')
    args = parser.parse_args()

    questions = json.loads(QUESTIONS_FILE.read_text(encoding='utf-8'))
    if not isinstance(questions, list):
        raise ValueError('eval/questions.json must contain a JSON list')

    cached = {}
    if not args.fresh and RESULTS_FILE.exists():
        old_rows = json.loads(RESULTS_FILE.read_text(encoding='utf-8'))
        if isinstance(old_rows, list):
            cached = {r['question']: r for r in old_rows if isinstance(r, dict) and 'question' in r and valid_result(r)}

    results = []
    print(f'Evaluating {len(questions)} questions; {len(cached)} reusable results.\n', flush=True)

    try:
        with app.test_client() as client:
            for index, case in enumerate(questions, 1):
                question = case['question']
                if question in cached:
                    result = cached[question]
                    print(f'[{index}/{len(questions)}] Reused: {question}', flush=True)
                else:
                    print(f'[{index}/{len(questions)}] {question}', flush=True)
                    result = evaluate_case(client, case)
                    print(f"  HTTP {result['status']} | {result['latency_ms']:.0f} ms | attempts {result['attempt_count']}", flush=True)
                    if result.get('error'):
                        print(f"  Error: {result['error']}", flush=True)
                results.append(result)
                save_json(RESULTS_FILE, results)
    except KeyboardInterrupt:
        print('\nInterrupted. Completed questions have been saved; rerun to resume.', flush=True)
    finally:
        save_json(RESULTS_FILE, results)
        summary = summarize(results)
        save_json(SUMMARY_FILE, summary)
        print('\n========== EVALUATION SUMMARY ==========', flush=True)
        for key, value in summary.items():
            if key != 'notes':
                print(f'{key}: {value}', flush=True)
        print(f'\nSaved {RESULTS_FILE} and {SUMMARY_FILE}', flush=True)


if __name__ == '__main__':
    main()
