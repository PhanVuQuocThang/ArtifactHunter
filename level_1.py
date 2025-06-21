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
        self.level_contents.cleanup()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None


class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=0, y=40, width=40, height=40)
        
        # Lists for bullets, particles, enemies
        self.projectiles = []
        self.particles = []
        self.platforms = []
        self.enemies = []
        self.puzzles = []

        self.player.inventory_add_item("H3nt4i")
        self.player.inventory_add_item("N1gg4")
        self.player.inventory_add_item("Chải mèo")
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
            (60, 150, 10, 1),
            (60, 40, 1, 1),
            (600, 40, 1, 10),
            (560, 80, 1, 1),
            (560, 210, 1, 1),
            (460, 260, 3, 1)
        ]

        for x, y, num_tiles_x, num_tiles_y in platforms_data:
            platform = Platform(x, y, num_tiles_x, num_tiles_y,
                                texture_path='assets/sprites/PixelTexturePack/Textures/Tech/BIGSQUARES.png')
            self.platforms.append(platform)
            self.add_widget(platform)

    def create_enemy(self):
        pass

    def create_artifact(self):
        pass

    def create_puzzle(self):
        pass

    def update(self, dt):
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
