from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock

from level_class import Player, Platform, BaseLevelContents,Artifact, Enemy


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


class LevelContents(BaseLevelContents):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(x=100, y=200, width=40, height=40)
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
        enemy = Enemy(x=500, y=200, width=40, height=40)
        self.add_widget(enemy)
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
