from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.text import LabelBase
from kivy.core.window import Window

from level_1 import LevelContents, Level_1_Class
from level_2 import LevelContents, Level_2_Class
from level_3 import LevelContents, Level_3_Class
from level_class import SoundManager

# Set default font
LabelBase.register(name="Roboto", fn_regular="assets/fonts/EBGaramond-Regular.ttf"
                   , fn_italic="assets/fonts/EBGaramond-Italic.ttf")

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_game(self):
        print("Starting the game...")
        self.manager.current = 'level_selection'

    def show_how_to_play(self):
        print("Displaying How to Play...")
        app = App.get_running_app()
        app.previous_screen = self.manager.current  
        self.manager.current = 'guide'

    def open_settings(self):
        print("Opening Settings...")
        app = App.get_running_app()
        app.previous_screen = self.manager.current  
        self.manager.current = 'settings'

    def quit_game(self):
        App.get_running_app().stop()

class LevelSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def back(self):
        print("Back to main menu")
        self.manager.current = 'main_menu'

    def select_level(self, level_id):
        print(f"Select level {level_id}")
        match level_id:
            case 1:
                self.manager.current = 'level_1'
            case 2:
                self.manager.current = 'level_2'
            case 3:
                self.manager.current = 'level_3'
            case _:
                print("Invalid")

    def on_enter(self, *args):
        print(Window.size)

class GuideScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def back_to_previous(self):
        app = App.get_running_app()
        previous = getattr(app, 'previous_screen', 'main_menu')
        self.manager.current = previous

class SettingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_music_volume(self, instance, value):
        SoundManager.set_music_volume(value / 100)

    def set_sfx_volume(self, instance, value):
        SoundManager.set_sfx_volume(value / 100)

    # def toggle_fullscreen(self, instance):
    #     if instance.state == 'down':
    #         instance.text = "Windowed"
    #         Window.fullscreen = True
    #     else:
    #         instance.text = "Fullscreen"
    #         Window.fullscreen = False

    def back_to_previous(self):
        app = App.get_running_app()
        previous = getattr(app, 'previous_screen', 'main_menu')
        self.manager.current = previous

class PauseMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resume_game(self):
        app = App.get_running_app()
        if app.current_playing_screen:
            self.manager.current = app.current_playing_screen

    def go_to_guide(self):
        app = App.get_running_app()
        app.previous_screen = self.manager.current  # Lưu tên màn hình hiện tại ('pause_menu')
        self.manager.current = 'guide'

    def open_settings(self):
        app = App.get_running_app()
        app.previous_screen = self.manager.current  # Lưu là 'pause_menu'
        self.manager.current = 'settings'

    def back_to_menu(self):
        self.manager.current = 'main_menu'

    def quit_game(self):
        App.get_running_app().stop()

class ArtifactHunterApp(App):
    current_playing_screen = None

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        SoundManager.load()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(LevelSelectionScreen(name='level_selection'))
        sm.add_widget(GuideScreen(name='guide'))
        sm.add_widget(SettingScreen(name='settings'))
        sm.add_widget(PauseMenuScreen(name='pause_menu'))
        sm.add_widget(Level_1_Class(name='level_1'))
        sm.add_widget(Level_2_Class(name='level_2'))
        sm.add_widget(Level_3_Class(name='level_3'))
        return sm

    def on_key_down(self, window, key, *args):
        if key == 27:  # ESC
            current = self.root.current
            if current.startswith("level"):
                self.current_playing_screen = current
                self.root.current = 'pause_menu'
                return True


if __name__ == "__main__":
    print("-----------------------")
    Window.top = 25
    Window.left = 0
    ArtifactHunterApp().run()
