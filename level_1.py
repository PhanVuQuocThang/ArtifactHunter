from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from level_class import Player, Platform
from kivy.clock import Clock


class Level_1_Class(Screen):
    """
    All other Level_X_Class should follow this structure.
    When entering the game, this should be called and registered as a Screen for ScreenManager.
    Always override methods on_enter and on_leave of class Screen.
    Set frame rate (FPS) only in on_enter, not in __init__.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level_contents = LevelContents()
        self.add_widget(self.level_contents)
        self.update_event = None
    def on_enter(self, *args):
        # Overriding Kivy-defined on_enter
        print("Entering level 1, press Q to exit")
        # Frame rate: 60FPS
        self.update_event = Clock.schedule_interval(self.level_contents.update, 1/60)

    def on_leave(self, *args):
        # Overriding Kivy-defined on_leave
        print("Leaving level 1 ")
        self.level_contents.player.cleanup()
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None


class LevelContents(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=100, y=200, width=40, height=40)
        self.add_widget(self.player)
        self.platforms = []

        self.create_platform()

    def create_platform(self):
        # Create all platforms for this level
        ground = Platform(0, 0, Window.width, 40)
        self.platforms.append(ground)
        self.add_widget(ground)

        # Floating platforms
        platforms_data = [
            # (x, y, width, height)
            (200, 150, 200, 20),  # Light brown
            (500, 250, 150, 20),  # Green
            (100, 350, 120, 20),  # Red
            (350, 450, 180, 20),  # Blue
            (600, 380, 100, 20),  # Yellow
        ]

        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.platforms.append(platform)
            self.add_widget(platform)

    def check_collisions(self):
        """Check collisions between player and platforms.
        This will be refactored later to prevent constantly rewriting the same collision check."""
        player_rect = (
            self.player.pos[0],
            self.player.pos[1],
            self.player.size[0],
            self.player.size[1]
        )

        on_ground_temp = False
        epsilon = 2 # pixels. Allow slight overlap or near-platform alignment. Unused.

        for platform in self.platforms:
            platform_rect = (
                platform.pos[0],
                platform.pos[1],
                platform.size[0],
                platform.size[1]
            )

            # Standard Axis-Aligned Bounding Box (AABB) collision check
            if (player_rect[0] <= platform_rect[0] + platform_rect[2] and
                    player_rect[0] + player_rect[2] >= platform_rect[0] and
                    player_rect[1] <= platform_rect[1] + platform_rect[3] and
                    player_rect[1] + player_rect[3] >= platform_rect[1]):

                # Player is falling down onto platform
                if self.player.velocity.y <= 0:
                    # Place player on top of platform
                    self.player.pos = (
                        self.player.pos[0],
                        platform_rect[1] + platform_rect[3]
                    )
                    self.player.velocity.y = 0
                    on_ground_temp = True
                    break  # Stop checking other platforms
        self.player.on_ground = on_ground_temp


    def update(self, dt):
        """Main game update loop. This is called by Clock.schedule_interval.
        Follow: process input -> update -> check collision."""
        self.player.process_input()
        self.player.update(dt)
        self.check_collisions()

    def cleanup(self):
        """Clean up game resources"""
        if hasattr(self.player, 'cleanup'):
            self.player.cleanup()
