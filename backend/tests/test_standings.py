"""Tests for the league rules.

These never touch the database or the HTTP layer. That is the point of keeping
the standings engine pure: the rules can be verified in isolation, and a
failure here points at the rules rather than at plumbing.
"""

from app.standings import MatchResult, TeamStanding, compute_standings

import pytest


def test_empty_league_returns_empty_table():
    assert compute_standings([], []) == []


def test_teams_with_no_matches_still_appear():
    table = compute_standings(["Ajax", "Benfica"], [])
    assert [s.team for s in table] == ["Ajax", "Benfica"]
    assert all(s.played == 0 and s.points == 0 for s in table)


def test_a_win_is_worth_three_points():
    table = compute_standings(
        ["Ajax", "Benfica"],
        [MatchResult("Ajax", "Benfica", 2, 0)],
    )
    winner, loser = table
    assert winner.team == "Ajax"
    assert winner.points == 3
    assert winner.won == 1
    assert loser.points == 0
    assert loser.lost == 1


def test_a_draw_is_worth_one_point_each():
    table = compute_standings(
        ["Ajax", "Benfica"],
        [MatchResult("Ajax", "Benfica", 1, 1)],
    )
    assert all(s.points == 1 and s.drawn == 1 for s in table)


def test_goals_are_counted_from_both_sides():
    table = compute_standings(
        ["Ajax", "Benfica"],
        [MatchResult("Ajax", "Benfica", 3, 1)],
    )
    ajax = next(s for s in table if s.team == "Ajax")
    benfica = next(s for s in table if s.team == "Benfica")

    assert (ajax.goals_for, ajax.goals_against) == (3, 1)
    assert (benfica.goals_for, benfica.goals_against) == (1, 3)
    assert ajax.goal_difference == 2
    assert benfica.goal_difference == -2


def test_points_decide_the_order_before_anything_else():
    table = compute_standings(
        ["Ajax", "Benfica", "Celtic"],
        [
            MatchResult("Ajax", "Benfica", 1, 0),
            MatchResult("Celtic", "Benfica", 9, 0),
            MatchResult("Ajax", "Celtic", 1, 0),
        ],
    )
    # Ajax has 6 points, Celtic 3 with a far better goal difference.
    # Points still win.
    assert [s.team for s in table] == ["Ajax", "Celtic", "Benfica"]


def test_goal_difference_breaks_a_tie_on_points():
    table = compute_standings(
        ["Ajax", "Benfica", "Celtic"],
        [
            MatchResult("Ajax", "Celtic", 5, 0),
            MatchResult("Benfica", "Celtic", 1, 0),
        ],
    )
    assert [s.team for s in table][:2] == ["Ajax", "Benfica"]


def test_goals_scored_breaks_a_tie_on_goal_difference():
    table = compute_standings(
        ["Ajax", "Benfica", "Celtic", "Dynamo"],
        [
            MatchResult("Ajax", "Celtic", 4, 2),
            MatchResult("Benfica", "Dynamo", 2, 0),
        ],
    )
    # Both won by two goals; Ajax scored more.
    assert [s.team for s in table][:2] == ["Ajax", "Benfica"]


def test_teams_that_are_completely_level_are_ordered_alphabetically():
    table = compute_standings(["Zenit", "Ajax", "Milan"], [])
    assert [s.team for s in table] == ["Ajax", "Milan", "Zenit"]


def test_the_order_is_stable_across_calls():
    teams = ["Zenit", "Ajax", "Milan"]
    matches = [MatchResult("Ajax", "Milan", 1, 1)]
    first = [s.team for s in compute_standings(teams, matches)]
    second = [s.team for s in compute_standings(list(reversed(teams)), matches)]
    assert first == second


def test_played_count_accumulates_over_several_matches():
    table = compute_standings(
        ["Ajax", "Benfica", "Celtic"],
        [
            MatchResult("Ajax", "Benfica", 1, 0),
            MatchResult("Ajax", "Celtic", 0, 0),
            MatchResult("Benfica", "Celtic", 2, 3),
        ],
    )
    ajax = next(s for s in table if s.team == "Ajax")
    assert ajax.played == 2
    assert (ajax.won, ajax.drawn, ajax.lost) == (1, 1, 0)
    assert ajax.points == 4


def test_a_match_with_an_unknown_team_is_rejected():
    with pytest.raises(ValueError, match="unknown team"):
        compute_standings(["Ajax"], [MatchResult("Ajax", "Ghost FC", 1, 0)])


def test_standing_is_a_plain_object_with_derived_fields():
    s = TeamStanding(team="Ajax", won=2, drawn=1, goals_for=7, goals_against=3)
    assert s.points == 7
    assert s.goal_difference == 4
