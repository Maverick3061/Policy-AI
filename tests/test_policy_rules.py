from pathlib import Path
from policyai.core import chunk_text, read_document

ROOT = Path(__file__).resolve().parents[1]

def test_policy_corpus_count():
    assert len(list((ROOT / "policies").glob("*.md"))) == 10

def test_all_policies_have_substantive_guidance():
    for path in (ROOT / "policies").glob("*.md"):
        text = read_document(path)
        assert "Operational handbook" in text
        assert text.count("Worked scenario.") >= 5
        assert len(text.split()) >= 1100

def test_chunk_ids_are_stable_for_same_input():
    text = read_document(ROOT / "policies" / "leave.md")
    assert chunk_text(text) == chunk_text(text)
    assert all(0 < len(c) <= 1100 for c in chunk_text(text))
