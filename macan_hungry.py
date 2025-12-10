import sys
import random
import math
import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Signal, QSize
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, 
                           QPainterPath, QRadialGradient, QLinearGradient)

# --- Constants ---
CELL_SIZE = 40
MAZE_WIDTH = 19
MAZE_HEIGHT = 21
base_width = MAZE_WIDTH * CELL_SIZE
base_height = MAZE_HEIGHT * CELL_SIZE

# --- SETUP SAVE PATH (MODIFIED) ---
# Menggunakan Local AppData: C:\Users\Username\AppData\Local\MacanHungry
app_data_path = os.getenv('LOCALAPPDATA')
if not app_data_path:
    # Fallback jika bukan Windows atau variabel env tidak ada
    app_data_path = os.path.expanduser("~")

SAVE_DIR = os.path.join(app_data_path, "MacanHungry")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

SAVE_FILE = os.path.join(SAVE_DIR, "macan_save.json")
# ----------------------------------

# Maze layout awal (Level 1 statis)
MAZE_LAYOUT = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
    [0,3,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,3,0],
    [0,1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0],
    [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
    [0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
    [2,2,2,0,1,0,1,1,1,1,1,1,1,0,1,0,2,2,2],
    [0,0,0,0,1,0,1,0,0,2,0,0,1,0,1,0,0,0,0],
    [2,2,2,2,1,1,1,0,2,2,2,0,1,1,1,2,2,2,2],
    [0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0],
    [2,2,2,0,1,0,1,1,1,1,1,1,1,0,1,0,2,2,2],
    [0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
    [0,1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0],
    [0,3,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,3,0],
    [0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0],
    [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
    [0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# --- Classes ---

class Particle:
    """Efek visual untuk ledakan kecil saat makan."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 1.0  # Opacity 1.0 to 0.0
        self.color = color
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05
        self.size *= 0.95

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.direction = 0
        
    def get_rect(self):
        return QRectF(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

class Tiger(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.animation_frame = 0
        self.mouth_open = False
        
    def update_animation(self):
        self.animation_frame = (self.animation_frame + 1) % 20
        if self.animation_frame % 5 == 0: 
            self.mouth_open = not self.mouth_open

class Enemy(Entity):
    def __init__(self, x, y, color, personality):
        super().__init__(x, y)
        self.color = color
        self.personality = personality
        self.scared = False
        self.scatter_mode = False
        
    def choose_direction(self, tiger_x, tiger_y, maze):
        corners = [(1, 1), (MAZE_WIDTH-2, 1), (1, MAZE_HEIGHT-2), (MAZE_WIDTH-2, MAZE_HEIGHT-2)]
        target = (self.x, self.y)
        
        if self.scared:
            dx = self.x - tiger_x
            dy = self.y - tiger_y
        elif self.scatter_mode:
            # Menggunakan hash dari string nama warna agar deterministik
            corner_index = hash(self.color.name()) % 4
            target = corners[corner_index]
            dx = target[0] - self.x
            dy = target[1] - self.y
        else:
            if self.personality == 'chase':
                dx = tiger_x - self.x
                dy = tiger_y - self.y
            elif self.personality == 'ambush':
                dx = tiger_x - self.x + random.randint(-3, 3)
                dy = tiger_y - self.y + random.randint(-3, 3)
            elif self.personality == 'random':
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
            else:  # patrol
                dx = random.randint(-2, 2)
                dy = random.randint(-2, 2)
        
        directions = []
        if abs(dx) > abs(dy):
            if dx > 0: directions = [0, 1, 3, 2] 
            else: directions = [2, 1, 3, 0]
        else:
            if dy > 0: directions = [1, 0, 2, 3]
            else: directions = [3, 0, 2, 1]
            
        for d in directions:
            new_x, new_y = self.x, self.y
            if d == 0: new_x += 1
            elif d == 1: new_y += 1
            elif d == 2: new_x -= 1
            elif d == 3: new_y -= 1
            
            if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
                if maze[new_y][new_x] != 0:
                    self.target_x = new_x
                    self.target_y = new_y
                    self.direction = d
                    return
        
        # Fallback movement if stuck
        for d in range(4):
            new_x, new_y = self.x, self.y
            if d == 0: new_x += 1
            elif d == 1: new_y += 1
            elif d == 2: new_x -= 1
            elif d == 3: new_y -= 1
            if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
                if maze[new_y][new_x] != 0:
                    self.target_x = new_x
                    self.target_y = new_y
                    self.direction = d
                    return

class GameWidget(QWidget):
    # Signals
    game_over_signal = Signal(int)
    score_updated = Signal(int)
    lives_updated = Signal(int)
    level_updated = Signal(int)
    msg_signal = Signal(str, str) # Untuk menampilkan pesan ke window utama

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # State
        self.score = 0
        self.lives = 3
        self.level = 1
        self.power_mode = False
        self.power_timer = 0
        self.game_active = False
        self.game_paused = False
        
        self.particles = []
        self.global_pulse = 0.0
        
        self.init_game()
        
        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(50) 
        
        # Background elements
        self.fireflies = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(40)]
        self.firefly_brightness = [random.random() for _ in range(40)]

    def generate_random_maze(self):
        """Membuat maze acak yang simetris dan PASTI terhubung."""
        # 1. Inisialisasi grid penuh tembok (0)
        new_maze = [[0 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        
        # 2. Algoritma DFS (Recursive Backtracker) untuk separuh kiri
        stack = []
        start_pos = (1, 1)
        new_maze[1][1] = 1
        stack.append(start_pos)
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            
            # Cek tetangga dengan jarak 2 sel
            directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                # Batas kanan adalah 8 (setengah lebar maze)
                if 1 <= nx < 9 and 1 <= ny < MAZE_HEIGHT - 1:
                    if new_maze[ny][nx] == 0:
                        neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                new_maze[cy + dy//2][cx + dx//2] = 1
                new_maze[ny][nx] = 1
                stack.append((nx, ny))
            else:
                stack.pop()

        # 3. Mirroring (Cerminkan bagian kiri ke kanan)
        for y in range(MAZE_HEIGHT):
            for x in range(9): # 0 sampai 8
                val = new_maze[y][x]
                new_maze[y][x] = val
                new_maze[y][MAZE_WIDTH - 1 - x] = val 
            
            # Hubungkan tengah secara horizontal jika kiri-kanan terbuka
            if new_maze[y][8] == 1:
                new_maze[y][9] = 1 
                new_maze[y][10] = 1

        # 4. Buat Ghost House (Area Musuh)
        for y in range(8, 13):
            for x in range(7, 12):
                if y == 8 or y == 12 or x == 7 or x == 11:
                     if not (y == 8 and x == 9): 
                        new_maze[y][x] = 0 
                else:
                    new_maze[y][x] = 2 
        
        new_maze[8][9] = 2 # Pintu hantu

        # 5. Buat Loop (Jebol tembok acak)
        for _ in range(20): # Naikkan sedikit jumlah loop agar map lebih terbuka
            rx = random.randint(2, MAZE_WIDTH - 3)
            ry = random.randint(2, MAZE_HEIGHT - 3)
            if new_maze[ry][rx] == 0:
                # Pastikan tidak merusak dinding luar
                if 0 < rx < MAZE_WIDTH-1 and 0 < ry < MAZE_HEIGHT-1:
                     new_maze[ry][rx] = 1

        # --- FIX UTAMA ADA DI SINI ---
        # 6. Pastikan posisi spawn macan (9, 15) TERHUBUNG ke area tengah
        # Kita paksa buat jalur vertikal (koridor) dari bawah rumah hantu (y=12) 
        # turun sampai ke posisi spawn (y=15) di kolom tengah (x=9).
        for y in range(12, 17): 
            if y < MAZE_HEIGHT - 1:
                new_maze[y][9] = 1
        
        # Buka sedikit area samping spawn agar tidak sempit
        new_maze[15][8] = 1
        new_maze[15][10] = 1
        # -----------------------------

        # 7. Isi Makanan dan Power Pellet
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                # Jangan taruh makanan di dalam rumah hantu (nilai 2) atau tembok (0)
                if new_maze[y][x] == 1:
                    if (x < 2 or x > MAZE_WIDTH-3) and (y < 3 or y > MAZE_HEIGHT-4):
                        new_maze[y][x] = 3 # Power Pellet
                    else:
                        new_maze[y][x] = 1 # Makanan
        
        return new_maze

    def init_game(self):
        # Gunakan layout default untuk level 1, generate acak untuk level > 1
        if self.level == 1:
            self.maze = [row[:] for row in MAZE_LAYOUT]
        else:
            self.maze = self.generate_random_maze()

        self.tiger = Tiger(9, 15)
        self.enemies = [
            Enemy(8, 9, QColor(255, 50, 50), 'chase'),
            Enemy(9, 9, QColor(255, 105, 180), 'ambush'),
            Enemy(10, 9, QColor(0, 255, 255), 'patrol'),
            Enemy(9, 10, QColor(255, 165, 0), 'random'),
        ]
        self.next_move = None
        self.move_cooldown = 0
        self.enemy_move_cooldown = 0
        self.scatter_timer = 0
        self.particles = []
        
        # Reset signal values
        self.score_updated.emit(self.score)
        self.lives_updated.emit(self.lives)
        self.level_updated.emit(self.level)

    def reset_full_game(self):
        """Merestart game sepenuhnya ke level 1."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.init_game()
        self.game_active = False # Harus tekan Enter lagi untuk start
        self.game_paused = False
        self.timer.stop()
        self.update()
        self.msg_signal.emit("Reset", "Game has been reset to Level 1.")

    def save_game(self):
        """Menyimpan progress game."""
        if self.lives <= 0:
            self.msg_signal.emit("Error", "Cannot save when Game Over!")
            return

        state = {
            "score": self.score,
            "lives": self.lives,
            "level": self.level,
            "maze": self.maze, # Simpan kondisi makanan
            "enemies": [{"x": e.x, "y": e.y} for e in self.enemies],
            "tiger": {"x": self.tiger.x, "y": self.tiger.y}
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(state, f)
            self.msg_signal.emit("Success", f"Game Saved Successfully to:\n{SAVE_FILE}")
        except Exception as e:
            self.msg_signal.emit("Error", f"Failed to save: {str(e)}")

    def load_game(self):
        """Memuat progress game."""
        if not os.path.exists(SAVE_FILE):
            self.msg_signal.emit("Error", f"No save file found at:\n{SAVE_FILE}")
            return

        try:
            with open(SAVE_FILE, 'r') as f:
                state = json.load(f)
            
            self.score = state["score"]
            self.lives = state["lives"]
            self.level = state["level"]
            self.maze = state["maze"]
            
            self.tiger.x = state["tiger"]["x"]
            self.tiger.y = state["tiger"]["y"]
            
            # Load enemy positions if count matches
            if len(state["enemies"]) == len(self.enemies):
                for i, e_data in enumerate(state["enemies"]):
                    self.enemies[i].x = e_data["x"]
                    self.enemies[i].y = e_data["y"]
                    self.enemies[i].target_x = e_data["x"]
                    self.enemies[i].target_y = e_data["y"]

            self.score_updated.emit(self.score)
            self.lives_updated.emit(self.lives)
            self.level_updated.emit(self.level)
            
            self.game_active = False # Pause saat baru load
            self.game_paused = True
            self.timer.stop() # Stop dulu logika game loop
            self.update() # Repaint
            
            self.msg_signal.emit("Success", "Game Loaded! Press 'P' or 'Enter' to continue.")
            
        except Exception as e:
            self.msg_signal.emit("Error", f"Failed to load: {str(e)}")

    def start_game(self):
        self.game_active = True
        self.game_paused = False
        self.timer.start(50) 
        self.setFocus()

    def reset_level(self):
        self.tiger.x, self.tiger.y = 9, 15
        self.next_move = None
        for i, e in enumerate(self.enemies):
            e.x = 8 + (i % 3)
            e.y = 9
            e.target_x = e.x
            e.target_y = e.y

    def spawn_particles(self, x, y, color):
        px = x * CELL_SIZE + CELL_SIZE/2
        py = y * CELL_SIZE + CELL_SIZE/2
        for _ in range(8):
            self.particles.append(Particle(px, py, color))

    def update_animation(self):
        self.global_pulse += 0.2
        
        if self.game_active and not self.game_paused:
            self.tiger.update_animation()
            
            for i in range(len(self.firefly_brightness)):
                self.firefly_brightness[i] += random.uniform(-0.1, 0.1)
                self.firefly_brightness[i] = max(0.1, min(1.0, self.firefly_brightness[i]))
            
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)
                    
            self.update()
        elif not self.game_active or self.game_paused:
            # Tetap repaint untuk animasi idle/menu
            self.update()

    def update_game(self):
        if not self.game_active or self.game_paused:
            return
        
        # 1. Tiger Movement
        if self.move_cooldown <= 0:
            if self.next_move is not None:
                dx = [1, 0, -1, 0][self.next_move]
                dy = [0, 1, 0, -1][self.next_move]
                new_x, new_y = self.tiger.x + dx, self.tiger.y + dy
                
                if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
                    if self.maze[new_y][new_x] != 0:
                        self.tiger.x = new_x
                        self.tiger.y = new_y
                        self.tiger.direction = self.next_move
                        
                        # Eat Logic
                        cell = self.maze[new_y][new_x]
                        if cell == 1:
                            self.score += 10
                            self.maze[new_y][new_x] = 2
                            self.spawn_particles(new_x, new_y, QColor(255, 200, 100))
                            self.score_updated.emit(self.score)
                        elif cell == 3:
                            self.score += 50
                            self.maze[new_y][new_x] = 2
                            self.power_mode = True
                            # Leveling: Power bertahan lebih sebentar di level tinggi
                            base_time = 150
                            level_penalty = min(100, (self.level - 1) * 10)
                            self.power_timer = base_time - level_penalty
                            
                            self.spawn_particles(new_x, new_y, QColor(255, 255, 0))
                            self.score_updated.emit(self.score)
                            for enemy in self.enemies:
                                enemy.scared = True
                        
                        self.move_cooldown = 2 
        else:
            self.move_cooldown -= 1
        
        # 2. Power Mode Logic
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
                for enemy in self.enemies:
                    enemy.scared = False
        
        # 3. Enemy Movement & Leveling Difficulty
        # Leveling: Musuh makin cepat (cooldown makin kecil)
        base_speed = 6 if self.power_mode else 4
        # Kurangi delay per 3 level
        speed_modifier = 0 if self.power_mode else min(2, (self.level - 1) // 3)
        current_speed_threshold = max(2, base_speed - speed_modifier)

        if self.enemy_move_cooldown <= 0:
            for enemy in self.enemies:
                # Slow down scared enemies
                if enemy.scared and self.enemy_move_cooldown % 2 != 0:
                    continue
                enemy.choose_direction(self.tiger.x, self.tiger.y, self.maze)
                enemy.x = enemy.target_x
                enemy.y = enemy.target_y
            self.enemy_move_cooldown = current_speed_threshold
        else:
            self.enemy_move_cooldown -= 1
        
        # 4. Scatter Logic
        self.scatter_timer += 1
        if self.scatter_timer % 200 == 0:
            for enemy in self.enemies:
                enemy.scatter_mode = not enemy.scatter_mode

        # 5. Collisions
        for enemy in self.enemies:
            if self.tiger.x == enemy.x and self.tiger.y == enemy.y:
                if self.power_mode:
                    self.score += 200 * self.level # Skor lebih besar di level tinggi
                    self.spawn_particles(enemy.x, enemy.y, QColor(255, 255, 255))
                    self.score_updated.emit(self.score)
                    # Send enemy home
                    enemy.x = 9
                    enemy.y = 9
                    enemy.scared = False
                else:
                    self.lives -= 1
                    self.lives_updated.emit(self.lives)
                    self.spawn_particles(self.tiger.x, self.tiger.y, QColor(255, 0, 0))
                    
                    if self.lives <= 0:
                        self.game_active = False
                        self.timer.stop()
                        self.game_over_signal.emit(self.score)
                        self.update()
                    else:
                        self.reset_level()
        
        # 6. Level Complete
        food_left = sum(row.count(1) + row.count(3) for row in self.maze)
        if food_left == 0:
            self.level += 1
            self.level_updated.emit(self.level)
            
            # --- MODIFIED: Generate Random Maze on Level Up ---
            self.maze = self.generate_random_maze()
            # --------------------------------------------------
            
            self.reset_level()
            self.game_paused = True # Pause sebentar antar level
            self.msg_signal.emit("Level Up!", f"Entering Level {self.level}\nMap Scrambled!\nEnemies are faster!")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.parent().parent().close() 
            return

        if not self.game_active:
            if key in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space]:
                if self.lives > 0:
                    self.start_game()
                else:
                    # Restart if game over
                    self.reset_full_game()
                    self.start_game()
            return
            
        if key == Qt.Key_P:
            self.game_paused = not self.game_paused
            self.update()
            
        if key == Qt.Key_Right or key == Qt.Key_D: self.next_move = 0
        elif key == Qt.Key_Down or key == Qt.Key_S: self.next_move = 1
        elif key == Qt.Key_Left or key == Qt.Key_A: self.next_move = 2
        elif key == Qt.Key_Up or key == Qt.Key_W: self.next_move = 3
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
            
        painter.setRenderHint(QPainter.Antialiasing)
        
        # --- Responsive Scaling ---
        scale_x = self.width() / base_width
        scale_y = self.height() / base_height
        scale = min(scale_x, scale_y) * 0.9 
        
        trans_x = (self.width() - (base_width * scale)) / 2
        trans_y = (self.height() - (base_height * scale)) / 2
        
        # Background
        painter.fillRect(self.rect(), QColor(15, 20, 30))
        
        painter.translate(trans_x, trans_y)
        painter.scale(scale, scale)
        
        # Maze Box
        bg_rect = QRectF(0, 0, base_width, base_height)
        painter.setBrush(QColor(25, 35, 45))
        painter.setPen(QPen(QColor(50, 60, 80), 4))
        painter.drawRoundedRect(bg_rect, 10, 10)
        
        # Fireflies
        for i, (fx, fy) in enumerate(self.fireflies):
            bx = (fx / 1000) * base_width
            by = (fy / 1000) * base_height
            brightness = self.firefly_brightness[i]
            color = QColor(100, 255, 100, int(brightness * 150))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(bx, by), 4, 4)

        # Cells
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                cell = self.maze[y][x]
                cx = x * CELL_SIZE + CELL_SIZE/2
                cy = y * CELL_SIZE + CELL_SIZE/2
                rect = QRectF(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if cell == 0:
                    painter.setBrush(QColor(40, 50, 70))
                    painter.setPen(QPen(QColor(60, 75, 100), 2))
                    painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 4, 4)
                elif cell == 1:
                    pulse = (math.sin(self.global_pulse + x + y) + 1) * 2
                    painter.setBrush(QColor(255, 180, 180))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(cx, cy), 4 + pulse, 4 + pulse)
                elif cell == 3:
                    pulse = (math.sin(self.global_pulse * 2) + 1) * 4
                    grad = QRadialGradient(cx, cy, 15)
                    grad.setColorAt(0, QColor(255, 255, 0, 255))
                    grad.setColorAt(1, QColor(255, 100, 0, 0))
                    painter.setBrush(QBrush(grad))
                    painter.drawEllipse(QPointF(cx, cy), 12 + pulse, 12 + pulse)
                    painter.setBrush(QColor(255, 255, 200))
                    painter.drawEllipse(QPointF(cx, cy), 6, 6)
                elif cell == 2 and self.level > 1:
                    # Debug visual for empty paths in generated levels (optional)
                    pass

        # Entities
        for enemy in self.enemies:
            self.draw_enemy(painter, enemy)
            
        self.draw_tiger(painter, self.tiger)
        
        # Particles
        for p in self.particles:
            painter.setBrush(p.color)
            painter.setOpacity(p.life)
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)
            painter.setOpacity(1.0) 

        painter.resetTransform()
        
        # UI Overlays
        if not self.game_active and self.lives > 0:
            self.draw_overlay(painter, "MACAN HUNGRY", "Press ENTER to Start")
        elif not self.game_active and self.lives <= 0:
            self.draw_overlay(painter, "GAME OVER", f"Final Score: {self.score}\nPress ENTER to Restart")
        elif self.game_paused:
             self.draw_overlay(painter, "PAUSED", "Press P to Resume")

        # FIX: End painter explicitly
        painter.end()

    def draw_overlay(self, painter, title, subtitle):
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        
        painter.setPen(QColor(255, 200, 0))
        font = QFont('Arial', 48, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{title}\n\n\n")
        
        painter.setPen(QColor(255, 255, 255))
        font.setPointSize(24)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"\n\n{subtitle}")

    def draw_tiger(self, painter, tiger):
        cx = tiger.x * CELL_SIZE + CELL_SIZE/2
        cy = tiger.y * CELL_SIZE + CELL_SIZE/2
        size = CELL_SIZE * 0.85
        
        painter.save()
        painter.translate(cx, cy)
        
        rotations = [0, 90, 180, 270] 
        painter.rotate(rotations[tiger.direction])
        
        if self.power_mode:
            grad = QRadialGradient(0, 0, size)
            grad.setColorAt(0, QColor(255, 255, 255, 100))
            grad.setColorAt(1, QColor(255, 200, 0, 0))
            painter.setBrush(grad)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-size, -size, size*2, size*2)
            
        painter.setBrush(QColor(255, 165, 0)) 
        painter.setPen(QPen(QColor(180, 100, 0), 2))
        painter.drawEllipse(int(-size/2), int(-size/2), int(size), int(size))
        
        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)
        painter.drawPolygon([QPointF(0, -size/2), QPointF(-4, -size/2 + 8), QPointF(4, -size/2 + 8)])
        painter.drawPolygon([QPointF(0, size/2), QPointF(-4, size/2 - 8), QPointF(4, size/2 - 8)])
        
        painter.setBrush(Qt.white)
        painter.drawEllipse(4, -6, 8, 8) 
        painter.drawEllipse(4, 6, 8, 8)  
        
        painter.setBrush(Qt.black)
        dx = 2 if tiger.mouth_open else 0
        
        painter.drawEllipse(8 + dx, -6, 3, 3)
        painter.drawEllipse(8 + dx, 6, 3, 3)
        
        if tiger.mouth_open:
            painter.setBrush(QColor(150, 0, 0))
            painter.drawPie(QRectF(0, -6, 12, 12), -45 * 16, 90 * 16)

        painter.restore()

    def draw_enemy(self, painter, enemy):
        cx = enemy.x * CELL_SIZE + CELL_SIZE/2
        cy = enemy.y * CELL_SIZE + CELL_SIZE/2
        size = CELL_SIZE * 0.8
        
        color = QColor(100, 100, 255) if enemy.scared else enemy.color
        
        path = QPainterPath()
        path.moveTo(cx - size/2, cy)
        path.arcTo(QRectF(cx - size/2, cy - size/2, size, size), 180, 180)
        
        bottom = cy + size/2
        wave_height = 4 if (self.global_pulse * 5) % 2 > 1 else -4 
        
        path.lineTo(cx + size/2, bottom)
        path.lineTo(cx + size/4, bottom - 5)
        path.lineTo(cx, bottom)
        path.lineTo(cx - size/4, bottom - 5)
        path.lineTo(cx - size/2, bottom)
        path.closeSubpath()
        
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(), 2))
        painter.drawPath(path)
        
        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)
        eye_y = cy - 4
        painter.drawEllipse(QPointF(cx - 6, eye_y), 6, 8)
        painter.drawEllipse(QPointF(cx + 6, eye_y), 6, 8)
        
        painter.setBrush(QColor(0, 0, 50))
        if enemy.scared:
            painter.drawEllipse(QPointF(cx - 6 + random.randint(-1,1), eye_y), 2, 2)
            painter.drawEllipse(QPointF(cx + 6 + random.randint(-1,1), eye_y), 2, 2)
        else:
            look_x = 0
            look_y = 0
            if enemy.direction == 0: look_x = 2
            elif enemy.direction == 2: look_x = -2
            elif enemy.direction == 1: look_y = 2
            elif enemy.direction == 3: look_y = -2
            
            painter.drawEllipse(QPointF(cx - 6 + look_x, eye_y + look_y), 3, 3)
            painter.drawEllipse(QPointF(cx + 6 + look_x, eye_y + look_y), 3, 3)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Hungry - Jungle Adventure Premium")
        
        # --- MODIFIED: Added QMessageBox Styling ---
        self.setStyleSheet("""
            QMainWindow { background-color: #0f141e; }
            QLabel { color: white; font-family: 'Segoe UI', Arial; font-weight: bold; }
            
            /* Style khusus QMessageBox agar teks hitam dan background putih */
            QMessageBox { background-color: white; }
            QMessageBox QLabel { color: black; font-weight: normal; font-size: 14px; }
            QMessageBox QPushButton { color: white; background-color: #3498db; min-width: 60px; }

            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60; }
            QPushButton:pressed { background-color: #219150; }
            QPushButton#btn_restart { background-color: #e74c3c; }
            QPushButton#btn_restart:hover { background-color: #c0392b; }
            QPushButton#btn_quit { background-color: #7f8c8d; }
            QPushButton#btn_quit:hover { background-color: #2c3e50; }
            QPushButton#btn_save { background-color: #3498db; }
            QPushButton#btn_save:hover { background-color: #2980b9; }
            QPushButton#btn_load { background-color: #9b59b6; }
            QPushButton#btn_load:hover { background-color: #8e44ad; }
        """)

        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top HUD (Floating)
        hud_container = QWidget()
        hud_container.setFixedHeight(60)
        hud_container.setStyleSheet("background-color: rgba(0,0,0,150); border-bottom: 2px solid #34495e;")
        hud_layout = QHBoxLayout(hud_container)
        
        self.score_label = QLabel("SCORE: 0")
        self.score_label.setStyleSheet("font-size: 24px; color: #f1c40f;")
        
        self.lives_label = QLabel("LIVES: 3")
        self.lives_label.setStyleSheet("font-size: 24px; color: #e74c3c;")
        
        self.level_label = QLabel("LEVEL: 1")
        self.level_label.setStyleSheet("font-size: 24px; color: #3498db;")
        
        # --- HUD Buttons ---
        self.btn_save = QPushButton("SAVE")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        
        self.btn_load = QPushButton("LOAD")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setCursor(Qt.PointingHandCursor)
        
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setObjectName("btn_restart")
        self.btn_reset.setCursor(Qt.PointingHandCursor)

        self.btn_quit = QPushButton("QUIT")
        self.btn_quit.setObjectName("btn_quit")
        self.btn_quit.setCursor(Qt.PointingHandCursor)
        self.btn_quit.clicked.connect(self.close)

        hud_layout.addWidget(self.score_label)
        hud_layout.addSpacing(20)
        hud_layout.addWidget(self.lives_label)
        hud_layout.addSpacing(20)
        hud_layout.addWidget(self.level_label)
        hud_layout.addStretch()
        hud_layout.addWidget(self.btn_save)
        hud_layout.addWidget(self.btn_load)
        hud_layout.addWidget(self.btn_reset)
        hud_layout.addWidget(self.btn_quit)

        layout.addWidget(hud_container)
        
        # Game Area
        self.game = GameWidget(self)
        layout.addWidget(self.game)
        
        # Connect Signals
        self.game.score_updated.connect(self.update_score)
        self.game.lives_updated.connect(self.update_lives)
        self.game.level_updated.connect(self.update_level)
        self.game.msg_signal.connect(self.show_message)
        
        # Connect Buttons
        self.btn_save.clicked.connect(self.game.save_game)
        self.btn_load.clicked.connect(self.game.load_game)
        self.btn_reset.clicked.connect(self.game.reset_full_game)
        
        # Set Fullscreen
        self.showFullScreen()

    def update_score(self, score):
        self.score_label.setText(f"SCORE: {score}")

    def update_lives(self, lives):
        self.lives_label.setText(f"LIVES: {lives}")

    def update_level(self, level):
        self.level_label.setText(f"LEVEL: {level}")
    
    def show_message(self, title, msg):
        QMessageBox.information(self, title, msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() 
    sys.exit(app.exec())