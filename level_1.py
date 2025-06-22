from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent, PlaceHolder, DeathTrap


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
        self.level_contents.cleanup()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None


class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=10, y=40, width=40, height=40)
        self.paused = False     # Flag to stop game
        self.active_puzzle_popup = None
        
        # Lists for bullets, particles, enemies
        self.projectiles = []
        self.particles = []
        self.platforms = []
        self.enemies = []
        self.puzzles = []
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
            texture_path='assets/sprites/PixelTexturePack/Textures/Rocks/GOLDROCKS.png'
        )
        self.platforms.append(ground)
        self.add_widget(ground)

        # Floating platforms
        platforms_data = [
            (160, 80, 2, 1),
            (440, 80 * 2, 2, 1),
            (160, 80 * 3, 2, 1),
            (440, 80 * 4, 2, 1),
            (160, 80 * 5, 2, 1),
            (440, 80 * 6, 2, 1),

            (560, 40, 1, 14),
            (640, 120, 1, 14),

            (160 + 600, 80, 2, 1),
            (440 + 600, 80 * 2, 2, 1),
            (160 + 600, 80 * 3, 2, 1),
            (440 + 600, 80 * 4, 2, 1),
            (160 + 600, 80 * 5, 2, 1),
            (440 + 600, 80 * 6, 2, 1),
            (160 + 600, 80 * 7, 2, 1),

            (0, 120 + 40 * 14, 16, 1),

            (160, 760, 2, 1),
            (440, 840, 2, 1),
            (440 + 320, 840, 2, 1),
            (440 + 320 * 2, 840, 2, 1),

            (440 + 400 * 2, 40, 1, 22)
        ]

        for x, y, num_tiles_x, num_tiles_y in platforms_data:
            platform = Platform(x, y, num_tiles_x, num_tiles_y,
                                texture_path='assets/sprites/PixelTexturePack/Textures/Elements/SAND.png')
            self.platforms.append(platform)
            self.add_widget(platform)

    def create_enemy(self):
        enemy_data = [
            (480, 520),
            (1200, 40),
            (640, 680),
            (1500, 40)
        ]

        for position in enemy_data:
            enemy = PlaceHolder(position=position, color=(1, 0, 0))
            self.enemies.append(enemy)
            self.add_widget(enemy)

    def create_artifact(self):
        artifact_data = (1800, 40)
        artifact = PlaceHolder(position=artifact_data, color=(1, 1, 0))
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
