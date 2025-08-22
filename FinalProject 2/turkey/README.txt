# Mmmmm Gobble, Gobble - Pygame Project

## Overview
"Mmmmm Gobble, Gobble" is a fun, Thanksgiving-themed Pygame project where players click on moving turkeys to turn them into roasts. After defeating all turkeys, a boss turkey (Turkethimus) appears, requiring multiple hits to defeat. The game features a start menu with "Start" and "Quit" options, sound effects, and a victory screen with a cornucopia and celebratory message.

## Requirements
- Python 3.x
- Pygame library (`pip install pygame`)
- Required assets (must be in the same directory as the script):
  - Images: `Turkethimus.png`, `table.jpg`, `turkey.jpeg`, `roast.jpeg`, `cornucopia.jpg`
  - Sounds: `goofygoober.wav`, `erikaturkeyscream.wav`, `heaven.wav`, `bossturkeytheme.mp3`

## How to Run
1. Ensure Python and Pygame are installed.
2. Place all required image and sound files in the same directory as the game script.
3. Run the script using Python:
   ```
   python turkey.py
   ```
4. The game will start with a menu. Click "Start" to play or "Quit" to exit.

## Gameplay
- **Menu**: Use the mouse to click "Start" to begin the game or "Quit" to exit.
- **Objective**: Click on moving turkeys to turn them into roasts, which fall off the screen.
- **Boss Battle**: After defeating all turkeys, a boss turkey (Turkethimus) spawns. Click it five times to defeat it.
- **Victory**: Upon defeating the boss, a cornucopia appears with the message "Have a Big Back Thanksgiving."
- **Controls**:
  - Left-click: Interact with menu buttons or attack turkeys/boss.
  - ESC: Exit the game (returns to menu or closes).
  - Close window: Exit the game.

## Notes
- The game runs at 60 FPS for smooth performance.
- Background music (`goofygoober.wav`) plays during the menu and game, switching to `bossturkeytheme.mp3` during the boss battle.
- Sound effects play when turkeys are clicked (`erikaturkeyscream.wav`) and when the boss is defeated (`heaven.wav`).
- Ensure all asset files are present to avoid runtime errors.

## Credits
- Developed as a class project with contributions from Erika (#insert contributions), Bradley (#insert contributions), Landin (#insert contributions), and Mel (main menu code implementation), .
- Assets: Custom images and sounds for a Thanksgiving theme.

## Troubleshooting
- If the game crashes, check that all image and sound files are in the correct directory.
- Run the script from a terminal to view error messages: `python turkey.py`.
- Ensure Pygame is installed: `pip install pygame`.