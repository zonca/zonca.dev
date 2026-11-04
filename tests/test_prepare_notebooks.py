"""Tests for the notebook section/anchor rules in scripts/prepare_notebooks.py.

Run with: python3 -m pytest tests/test_prepare_notebooks.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from prepare_notebooks import drop_duplicate_title, norm_heading, section_headings  # noqa: E402


def test_section_headings_returns_level_two_and_deeper():
    text = "# Title\n\n## One\n\n### Sub\n\n## Two\n"
    assert section_headings(text) == ["One", "Sub", "Two"]


def test_section_headings_ignores_fenced_code():
    text = "## Real\n\n```python\n# comment\n## not a heading\n```\n\n## Also real\n"
    assert section_headings(text) == ["Real", "Also real"]


def test_section_headings_ignores_heading_inside_indented_output():
    text = "## A\n\n~~~\n## hidden\n~~~\n\n## B\n"
    assert section_headings(text) == ["A", "B"]


def test_drop_duplicate_title_removes_matching_first_heading():
    body = "# My Title\n\nIntro text\n"
    assert drop_duplicate_title(body, "My Title") == "Intro text\n"


def test_drop_duplicate_title_when_a_notice_comes_first():
    body = "> **AI-generated notebook**\n>\n> prompt\n\n# My Title\n\n## Background\n\ntext\n"
    got = drop_duplicate_title(body, "My Title")
    assert "# My Title" not in got
    assert got.startswith("> **AI-generated notebook**")
    assert "## Background" in got


def test_drop_duplicate_title_ignores_inline_markup():
    body = "# `ud_grade` vs `harmonic_ud_grade`: A Comparison\n\ntext\n"
    got = drop_duplicate_title(body, "ud_grade vs harmonic_ud_grade: A Comparison")
    assert got == "text\n"


def test_drop_duplicate_title_keeps_a_different_heading():
    body = "# A Different Heading\n\ntext\n"
    assert drop_duplicate_title(body, "My Title") == body


def test_drop_duplicate_title_keeps_level_two_heading():
    body = "## My Title\n\ntext\n"
    assert drop_duplicate_title(body, "My Title") == body


def test_drop_duplicate_title_only_touches_the_first_heading():
    """A `#` after a real section is a genuine heading and must survive."""
    body = "## Intro\n\n# My Title\n\ntext\n"
    assert drop_duplicate_title(body, "My Title") == body


def test_drop_duplicate_title_keeps_heading_inside_a_code_fence():
    body = "```markdown\n# My Title\n```\n\ntext\n"
    assert drop_duplicate_title(body, "My Title") == body


def test_drop_duplicate_title_without_any_heading():
    body = "just a paragraph\n"
    assert drop_duplicate_title(body, "My Title") == body


def test_norm_heading_collapses_whitespace_and_markup():
    assert norm_heading("  A   *B* `C` _D_  ") == "a b c d"
