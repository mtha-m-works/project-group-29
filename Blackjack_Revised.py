"""
Blackjack Actions
-----------------
Implements the decision rules for a single player's turn in Blackjack.

Given a hand, the dealer's up card, and whether this is the first decision
of the turn, this module works out:
1. which actions are currently legal, and
2. what the resulting hand(s) look like after taking one.

Notation
--------
A decision point is written as three fields separated by "|":

10,6 | 9 | first

- Field 1: the player's hand, cards separated by commas.
- Field 2: the dealer's up card.
- Field 3: "first" if this is the player's first decision this turn
(no hits taken yet), otherwise "later".

Cards are written as: 2-10, J, Q, K, A.
"""

from dataclasses import dataclass
from enum import Enum


# --- Provided by the project scaffold -------------------------------------
# (reproduced here so this file runs standalone; use the versions your
# assignment actually gives you if they differ even slightly)

RANK_VALUES = {
    **{str(n): n for n in range(2, 11)},
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,
}


def hand_value(hand: tuple[str, ...] | list[str]) -> tuple[int, bool]:
    """
    Return (total, is_soft) for a hand of card ranks.
    is_soft is True if an Ace is still being counted as 11.
    """
    total = sum(RANK_VALUES[rank] for rank in hand)
    aces = hand.count("A")

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    is_soft = aces > 0
    return total, is_soft


# --- Data model -------------------------------------------------------------


class Action(Enum):
    """The six actions a player may take at a decision point."""

    HIT = "hit"
    STAND = "stand"
    DOUBLE_DOWN = "double_down"
    SPLIT = "split"
    SURRENDER = "surrender"
    INSURANCE = "insurance"


@dataclass(frozen=True)
class DecisionPoint:
    """
    A single decision point in a player's turn.

    hand: tuple of card ranks, e.g. ("10", "6")
    dealer_card: the dealer's up card rank, e.g. "9"
    is_first_decision: True if no hits have been taken yet this turn
    """

    hand: tuple[str, ...]
    dealer_card: str
    is_first_decision: bool


# --- Requirement 1: parsing ---------------------------------------------


def parse_decision_point(text: str) -> DecisionPoint:
    """
    Parse notation like "10,6 | 9 | first" into a DecisionPoint.
    """
    hand_field, dealer_field, timing_field = (part.strip() for part in text.split("|"))

    hand = tuple(card.strip() for card in hand_field.split(","))
    dealer_card = dealer_field

    if timing_field not in ("first", "later"):
        raise ValueError(f"Invalid timing field: {timing_field!r} (expected 'first' or 'later')")
    is_first_decision = timing_field == "first"

    return DecisionPoint(hand=hand, dealer_card=dealer_card, is_first_decision=is_first_decision)


# --- Requirement 2: legal actions -------------------------------------------


def is_pair(hand: tuple[str, ...]) -> bool:
    """True if the hand is exactly two cards of the same rank."""
    return len(hand) == 2 and hand[0] == hand[1]


def legal_actions(point: DecisionPoint) -> frozenset[Action]:
    """
    Return the set of Actions that are legal at this decision point.
    """
    total, _ = hand_value(point.hand)
    if total > 21:
        return frozenset()  # already busted: turn is over, nothing is legal

    actions = {Action.HIT, Action.STAND}  # legal in every situation

    if point.is_first_decision:
        actions.add(Action.DOUBLE_DOWN)
        actions.add(Action.SURRENDER)

        if is_pair(point.hand):
            actions.add(Action.SPLIT)

        if point.dealer_card == "A":
            actions.add(Action.INSURANCE)

    return frozenset(actions)


# --- Requirement 3: applying an action --------------------------------------


def apply_action(
    point: DecisionPoint,
    action: Action,
    drawn_card: str | None = None,
) -> tuple[str, ...] | tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Apply `action` to `point` and return the resulting hand.
    For SPLIT, returns a tuple of two hands instead of one.

    `drawn_card` is required for HIT and DOUBLE_DOWN (the card the player
    draws) and ignored for every other action.
    """
    if action not in legal_actions(point):
        raise ValueError(f"{action} is not legal for {point}")
    if action == Action.HIT:
        if drawn_card is None:
            raise ValueError("HIT requires a drawn_card")
        return point.hand + (drawn_card,)

    if action == Action.STAND:
        return point.hand  # hand is unchanged; turn is over

    if action == Action.DOUBLE_DOWN:
        if drawn_card is None:
            raise ValueError("DOUBLE_DOWN requires a drawn_card")
        return point.hand + (drawn_card,)  # bet doubling is out of scope here

    if action == Action.SURRENDER:
        return point.hand  # hand is unchanged; turn is over, half bet forfeited (not tracked here)

    if action == Action.INSURANCE:
        return point.hand  # side bet only: hand and turn are unaffected

    if action == Action.SPLIT:
        first_card, second_card = point.hand
        return (first_card,), (second_card,)

    raise ValueError(f"Unknown action: {action}")  # pragma: no cover


# --- Smoke tests / usage demo ------------------------------------------------

if __name__ == "__main__":
    # Hard 16 vs dealer 9, first decision: everything but Split/Insurance legal
    p1 = parse_decision_point("10,6 | 9 | first")
    assert p1 == DecisionPoint(hand=("10", "6"), dealer_card="9", is_first_decision=True)
    assert legal_actions(p1) == {
        Action.HIT,
        Action.STAND,
        Action.DOUBLE_DOWN,
        Action.SURRENDER,
    }
    assert apply_action(p1, Action.HIT, drawn_card="5") == ("10", "6", "5")
    assert apply_action(p1, Action.STAND) == ("10", "6")

    # A pair, first decision: Split becomes legal
    p2 = parse_decision_point("8,8 | 10 | first")
    assert Action.SPLIT in legal_actions(p2)
    assert apply_action(p2, Action.SPLIT) == (("8",), ("8",))

    # Dealer shows an Ace, first decision: Insurance becomes legal
    p3 = parse_decision_point("10,9 | A | first")
    assert Action.INSURANCE in legal_actions(p3)
    assert apply_action(p3, Action.INSURANCE) == ("10", "9")  # hand unaffected

    # Later decision: Double/Split/Surrender/Insurance are all gone
    p4 = parse_decision_point("10,6,4 | 9 | later")
    assert legal_actions(p4) == {Action.HIT, Action.STAND}

    # A,A: soft 12, not a bust, still just Hit/Stand/Double/Surrender/Split legal
    p5 = parse_decision_point("A,A | 6 | first")
    assert hand_value(p5.hand) == (12, True)
    assert Action.SPLIT in legal_actions(p5)

    print("All smoke tests passed.")

