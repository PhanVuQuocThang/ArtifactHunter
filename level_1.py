from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent

class Level_1_Class(Screen):
    """
    All other Level_X_Class should follow this structure.
    When entering the game, this should be called and registered as a Screen for ScreenManager.
    Always override methods on_enter and on_leave of class Screen.
    Set frame rate (FPS) only in on_enter, not in __init__.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level_contents = None
        self.update_event = None
        self.initialized = False    # Flag to ensure the level is initialized only once

    # Overriding Kivy-defined on_enter
    def on_enter(self, *args):
        # Initialize level
        print("Entering level 1, press Q to exit")
        if not self.initialized:
            self.level_contents = LevelContents()
            self.add_widget(self.level_contents)
            self.initialized = True
        else:
             # Restore keyboard input if re-entering
            self.level_contents.player.setup_keyboard()
        # Frame rate: 60FPS
        self.update_event = Clock.schedule_interval(self.level_contents.update, 1/60)
    
    # Overriding Kivy-defined on_leave
    def on_leave(self, *args):
        print("Leaving level 1 ")

        if hasattr(self.level_contents, "player"):
            self.level_contents.player.cleanup()

        if self.update_event:
            self.update_event.cancel()
            self.update_event = None


class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paused = False     # Flag to stop game
        self.player = Player(x=100, y=200, width=40, height=40)
        
        # Lists for bullets, particles, enemies
        self.projectiles = []
        self.particles = []
        self.enemies = []

        self.player.inventory_add_item("H3nt4i")
        self.player.inventory_add_item("N1gg4")
        self.player.inventory_add_item("Chải mèo")
        self.add_widget(self.player)
        artifact = Artifact(
            name="Marioowo",
            description="Cho Khả năng nhảy đôi.",
            x=300, y=200 , width = 40, height = 40
        )
        self.add_widget(artifact)
        enemy = Enemy(x=500, y=220, width=40, height=40)
        self.add_widget(enemy)
        self.enemies.append(enemy) 
        self.platforms = []

        self.create_platform()

        # Setup puzzles
        self.puzzles = []
        # Add puzzles automaticly for level
        # Level 1: 1 question
        # If level  2/3:   PuzzleComponent.get_puzzles_for_level(2/3)
        for puzzle in PuzzleComponent.get_puzzles_for_level(1):  
            puzzle.level_ref = self  # So puzzle can check enemies when failed
            self.puzzles.append(puzzle)
            self.add_widget(puzzle)

    def create_platform(self):
        # Create all platforms for this level
        ground = Platform(0, 0, Window.width, 40)
        self.platforms.append(ground)
        self.add_widget(ground)

        # Floating platforms
        platforms_data = [
            # Bottom tier - easy jumps from ground (60-120 pixels high)
            (200, 100, 200, 20),  # Light brown
            (500, 200, 150, 20),  # Green
            (100, 300, 120, 20),  # Red
            (350, 400, 180, 20),  # Blue
            (600, 280, 100, 20),  # Yellow

            # Additional bottom tier platforms
            (50, 80, 100, 20),  # Starting area helper
            (750, 120, 120, 20),  # Right side low platform
            (450, 320, 80, 20),  # Small connector
            (150, 180, 90, 20),  # Mid-left connector

            # Middle tier - moderate difficulty (200-350 pixels high)
            (80, 220, 140, 20),  # Left side climb
            (300, 260, 100, 20),  # Central stepping stone
            (520, 340, 110, 20),  # Right side platform
            (180, 350, 80, 20),  # Narrow jump challenge
            (680, 240, 90, 20),  # Far right access
            (420, 280, 70, 20),  # Small connector platform
            (250, 320, 60, 20),  # Precision jump target
            (580, 200, 85, 20),  # Bridge platform

            # Upper tier - challenging (400-550 pixels high)
            (120, 480, 100, 20),  # Left tower top
            (350, 520, 90, 20),  # Central high platform
            (600, 460, 110, 20),  # Right side high
            (250, 440, 80, 20),  # Mid-air stepping stone
            (480, 500, 70, 20),  # Narrow high platform
            (50, 420, 75, 20),  # Far left challenge
            (700, 380, 95, 20),  # Right side upper
            (320, 480, 60, 20),  # Small precision platform

            # Top tier - expert level (600+ pixels high)
            (200, 620, 120, 20),  # High central platform
            (450, 680, 100, 20),  # Very high right
            (80, 600, 90, 20),  # Left side peak
            (550, 640, 80, 20),  # Right peak approach
            (300, 720, 70, 20),  # Highest challenge platform
            (650, 580, 85, 20),  # Far right high
            (150, 660, 60, 20),  # Narrow high target

            # Connector platforms for complex routes
            (400, 360, 50, 20),  # Tiny connector
            (280, 380, 45, 20),  # Micro platform
            (520, 420, 55, 20),  # Small link
            (180, 540, 65, 20),  # Upper connector
            (480, 580, 50, 20),  # High connector
            (350, 600, 40, 20),  # Precision connector

            # Secret/bonus area platforms
            (750, 500, 100, 20),  # Hidden right side
            (20, 300, 60, 20),  # Secret left alcove
            (720, 320, 80, 20),  # Bonus right platform
            (40, 520, 70, 20),  # Secret upper left
            (680, 600, 90, 20),  # Hidden upper right

            # Moving/dynamic platform positions (static for now)
            (400, 180, 60, 20),  # Lower moving platform pos
            (300, 400, 55, 20),  # Mid moving platform pos
            (500, 560, 65, 20),  # Upper moving platform pos
        ]

        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.platforms.append(platform)
            self.add_widget(platform)
    
    def update(self, dt):
        if self.paused:  # if pause → no process
            return
        # Process keyboard input for movement
        self.player.process_input()

        # update proj
        for proj in self.projectiles:
            proj.update(dt, self)

        # update enemy
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.platforms, self)

        # Physics and collision checks
        self.check_collisions()
        self.player.update(dt)

        # Update puzzle state; remove if solved
        for puzzle in self.puzzles[:]:
            puzzle.update()
            if puzzle.solved:
                self.remove_widget(puzzle)
                self.puzzles.remove(puzzle)
