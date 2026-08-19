"""Tests for the pain-point analysis pipeline.

Every function under test is pure or filesystem-scoped, so no Reddit access is
required — fixtures write fake scrape output into a tmp_path RAW_DIR.
"""

import json

import pytest

import analyze_pain_points as ap


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    d = tmp_path / "raw"
    d.mkdir()
    monkeypatch.setattr(ap, "RAW_DIR", d)
    return d


def write(raw_dir, name, payload):
    (raw_dir / name).write_text(json.dumps(payload))


# --- load_all_posts ---------------------------------------------------------

def test_load_all_posts_returns_empty_when_raw_dir_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "RAW_DIR", tmp_path / "does-not-exist")
    assert ap.load_all_posts() == []


def test_load_all_posts_flattens_lists_and_keeps_single_objects(raw_dir):
    write(raw_dir, "a.json", [{"title": "one"}, {"title": "two"}])
    write(raw_dir, "b.json", {"title": "three"})

    titles = sorted(p["title"] for p in ap.load_all_posts())
    assert titles == ["one", "three", "two"]


def test_load_all_posts_skips_corrupt_files(raw_dir):
    write(raw_dir, "good.json", [{"title": "ok"}])
    (raw_dir / "bad.json").write_text("{not json")

    assert ap.load_all_posts() == [{"title": "ok"}]


# --- extract_pain_snippets --------------------------------------------------

def test_matching_title_is_extracted_with_its_url():
    posts = [{"title": "I'm stuck and don't know how to start", "url": "http://r/1"}]
    snippets = ap.extract_pain_snippets(posts)

    assert snippets
    assert all(url == "http://r/1" for _, url, _ in snippets)
    assert all(src == "title" for _, _, src in snippets)


def test_non_matching_text_produces_nothing():
    posts = [{"title": "Weather is nice today", "top_comments": ["Agreed"]}]
    assert ap.extract_pain_snippets(posts) == []


def test_comments_are_scanned_and_tagged_as_comments():
    posts = [{"title": "hello", "top_comments": ["honestly I am overwhelmed by tools"]}]
    snippets = ap.extract_pain_snippets(posts)

    assert [src for _, _, src in snippets] == ["comment"]


def test_comment_snippet_is_windowed_around_the_match():
    long_comment = "x" * 300 + " where to start " + "y" * 300
    posts = [{"title": "", "top_comments": [long_comment]}]

    snippet = ap.extract_pain_snippets(posts)[0][0]
    assert "where to start" in snippet
    assert len(snippet) < len(long_comment)


def test_missing_fields_do_not_raise():
    assert ap.extract_pain_snippets([{}]) == []
    assert ap.extract_pain_snippets([{"title": None, "top_comments": None}]) == []


def test_pain_matching_is_case_insensitive():
    posts = [{"title": "STUCK on this"}]
    assert ap.extract_pain_snippets(posts)


# --- cluster_and_rank -------------------------------------------------------

def test_cluster_and_rank_returns_empty_for_no_snippets():
    assert ap.cluster_and_rank([]) == []


def test_cluster_and_rank_returns_at_most_five_ranked_entries():
    snippets = [
        (f"stuck on pipeline problem number {i}", f"http://r/{i}", "title")
        for i in range(40)
    ]
    result = ap.cluster_and_rank(snippets)

    assert len(result) <= 5
    assert [r["rank"] for r in result] == list(range(1, len(result) + 1))


def test_ranked_entries_carry_the_expected_report_fields():
    snippets = [("stuck on shipping", "http://r/1", "title")] * 3
    entry = ap.cluster_and_rank(snippets)[0]

    assert set(entry) == {
        "rank", "pain_point", "example_quotes", "why_pdf_helps", "suggested_pdf_title"
    }
    assert entry["example_quotes"]


def test_example_quotes_are_deduplicated():
    snippets = [("stuck on shipping", "http://r/1", "title")] * 5
    entry = ap.cluster_and_rank(snippets)[0]

    assert len(entry["example_quotes"]) == 1


def test_larger_clusters_rank_above_smaller_ones():
    big = [("stuck automate pipeline shipping", "http://r/a", "title")] * 6
    small = [("overwhelm too many tabs open", "http://r/b", "title")] * 2
    result = ap.cluster_and_rank(big + small)

    assert len(result[0]["example_quotes"]) >= len(result[-1]["example_quotes"])


# --- main -------------------------------------------------------------------

def test_main_reports_and_exits_when_there_is_no_raw_data(raw_dir, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(ap, "DATA_DIR", tmp_path / "data")
    ap.main()

    assert "Run scrape_reddit.py first" in capsys.readouterr().out


def test_main_writes_json_and_markdown_outputs(raw_dir, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(ap, "DATA_DIR", data_dir)
    monkeypatch.setattr(ap, "OUT_JSON", data_dir / "top5_pain_points.json")
    monkeypatch.setattr(ap, "OUT_REPORT", data_dir / "PAIN_POINTS_REPORT.md")
    write(raw_dir, "a.json", [
        {"title": "stuck and don't know how to ship", "url": "http://r/1"},
        {"title": "too many tools, where to start", "url": "http://r/2"},
    ])

    ap.main()

    top5 = json.loads((data_dir / "top5_pain_points.json").read_text())
    report = (data_dir / "PAIN_POINTS_REPORT.md").read_text()

    assert top5 and top5[0]["rank"] == 1
    assert report.startswith("# Top 5 Pain Points")
    assert "Suggested PDF title:" in report
