# Photo Hunt Mini-Game

A "spot the difference" mini-game for Guardian of Ayutthaya.

## Overview

The Photo Hunt game is triggered on specific blocks (22 and 34) where players must find differences between two similar images within a time limit.

## Game Flow

1. **Intro Screen**: Instructions are displayed
2. **Viewing Phase**: Player sees the "before" image for 5 seconds
3. **Finding Phase**: Player sees the "after" image and has 5 seconds to click on the difference
4. **Result Screen**: Shows win/lose result

## Blocks

- **Block 22**: Temple scene - Find the blue spirit/ghost figure
- **Block 34**: Elephant scene - Find the monkey on the building

## Images

Images are stored in `assets/scene/event/photo-hunt/`:

- `22-before.png` / `22-after.png`
- `34-before.png` / `34-after.png`

## Clickable Areas

Each block has a defined clickable area (difference location):

### Block 22

- **Location**: Right side of screen (blue spirit figure)
- **Coordinates**: x=900, y=450
- **Radius**: 80 pixels

### Block 34

- **Location**: Top of white building (monkey)
- **Coordinates**: x=580, y=260
- **Radius**: 70 pixels

## Configuration

To add new Photo Hunt blocks:

1. Add before/after images to `assets/scene/event/photo-hunt/`
2. Add the block number to `photo_hunt_blocks` list in `board_block.py`
3. Add difference coordinates in `photo_hunt.py` `differences` dict:
   ```python
   self.differences = {
       block_number: {'x': x_pos, 'y': y_pos, 'radius': click_radius}
   }
   ```

## Testing

Run the test script:

```bash
cd module/games/events/photo-hunt
python test_photo_hunt.py
```

## Win/Lose Conditions

- **Win**: Player clicks within the difference radius during the 5-second finding phase
- **Lose**: Time runs out (5 seconds) without finding the difference
