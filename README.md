# 🐯 Macan Hungry - Jungle Adventure Game

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

A vibrant, arcade-style maze game where you play as a fierce but adorable tiger collecting food in a mystical jungle labyrinth while avoiding forest spirits!

## 🎮 Game Overview

**Macan Hungry** is a modern take on classic arcade maze games, featuring:
- A cute yet fierce tiger protagonist with expressive animations
- Stylized jungle maze environment with atmospheric lighting
- Dynamic enemy AI with unique personalities
- Power-up system that turns the tables on your enemies
- Multiple levels with increasing difficulty
- Vivid colors and smooth animations

## ✨ Features

### 🐅 Tiger Character
- Expressive animations with mouth movement
- Big, round cartoon eyes
- Smooth directional movement
- Power-up transformation with glowing effects

### 🌳 Jungle Environment
- Stone walls and bamboo fences
- Glowing fireflies for atmosphere
- Dark jungle ambiance
- Procedural maze layout

### 👻 Enemy Types
Each enemy has a unique personality and color:
- **Red Enemy (Chaser)**: Aggressively pursues the tiger
- **Pink Enemy (Ambusher)**: Tries to predict and cut off the tiger's path
- **Cyan Enemy (Patroller)**: Systematically patrols the maze
- **Orange Enemy (Random)**: Unpredictable movement patterns

### 🍖 Food System
- **Regular Food**: Meat, fish, and chicken legs (10 points each)
- **Power Food**: Glowing power meat (50 points + power mode)
- **Power Mode**: Tiger grows larger and can eat enemies (200 points each)

### 🎯 Game Mechanics
- Lives system represented by tiger paws (🐾)
- Score tracking
- Level progression
- Scatter mode for enemies
- Collision detection
- Win condition when all food is collected

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PySide6

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/danx123/macan-hungry.git
cd macan-hungry
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install PySide6
```

4. **Run the game**
```bash
python macan_hungry.py
```

## 🎮 How to Play

### Controls
- **Arrow Keys** or **WASD**: Move the tiger
  - ➡️ Right Arrow / D: Move right
  - ⬇️ Down Arrow / S: Move down
  - ⬅️ Left Arrow / A: Move left
  - ⬆️ Up Arrow / W: Move up

### Objective
1. Collect all food items in the maze
2. Avoid forest spirits (enemies)
3. Eat power food to activate power mode
4. Chase and eat enemies during power mode for bonus points
5. Complete levels to progress

### Scoring
- Regular food: 10 points
- Power food: 50 points
- Eating an enemy: 200 points

### Tips & Strategies
- **Plan your route**: Try to collect food efficiently while avoiding enemies
- **Use corners**: Enemies have a harder time cornering you in tight spaces
- **Save power food**: Use power-ups strategically when surrounded
- **Watch enemy patterns**: Each enemy type behaves differently
- **Scatter mode**: Enemies periodically enter scatter mode and retreat to corners

## 🏗️ Project Structure

```
macan-hungry/
│
├── macan_hungry.py          # Main game file
├── README.md                # This file
├── LICENSE                  # MIT License

```

## 🔧 Technical Details

### Architecture

The game is built using object-oriented principles with the following key classes:

#### **Entity** (Base Class)
- Position tracking (x, y)
- Target position for smooth movement
- Direction management

#### **Tiger** (Player Character)
- Inherits from Entity
- Animation state management
- Mouth animation for roaring effect

#### **Enemy** (AI Characters)
- Inherits from Entity
- Personality-based AI (chase, patrol, random, ambush)
- Scared state during power mode
- Scatter mode behavior
- Pathfinding logic

#### **GameWidget** (Main Game Logic)
- Maze rendering
- Collision detection
- Score and lives management
- Game state machine
- Timer-based updates

#### **MainWindow** (UI Container)
- Score display
- Lives indicator
- Control buttons
- Game over dialog

### Game Loop

The game uses two timers:
1. **Game Timer** (50ms): Updates game logic at 20 FPS
2. **Animation Timer** (100ms): Updates visual animations

### Rendering

Custom painting using QPainter:
- Gradient backgrounds
- Radial gradients for glowing effects
- Custom shapes for characters
- Dynamic firefly particles

## 🎨 Customization

### Modifying the Maze

Edit the `MAZE_LAYOUT` array in the code:
- `0`: Wall
- `1`: Path with regular food
- `2`: Empty path
- `3`: Path with power food

```python
MAZE_LAYOUT = [
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,3,0,1,0],
    [0,1,1,1,0],
    [0,0,0,0,0],
]
```

### Adjusting Difficulty

Modify these constants:
```python
# Speed settings
self.move_cooldown = 3      # Lower = faster tiger
self.enemy_move_cooldown = 5  # Lower = faster enemies

# Power mode duration
self.power_timer = 100       # Higher = longer power mode
```

### Changing Colors

Enemy colors can be modified in the `init_game` method:
```python
Enemy(8, 9, QColor(255, 0, 0), 'chase'),  # Red
```

## 🐛 Known Issues

- Enemies might occasionally overlap at spawn points
- Fireflies don't check for wall collisions
- No sound effects (planned for future release)

## 🚀 Future Enhancements

- [ ] Sound effects and background music
- [ ] More enemy types
- [ ] Different maze layouts per level
- [ ] High score leaderboard
- [ ] Difficulty settings
- [ ] Touch controls for mobile
- [ ] Multiplayer mode
- [ ] Boss levels
- [ ] Power-up variety (speed boost, shield, etc.)
- [ ] Animated transitions between levels

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test your changes thoroughly
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025 Macan Hungry Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Credits

**Concept & Design**: Inspired by classic arcade games
**Development**: Built with PySide6
**Art Style**: Cartoon jungle theme with vibrant colors

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/danx123/macan-hungry/issues)
- **Discussions**: [GitHub Discussions](https://github.com/danx123/macan-hungry/discussions)

## 🌟 Acknowledgments

Special thanks to:
- The PySide6 development team
- Classic arcade game developers for inspiration
- The open-source community

---

**Enjoy the game! May your tiger always find the tastiest food! 🐯🍖**

## 📸 Screenshots
<img width="1365" height="767" alt="Screenshot 2025-12-10 103129" src="https://github.com/user-attachments/assets/23e1d084-d8a1-48b4-a4fc-1138bf05b587" />
<img width="1365" height="767" alt="Screenshot 2025-12-10 103143" src="https://github.com/user-attachments/assets/b1594ce2-bbd1-4505-b161-6d5b12a8fd3a" />





---

Made with ❤️ and 🐯
