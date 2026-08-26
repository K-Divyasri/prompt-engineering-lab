"""Tests for the scoring / evaluation logic."""

from __future__ import annotations

from prompt_lab.data import load_tickets
from prompt_lab.evaluate import evaluate_style


def test_score_counts_add_up() -> None:
    tickets = load_tickets()
    score = evaluate_style("zero-shot", tickets)
    assert score.total == 30
    assert 0 <= score.correct <= 30
    # Every cell of the confusion matrix, summed, equals the number of readable
    # predictions (here all 30 parse, so it equals total).
    cells = sum(score.confusion[t][p] for t in score.confusion for p in score.confusion[t])
    assert cells == score.parsed_ok


def test_better_prompts_score_higher_offline() -> None:
    # The simulated offline model is built so few-shot and chain-of-thought beat
    # plain zero-shot. This guards that the teaching story stays intact.
    tickets = load_tickets()
    zero = evaluate_style("zero-shot", tickets).accuracy
    few = evaluate_style("few-shot", tickets).accuracy
    cot = evaluate_style("chain-of-thought", tickets).accuracy
    assert few > zero
    assert cot >= few


def test_accuracy_is_a_fraction() -> None:
    score = evaluate_style("role", load_tickets())
    assert 0.0 <= score.accuracy <= 1.0
    assert 0.0 <= score.parse_rate <= 1.0
