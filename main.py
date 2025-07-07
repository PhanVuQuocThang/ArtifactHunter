import os
from utils import resource_path
from kivy.resources import resource_add_path

APP_DIR = os.path.dirname(os.path.abspath(__file__))
resource_add_path(APP_DIR)


from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.clock import Clock

from level_1 import LevelContents, Level_1_Class
from level_2 import LevelContents, Level_2_Class
from level_3 import LevelContents, Level_3_Class
from level_class import SoundManager

# # Set default font
# LabelBase.register(name="Roboto", fn_regular=resource_path("assets/fonts/EBGaramond-Regular.ttf")
#                    , fn_italic=resource_path("assets/fonts/EBGaramond-Italic.ttf"))


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

    def back_to_menu(self):
        app = App.get_running_app()

        # Đảm bảo popup câu đố bị ẩn khi quay lại menu
        if hasattr(app.root, 'get_screen'):
            # Lấy màn hình hiện tại
            current_screen = app.root.get_screen(app.current_playing_screen)
            
            # Kiểm tra nếu màn hình hiện tại có chứa câu đố
            if hasattr(current_screen, 'level_contents') and current_screen.level_contents.active_puzzle_popup:
                current_screen.level_contents.active_puzzle_popup.dismiss()  # Đóng popup câu đố
                current_screen.level_contents.active_puzzle_popup = None  # Reset popup
        app.root.current = 'main_menu'

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
        app.root.current = previous

        # If return level, open popup pause
        if previous.startswith('level'):
            app.is_paused = True
            if hasattr(app.root.get_screen(previous), 'level_contents'):
                app.root.get_screen(previous).level_contents.paused = True
            popup = Factory.PausePopup()
            popup.open()

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
        app.root.current = previous

        # If return level, open popup pause
        if previous.startswith('level'):
            app.is_paused = True
            if hasattr(app.root.get_screen(previous), 'level_contents'):
                app.root.get_screen(previous).level_contents.paused = True
            popup = Factory.PausePopup()
            popup.open()

class PausePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resume_game(self):
        app = App.get_running_app()
        app.is_paused = False
        # Resume logic: reset pause flag trong LevelContents
        if hasattr(app.root.get_screen(app.current_playing_screen), 'level_contents'):
            app.root.get_screen(app.current_playing_screen).level_contents.paused = False
        self.dismiss()

    def go_to_guide(self):
        app = App.get_running_app()
        screen = app.root.get_screen(app.current_playing_screen)
        if hasattr(screen, 'level_contents'):
            puzzle = getattr(screen.level_contents, 'active_puzzle_popup', None)
            if puzzle and getattr(puzzle, 'popup', None):
                puzzle.popup.dismiss()
                puzzle.show_prompt = False
        app.previous_screen = app.current_playing_screen
        self.dismiss()
        app.root.current = 'guide'

    def open_settings(self):
        app = App.get_running_app()
        screen = app.root.get_screen(app.current_playing_screen)
        if hasattr(screen, 'level_contents'):
            puzzle = getattr(screen.level_contents, 'active_puzzle_popup', None)
            if puzzle and getattr(puzzle, 'popup', None):
                puzzle.popup.dismiss()
                puzzle.show_prompt = False
        app.previous_screen = app.current_playing_screen
        self.dismiss()
        app.root.current = 'settings'

    def back_to_menu(self):
        app = App.get_running_app()
        app.is_paused = False
        # Get current screen and reset puzzle states
        screen = app.root.get_screen(app.current_playing_screen)
        if hasattr(screen, 'level_contents') and screen.level_contents:
            screen.level_contents.paused = False
            # Reset all puzzle states
            for puzzle in screen.level_contents.puzzles:
                if hasattr(puzzle, 'show_prompt'):
                    puzzle.show_prompt = False
                if hasattr(puzzle, 'popup') and puzzle.popup:
                    puzzle.popup.dismiss()
                    puzzle.popup = None
            # Reset active puzzle popup
            screen.level_contents.active_puzzle_popup = None        
        self.dismiss()
        app.root.current = 'main_menu'

    def quit_game(self):
        App.get_running_app().stop()

class GameOverPopup(Popup):
    def retry_level(self, instance):
        app = App.get_running_app()
        screen_name = app.current_playing_screen
        screen = app.root.get_screen(screen_name)
        if hasattr(screen, 'reset_level'):
            screen.reset_level()
        # Reset game state
        app.is_paused = False
        self.dismiss()
        
        # Switch back to the level
        app.root.current = screen_name

    def quit_to_menu(self, instance):
        app = App.get_running_app()
        
        # Reset game state
        app.is_paused = False
        
        # Get the current level screen and clean up
        screen_name = app.current_playing_screen
        screen = app.root.get_screen(screen_name)
        if hasattr(screen, 'on_leave'):
            screen.on_leave()  # Clean up level resources
        
        # Reset the puzzle used questions when going back to menu
        if hasattr(screen, 'level_contents') and screen.level_contents:
            # Reset puzzle states
            for puzzle in screen.level_contents.puzzles:
                if hasattr(puzzle, 'show_prompt'):
                    puzzle.show_prompt = False
                if hasattr(puzzle, 'popup') and puzzle.popup:
                    puzzle.popup.dismiss()
                    puzzle.popup = None
            screen.level_contents.active_puzzle_popup = None
            
        # Reset the screen completely
        screen.clear_widgets()
        screen.initialized = False
        screen.level_contents = None
        # Go back to main menu
        app.root.current = 'main_menu'
        self.dismiss()

Factory.register('GameOverPopup', cls=GameOverPopup)
Factory.register('PausePopup', cls=PausePopup)

class ArtifactHunterApp(App):
    current_playing_screen = None
    is_paused = False  # NEW: Pause state flag

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        SoundManager.load()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(LevelSelectionScreen(name='level_selection'))
        sm.add_widget(GuideScreen(name='guide'))
        sm.add_widget(SettingScreen(name='settings'))
        sm.add_widget(Level_1_Class(name='level_1'))
        sm.add_widget(Level_2_Class(name='level_2'))
        sm.add_widget(Level_3_Class(name='level_3'))
        return sm

    def on_key_down(self, window, key, *args):
        if key == 27:  # ESC
            current = self.root.current
            if self.is_paused:
                for w in Window.children:
                    if isinstance(w, Factory.PausePopup):
                        w.dismiss()
                        self.is_paused = False
                        # Resume: turn off pause in LevelContents
                        if hasattr(self.root.get_screen(current), 'level_contents'):
                            self.root.get_screen(current).level_contents.paused = False
                        break
            else:
                if current.startswith("level"):
                    self.current_playing_screen = current
                    self.is_paused = True
                    # Pause:turn on pause in LevelContents
                    if hasattr(self.root.get_screen(current), 'level_contents'):
                        self.root.get_screen(current).level_contents.paused = True
                    popup = Factory.PausePopup()
                    popup.open()
            return True

if __name__ == "__main__":
    print("-----------------------")
    Window.top = 25
    Window.left = 0
    ArtifactHunterApp().run()
