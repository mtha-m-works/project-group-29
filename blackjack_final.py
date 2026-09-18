import random

RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}

# Thekgo Section


def hand_value(cards):
    total = sum(RANK_VALUES[card] for card in cards)
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def parse_state(text):
    # flag is where the decision timing will be displayed
    # split into the player's hand, the dealer's face-up card, and the flag at the end
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]
    #validating the flag to either return first or later 
    if flag not in ("first", "later"):
        raise ValueError(f"Invalid flag: {flag!r} (expected 'first' or 'later')")

    # parse takes the result and returns it in the format asked for in the doc
    hand = [rank.strip() for rank in hand_str.split(",")]

    # brings back the results as a dictionary
    return {
        'hand': hand,
        'hand_value': hand_value(hand),
        'dealer_upcard': dealer_upcard,
        'flag': flag
    }

# Mtha Section


def generate_actions(state):
    hand = state["hand"]

    # a hand greater than 21 is busted so your turn is over
    if state["hand_value"] > 21:
        return []

    actions = ["hit", "stand"]  # legal in every situation

   # sorting out surrendering and insurance for splitt
    is_first_decision = state["flag"] == "first"

    if is_first_decision:
        actions.append("double")     # only allowed on your original two cards
        actions.append("surrender")  # only allowed before you've taken any other action

        # Restricting split options by checking if the hand has exactly two cards.
        if len(hand) == 2 and hand[0] == hand[1]:
            actions.append("split")

        # added insurance, it's only legal when the dealer's
        # face-up card is an Ace, and only as your first decision.
        if state["dealer_upcard"] == "A":
            actions.append("insurance")

    return actions


# New Input Handling Section
def get_user_action(state, exclude=None):
    
    exclude = exclude or []
    allowed_actions = [a for a in generate_actions(state) if a not in exclude]

    print(f"\nYour current hand: {state['hand']} (Value: {state['hand_value']})")
    print(f"Dealer is showing: {state['dealer_upcard']}")

    while True:
        if len(allowed_actions) > 1:
            choices_str = ", ".join(allowed_actions[:-1]) + f", or {allowed_actions[-1]}"
        else:
            choices_str = allowed_actions[0]

        user_input = input(f"What would you like to do? ({choices_str}): ").strip().lower()

        if user_input in allowed_actions:
            return user_input
        else:
            print(f" Invalid choice. '{user_input}' is not allowed right now. Please try again.")

# TK Section Section 11


def apply_action(state, action, next_card=None):
    hand = state["hand"]

    #Implementing the function logic and adding legality checks to block unauthorized actions immediately.
    if action not in generate_actions(state):
        raise ValueError(f"'{action}' is not a legal action for this state")

    if action == "hit":
        if next_card is None:
            raise ValueError("'hit' requires a next_card")
        return hand + [next_card]

    if action == "stand":
        return hand  # hand is unchanged; turn is over

    if action == "double":
        if next_card is None:
            raise ValueError("'double' requires a next_card")
        return hand + [next_card]  # bet-doubling itself is out of scope here

    if action == "surrender":
        return hand  # hand is unchanged; turn is over, half bet forfeited (not tracked here)

    if action == "insurance":
        return hand  # side bet only: hand and turn are unaffected

    if action == "split":
        card_a, card_b = hand
        return [card_a], [card_b]

    raise ValueError(f"Unknown action: {action}") 


#testing the code
'''
def build_state(hand, dealer_upcard, flag):
    return {
        'hand': hand,
        'hand_value': hand_value(hand),
        'dealer_upcard': dealer_upcard,
        'flag': flag,
    }


def draw_card():
    return random.choice(list(RANK_VALUES.keys()))


def play_hand(hand, dealer_upcard):
    flag = "first"
    insurance_taken = False

    while True:
        state = build_state(hand, dealer_upcard, flag)

        if state["hand_value"] > 21:
            print(f"\nYour hand: {hand} (Value: {state['hand_value']})")
            print("Busted!")
            return

        action = get_user_action(state, exclude=["insurance"] if insurance_taken else [])

        if action == "hit":
            hand = apply_action(state, action, next_card=draw_card())
            flag = "later"

        elif action == "stand":
            print(f"\nStanding on {hand} (Value: {hand_value(hand)}).")
            return

        elif action == "double":
            hand = apply_action(state, action, next_card=draw_card())
            print(f"\nDoubled down. Final hand: {hand} (Value: {hand_value(hand)}).")
            return

        elif action == "surrender":
            print("\nSurrendered — half your bet is forfeited (not tracked in this demo).")
            return

        elif action == "insurance":
            apply_action(state, action)
            print("\nTook insurance (side bet — hand unaffected). Now make your real decision.")
            insurance_taken = True

        elif action == "split":
            hand_a, hand_b = apply_action(state, action)
            print(f"\nSplit into two hands: {hand_a} and {hand_b}")
            print("\n-- Playing first split hand --")
            play_hand(hand_a, dealer_upcard)
            print("\n-- Playing second split hand --")
            play_hand(hand_b, dealer_upcard)
            return


def main():
    print("Blackjack Actions — interactive demo")
    print("(built on top of parse_state / generate_actions / apply_action)\n")

    while True:
        hand = [draw_card(), draw_card()]
        dealer_upcard = draw_card()
        play_hand(hand, dealer_upcard)

        again = input("\nPlay another hand? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    # Quick sanity check (fixed to use real "first"/"later" flags, not "N")
    test = 'A,A | 5 | first'
    state = parse_state(test)
    print('Parsed State:', state)
    print('Actions:', generate_actions(state))
    print()

    main()
'''
