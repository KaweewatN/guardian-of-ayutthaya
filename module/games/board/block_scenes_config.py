"""
Block Scenes Configuration
Defines the sequence of scenes to display for each block (1-60)
Each block shows: empty -> npc -> npc-details -> npc-dialogue
"""

def get_block_scene_sequence(block_number):
    """
    Get the sequence of scenes to display for a given block number.
    
    Args:
        block_number: Block number (1-60)
        
    Returns:
        list: List of scene dictionaries with folder and filename info
              Returns empty list if block has no scenes
    """
    if not (1 <= block_number <= 60):
        return []
    
    scenes = []
    
    # Scene 1: Empty scene (blocks 1-60)
    scenes.append({
        'folder': 'empty',
        'filename': f'{block_number}.png',
        'type': 'empty'
    })
    
    # Scene 2: NPC scene (blocks 1-60)
    scenes.append({
        'folder': 'npc',
        'filename': f'{block_number}.png',
        'type': 'npc'
    })
    
    # Scene 3: NPC Details (blocks 1-60)
    scenes.append({
        'folder': 'npc-details',
        'filename': f'{block_number}.png',
        'type': 'npc-details'
    })
    
    # Scene 4: NPC Dialogue (blocks 21-60 only, based on available files)
    if 21 <= block_number <= 60:
        scenes.append({
            'folder': 'npc-dialogue',
            'filename': f'{block_number}.png',
            'type': 'npc-dialogue'
        })
    
    return scenes


def get_all_blocks_config():
    """
    Get configuration for all blocks.
    
    Returns:
        dict: {block_number: [scene_list]}
    """
    config = {}
    for block_num in range(1, 61):
        config[block_num] = get_block_scene_sequence(block_num)
    return config


def get_block_jump_destination(block_number, from_jump=False):
    """
    Get the destination block for special block jumps.
    
    Args:
        block_number: Current block number
        from_jump: If True, indicates this block was reached via a jump (prevents chain jumping)
        
    Returns:
        int or None: Destination block number if there's a special jump, None otherwise
    """
    # If we arrived at this block via a jump, don't trigger another jump
    # This prevents infinite loops and chain jumping
    if from_jump:
        return None
    
    # Forward jumps (ladders/portals that move you ahead)
    forward_jumps = {
        3: 6,
        27: 35,
        38: 42,
        50: 55
    }
    
    # Backward jumps (snakes/traps that move you back)
    backward_jumps = {
        13: 8,
        21: 16,
        30: 23,
        35: 28,
        44: 38,
        55: 49
    }
    
    # Check forward jumps first
    if block_number in forward_jumps:
        return forward_jumps[block_number]
    
    # Check backward jumps
    if block_number in backward_jumps:
        return backward_jumps[block_number]
    
    # No special jump for this block
    return None


# For debugging/reference
if __name__ == "__main__":
    print("Block Scenes Configuration")
    print("=" * 60)
    
    # Show config for a few sample blocks
    for block_num in [1, 5, 20, 25, 30, 60]:
        scenes = get_block_scene_sequence(block_num)
        print(f"\nBlock {block_num}:")
        for i, scene in enumerate(scenes, 1):
            print(f"  {i}. {scene['folder']}/{scene['filename']} ({scene['type']})")
    
    print("\n" + "=" * 60)
    print(f"Total blocks configured: {len(get_all_blocks_config())}")
    
    # Show special block jumps
    print("\n" + "=" * 60)
    print("Special Block Jumps:")
    print("-" * 60)
    
    print("\nForward Jumps (Ladders/Portals):")
    for block in [3, 27, 38, 50]:
        dest = get_block_jump_destination(block)
        print(f"  Block {block} -> Block {dest}")
    
    print("\nBackward Jumps (Snakes/Traps):")
    for block in [13, 21, 30, 35, 44, 55]:
        dest = get_block_jump_destination(block)
        print(f"  Block {block} -> Block {dest}")

