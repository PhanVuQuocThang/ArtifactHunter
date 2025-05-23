from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.text import LabelBase
from kivy.clock import Clock

from level_1 import LevelContents, Level_1_Class

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

    def open_settings(self):
        print("Opening Settings...")

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
                # See documentation in Level_1_Class
                self.manager.current = 'level_1'
            case 2:
                pass
            case 3:
                pass
            case _:
                print("Invalid")


class GuideScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ArtifactHunterApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(LevelSelectionScreen(name='level_selection'))
        sm.add_widget(Level_1_Class(name='level_1'))
        return sm

if __name__ == "__main__":
    print("-----------------------")
    ArtifactHunterApp().run()
