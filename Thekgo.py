import random

RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}

# Thekgo Section mANFDHGD


def hand_value(cards):
    total = sum(RANK_VALUES[card] for card in cards)
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

# Mtha section
# Mtha in the building!


def parse_state(text):
    #flag is where the decisions will be displayed
    #split into the players hand, the dealers face up card and the flag at the end
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]

    #parse takes the result and returns it in the format asked for
    hand = [rank.strip() for rank in hand_str.split(",")]

#brings back the results as a dictionary
    return {
        'hand': hand,
        'hand_value': hand_value(hand),
        'dealer_upcard': dealer_upcard,
        'flag': flag
    }

# TK section


def generate_actions(state):
    hand = state["hand"]
    actions = ["hit", "stand"]
    # Double down: typically only allowed on the first two cards
    if len(hand) == 2:
    	actions.append("double")
    	# Split: only if both cards have the rank
    	if hand [0] == hand[1]:
    		actions.append("split")
    	return actions


# New Input Handling Section
def get_user_action(state):
    """
    Presents allowed actions to the user, prompts for input,
    and returns a validated action string.
    """
    allowed_actions = generate_actions(state)

    print(f"\nYour current hand: {state['hand']} (Value: {state['hand_value']})")
    print(f"Dealer is showing: {state['dealer_upcard']}")

    while True:
        # Format actions cleanly, e.g., "hit, stand, double, or split"
        if len(allowed_actions) > 1:
            choices_str = ", ".join(allowed_actions[:-1]) + f", or {allowed_actions[-1]}"
        else:
            choices_str = allowed_actions[0]

        user_input = input(f"What would you like to do? ({choices_str}): ").strip().lower()

        if user_input in allowed_actions:
            return user_input
        else:
            print(f" Invalid choice. '{user_input}' is not allowed right now. Please try again.")
    	
# Generic Section 11


def apply_action(state, action, next_card=None):
    raise NotImplementedError("This function is not implemented yet.")

test = 'A,A | 5 | N'
state = parse_state(test)
a_actions = generate_actions(state)

print('Parsed State:', state)
print('A Actions:', a_actions)
