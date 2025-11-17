"""
Print all random card configurations without UI
"""
from random_event import RandomCard


def main():
    # All random card block numbers
    block_numbers = [4, 8, 12, 16, 19, 23, 26, 29, 33, 36, 39, 42, 45, 48, 52, 56]
    
    # Print all block configurations
    print("=" * 80)
    print("RANDOM CARD CONFIGURATIONS FOR ALL BLOCKS")
    print("=" * 80)
    
    for block_num in block_numbers:
        cards = RandomCard.BLOCK_CARDS.get(block_num, [])
        print(f"\nSpace {block_num}:")
        for i, card in enumerate(cards, 1):
            if card == "good":
                effect = "Divine Blessing - Gain one letter for your collection"
            elif card == "bad":
                effect = "Careless Mistake - Return one collected letter back to the deck"
            elif card.startswith("forward-"):
                spaces = card.replace("forward-", "")
                effect = f"Warp - Move forward {spaces} spaces"
            elif card.startswith("backward-"):
                spaces = card.replace("backward-", "")
                effect = f"Warp - Move backward {spaces} spaces"
            else:
                effect = "Unknown"
            print(f"  Card {i}: {card:15s} -> {effect}")
    
    print("=" * 80)
    print(f"Total blocks with random cards: {len(block_numbers)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
