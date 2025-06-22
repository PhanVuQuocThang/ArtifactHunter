from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent, PlaceHolder, DeathTrap

class Level_3_Class(Screen):
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
        # Set background color or image
        with self.canvas.before:
            self.bg_rect = Rectangle(source='assets/backgrounds/level_3.jpg',
                                     size=self.size, pos=self.pos)

        # Bind to update background when screen size changes
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Initialize level
        print("Entering level 3, press Q to exit")
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
        print("Leaving level 3 ")
        self.level_contents.cleanup()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def update_bg(self, instance, value):
        """Update background rectangle when screen size changes"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=1500, y=640, width=40, height=40)
        self.paused = False     # Flag to stop game
        self.active_puzzle_popup = None
        
        # Lists for bullets, particles, enemies
        self.projectiles = []
        self.particles = []
        self.platforms = []
        self.enemies = []
        self.puzzles = []
        self.artifact = None
        self.add_widget(self.player)

        self.create_platform()
        self.create_puzzle()
        self.create_enemy()
        self.create_artifact()

    def create_platform(self):
        # Create all platforms for this level
        ground = Platform(
            x=0, y=0,
            num_tiles_x=100,
            num_tiles_y=1,
            texture_path='assets/sprites/PixelTexturePack/Textures/Tech/HIGHTECHWALL.png'
        )
        self.platforms.append(ground)
        self.add_widget(ground)

        # Floating platforms
        platforms_data = [
            (60, 80, 15, 1),
            (120, 160, 2, 1),
            (240, 240, 2, 1),
            (480, 300, 2, 1),
            (240, 360, 2, 1),
            (360, 480, 8, 1),
            (120, 420, 1, 1),

            (660, 80, 1, 11),
            (780, 40, 1, 5),
            (780, 320, 1, 8),
            (900, 80, 1, 11),
            (0, 600, 20, 1),

            (1020, 80, 2, 1),
            (1140, 160, 2, 1),
            (900, 240, 3, 1),
            (1140, 360, 2, 1),
            (900, 280, 2, 1),
            (1060 - 120, 440, 1, 1),

            (1220, 40, 1, 15),
            (1220, 120 + 40 * 15, 1, 10),
            (820, 560, 1, 1),
            (780, 760, 1, 4),

            (120, 760 - 80, 2, 1),
            (240, 840 - 80, 2, 1),
            (120, 800, 1, 1),
            (240, 960 - 80, 10, 1),

            (780, 720, 8, 1),
            (900, 880, 1, 4),
            (1060, 760, 1, 5),
            (1020, 800, 1, 1),
            (940, 880, 1, 1),

            (1260, 600, 10, 1),
            (1620, 80, 1, 21),
            (1580, 680, 1, 1),
            (1380, 760, 1, 1),
            (1260, 840, 1, 1),
            (1420, 880, 1, 1),

            (1580, 80, 1, 1),
            (1380, 160, 1, 1),
            (1260, 240, 1, 1),
            (1420, 320, 1, 1),
            (1580, 400, 1, 1),
            (1260, 480, 5, 1),
            (1420, 420, 1, 2)
        ]

        death_trap_data = [
            (200, 120, 12, 1),
            (660, 40, 3, 1),
            (820, 40, 1, 1),
            (1020, 40, 2, 1),
            (860, 760, 1, 1),
            (1470, 640, 1, 1),
            (1270, 40, 6, 1),

        ]

        for x, y, num_tiles_x, num_tiles_y, in death_trap_data:
            death_trap = DeathTrap(x, y, num_tiles_x, num_tiles_y,
                                texture_path='assets/sprites/tech_laser.png')
            self.platforms.append(death_trap)
            self.add_widget(death_trap)

        for x, y, num_tiles_x, num_tiles_y in platforms_data:
            platform = Platform(x, y, num_tiles_x, num_tiles_y,
                                texture_path='assets/sprites/PixelTexturePack/Textures/Tech/BIGSQUARES.png')
            self.platforms.append(platform)
            self.add_widget(platform)

    def create_enemy(self):
        enemy_data = [
            (160, 40),
            (520, 340),
            (1180, 40),
            (1060, 120),
            (980, 280),
            (1180, 400),
            (570, 640),
            (430, 640),
            (210, 640),
            (1020, 760),
            (1580, 640),
            (1580, 720),
            (1260, 880),
            (1615, 40),
            (1880, 40)
        ]

        for position in enemy_data:
            enemy = PlaceHolder(position=position, color=(1, 0, 0),texture_path='assets/sprites/Characters/ENEMY.png')
            self.enemies.append(enemy)
            self.add_widget(enemy)

    def create_artifact(self):
        artifact_data = (40, 40)
        artifact = PlaceHolder(position=artifact_data, color=(1, 1, 0),texture_path='assets/sprites/Artifacts/DMG.png')
        self.artifact = artifact
        self.add_widget(artifact)

    def create_puzzle(self):
        pass

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
            if isinstance(enemy, PlaceHolder):
                continue
            enemy.update(dt, self.player, self.platforms, self)

        # Physics and collision checks
        self.check_collisions()
        self.player.update(dt)

        # Update puzzle state; remove if solved
        for puzzle in self.puzzles[:]:
            if isinstance(puzzle, PlaceHolder):
                continue
            puzzle.update()
            if puzzle.solved:
                self.remove_widget(puzzle)
                self.puzzles.remove(puzzle)
