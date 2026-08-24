"""Tests for the scrape_reddit CLI argument parsing.

parse_args() is pure — no network access, no filesystem writes — so these run
anywhere, including CI.
"""

from pathlib import Path

import pytest

import scrape_reddit as sr


def test_defaults_match_documented_behavior():
    args = sr.parse_args([])

    assert args.subreddits == sr.DEFAULT_SUBREDDITS
    assert args.limit == sr.DEFAULT_LIMIT == 50
    assert args.output == sr.DEFAULT_OUTPUT_DIR


def test_comma_separated_subreddits_are_split():
    args = sr.parse_args(["--subreddits", "startups,SaaS,freelance"])
    assert args.subreddits == ["startups", "SaaS", "freelance"]


def test_repeated_subreddit_flags_accumulate_and_mix_with_commas():
    args = sr.parse_args(["-s", "startups", "-s", "SaaS,freelance"])
    assert args.subreddits == ["startups", "SaaS", "freelance"]


def test_r_prefix_and_whitespace_are_normalized():
    args = sr.parse_args(["--subreddits", " r/startups , SaaS "])
    assert args.subreddits == ["startups", "SaaS"]


def test_limit_and_output_are_parsed():
    args = sr.parse_args(["--limit", "10", "--output", "out/run1"])

    assert args.limit == 10
    assert args.output == Path("out/run1")


def test_limit_below_one_is_rejected():
    with pytest.raises(SystemExit):
        sr.parse_args(["--limit", "0"])


def test_empty_subreddit_value_is_rejected():
    with pytest.raises(SystemExit):
        sr.parse_args(["--subreddits", " , "])
