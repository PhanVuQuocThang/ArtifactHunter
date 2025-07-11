from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Rectangle, Color
from utils import resource_path
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent, PlaceHolder, DeathTrap, SoundManager


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
        # Đảm bảo không có câu đố nào đang hiển thị
        if hasattr(self, 'level_contents') and self.level_contents:
            self.level_contents.active_puzzle_popup = None  # Reset popup câu đố
            # Reset all puzzle states
            for puzzle in self.level_contents.puzzles:
                if hasattr(puzzle, 'show_prompt'):
                    puzzle.show_prompt = False
                if hasattr(puzzle, 'popup') and puzzle.popup:
                    puzzle.popup.dismiss()
                    puzzle.popup = None

        # Initialize level
        print("Entering level 1, press Q to exit")
        if not self.initialized:
            SoundManager.play_music("level_1")
            self.level_contents = LevelContents()
            self.add_widget(self.level_contents)
            self.initialized = True
        else:
            # Reset puzzle states when re-entering level
            if hasattr(self.level_contents, 'puzzles'):
                for puzzle in self.level_contents.puzzles:
                    if hasattr(puzzle, 'show_prompt'):
                        puzzle.show_prompt = False
                    if hasattr(puzzle, 'popup') and puzzle.popup:
                        puzzle.popup.dismiss()
                        puzzle.popup = None
            # Reset active puzzle popup
            if hasattr(self.level_contents, 'active_puzzle_popup'):
                self.level_contents.active_puzzle_popup = None

             # Restore keyboard input if re-entering
            self.level_contents.player.setup_keyboard()
        # Frame rate: 60FPS
        self.update_event = Clock.schedule_interval(self.level_contents.update, 1/60)
    
    # Overriding Kivy-defined on_leave
    def on_leave(self, *args):
        print("Leaving level 1 ")
        if hasattr(self, 'level_contents') and self.level_contents:
            
            if self.level_contents.active_puzzle_popup and hasattr(self.level_contents.active_puzzle_popup, 'popup'):
                self.level_contents.active_puzzle_popup.popup.dismiss()  # Đóng popup câu đố
                self.level_contents.active_puzzle_popup = None  # Reset popup

            self.level_contents.cleanup()
        SoundManager.stop_music()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None
    def reset_level(self):
        """Reset the level to its initial state"""
        if self.level_contents:
            self.remove_widget(self.level_contents)
        self.level_contents = None
        self.initialized = False
        self.on_enter()  # Re-initialize the level

class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=10, y=40, width=40, height=40)
        self.paused = False     # Flag to stop game
        self.active_puzzle_popup = None
        self.artifact = None
        
        # Lists for bullets, particles, enemies
        self.projectiles = []
        self.particles = []
        self.platforms = []
        self.enemies = []
        self.puzzles = []
        self.entities = []
        self.add_widget(self.player)

        self.entities.append(self.player)
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
            texture_path=resource_path('assets/sprites/PixelTexturePack/Textures/Rocks/GOLDROCKS.png')
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
                                texture_path=resource_path('assets/sprites/PixelTexturePack/Textures/Elements/SAND.png'))
            self.platforms.append(platform)
            self.add_widget(platform)

    def create_enemy(self):
        enemy_data = [
            (480, 520),
            (1200, 40),
            (640, 680),
            (1500, 40)
        ]

        for x, y in enemy_data:
            enemy = Enemy(x=x, y=y, width=40, height=40,
                          texture_path=resource_path('assets/sprites/Characters/Enemy.png'))
            self.enemies.append(enemy)
            self.entities.append(enemy)
            self.add_widget(enemy)

    def create_artifact(self):
        artifact_data = (700, 40)
        artifact = Artifact(name="sky rocket",x=artifact_data[0],y = artifact_data[1],  width=40, height=40,
                            texture_path=resource_path('assets/sprites/Artifacts/DOUBLE_JUMP.png'))
        # self.artifact = artifact
        self.platforms.append(artifact) # Workaround for collision checking
        self.add_widget(artifact)

    def create_puzzle(self):
        for puzzle in PuzzleComponent.get_puzzles_for_level(1):  
            puzzle.level_ref = self  # So puzzle can check enemies when failed
            self.puzzles.append(puzzle)
            self.add_widget(puzzle)


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
        # Update artifacts
        for artifact in self.platforms:
            if isinstance(artifact, Artifact):
                artifact.pick_up(self.player)
        # Update inventory effects
        self.player.apply_inventory_effects()

        # Update puzzle state; remove if solved
        for puzzle in self.puzzles[:]:
            if isinstance(puzzle, PlaceHolder):
                continue
            puzzle.update()
            if puzzle.solved:
                self.remove_widget(puzzle)
                self.puzzles.remove(puzzle)