from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.app import App
from utils import resource_path

from level_class import Player, Platform, BaseLevelContents, Artifact, Enemy, PuzzleComponent, PlaceHolder, DeathTrap, \
    LevelExit


class Level_Custom_Class(Screen):
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
            self.bg_rect = Rectangle(source=resource_path('assets/backgrounds/level_3.jpg'),
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
        if hasattr(self, 'level_contents') and self.level_contents:
            self.level_contents.cleanup()
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


    def update_bg(self, instance, value):
        """Update background rectangle when screen size changes"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.data : dict = app.custom_level_data
        if self.data.get('spawn_point'):
            x, y = self.data['spawn_point'][0]
        else:
            x, y = 1, 1
        self.player = Player(x=x, y=y, width=40, height=40)
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
        self.create_enemy()
        self.create_artifact()
        self.create_exit()

    def create_platform(self, platforms_data=(), death_trap_data=()):
        death_trap_data = self.data.get('death_trap')
        if death_trap_data:
            for x, y, num_tiles_x, num_tiles_y, in death_trap_data:
                death_trap = DeathTrap(x, y, num_tiles_x, num_tiles_y,
                                    texture_path=resource_path('assets/sprites/tech_laser.png'))
                self.platforms.append(death_trap)
                self.add_widget(death_trap)
        platforms_data = self.data.get('platform')
        if platforms_data:
            for x, y, num_tiles_x, num_tiles_y in platforms_data:
                platform = Platform(x, y, num_tiles_x, num_tiles_y,
                                    texture_path=resource_path('assets/sprites/PixelTexturePack/Textures/Tech/BIGSQUARES.png'))
                self.platforms.append(platform)
                self.add_widget(platform)

    def create_enemy(self, enemy_data=()):
        enemy_data = self.data.get('enemy')
        if enemy_data:
            for x,y in enemy_data:
                enemy = Enemy(x=x, y=y, width=40, height=40, texture_path=resource_path('assets/sprites/Characters/Enemy.png'))
                self.enemies.append(enemy)
                self.add_widget(enemy)

    def create_artifact(self, artifact_data=()):
        artifact_data = self.data.get('artifact')
        if artifact_data:
            for x, y in artifact_data:
                artifact = Artifact(name="Acient Shotgun",
                                    x=x, y=y,
                                    width=40, height=40,texture_path=resource_path('assets/sprites/Artifacts/DMG.png'))
                self.artifact = artifact
                self.platforms.append(artifact)
                self.add_widget(artifact)

    def create_exit(self):
        exit_data = self.data.get('exit')
        if exit_data:
            for x, y in exit_data:
                exit = LevelExit(x=x, y=y)
                self.platforms.append(exit)
                self.add_widget(exit)

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

