from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent

class Level_2_Class(Screen):
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
        print("Entering level 2, press Q to exit")
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
        print("Leaving level 2 ")
        self.level_contents.cleanup()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None


class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=10, y=40, width=40, height=40)
        
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
            (0, 230, 2, 1),
            (600, 40, 1, 11),
            (640, 440, 1, 1),
            (680, 440, 1, 3),
            (560, 80, 1, 1),
            (400, 400, 3, 1),
            (260, 350, 1, 1),
            (160, 300, 1, 1),
            (600, 530, 12, 1),
            (770, 440, 10, 1),
            (1130, 530, 1, 1),
            (1170, 440, 1, 8),
            (690, 360, 5, 1),
            (770, 400, 3, 2),
            (640, 280, 3, 1),
            (770, 80, 1, 1),
            (890, 160, 1, 1),
            (890, 260, 1, 5),
            (1010, 120, 1, 1),
            (1130, 200, 1, 1),
            (930, 260, 2, 1),
            (1130, 320, 2, 1),
            (1290, 400, 2, 1),
            (1290, 560, 2, 1),
            (1290, 720, 2, 1),
            (1210, 480, 2, 1),
            (1210, 640, 2, 1),
            (1370, 40, 1, 21),
            (320, 760, 1, 1),
            (480, 720, 18, 1),
            (480, 720, 1, 2),
            (480, 850, 23, 1),
            (1610, 800, 1, 5),
            (1610, 680, 1, 1),
            (1410, 640, 5, 1),
            (1700, 720, 1, 1),
            (1800, 640, 1, 4),
            (1500, 510, 11, 1),
            (1370, 320, 12, 1),
            (1530, 360, 1, 2),
            (1670, 360, 1, 1),
            (1810, 360, 1, 2),
            (1530, 160, 8, 1),
            (1810, 200, 1, 3),
            (1530, 80, 1, 2),
            (1410, 80, 1, 1)
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
