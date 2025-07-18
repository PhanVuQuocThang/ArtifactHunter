import os
import ast

from utils import resource_path
from kivy.resources import resource_add_path

APP_DIR = os.path.dirname(os.path.abspath(__file__))
resource_add_path(APP_DIR)


from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.properties import StringProperty

from level_1 import Level_1_Class
from level_2 import Level_2_Class
from level_3 import Level_3_Class
from level_custom import Level_Custom_Class
from level_custom import LevelContents as Custom_LevelContents
from level_class import SoundManager, DeathTrap, Platform, Enemy, Artifact, Player, LevelExit


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
        SoundManager.stop_music()
        app.root.current = 'main_menu'

    def quit_game(self):
        App.get_running_app().stop()


class LevelSelectionScreen(Screen):
    custom_level_status = StringProperty("No custom.txt found")  # Use Kivy property
    categories = {'platform', 'death_trap', 'enemy', 'artifact', 'spawn_point', 'exit'}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_level_data = None
        self.check_custom_level()

    def back(self):
        print("Back to main menu")
        self.manager.current = 'main_menu'

    def select_level(self, level_id):
        print(f"Select level {level_id}")
        match level_id:
            case 1:
                self.manager.current = 'level_1'
                SoundManager.play_music("level_1")
            case 2:
                self.manager.current = 'level_2' 
                SoundManager.play_music("level_2") 
            case 3:
                self.manager.current = 'level_3'
                SoundManager.play_music("level_3")
            case 4:
                # Handle custom level
                print(self.custom_level_data)
                if self.custom_level_data is not None:
                    # Custom level exists, proceed to load it
                    print("Loading custom level...")
                    self.manager.current = 'level_custom'
                else:
                    # No custom level found
                    print("No custom level available")
            case _:
                print("Invalid")

    def on_enter(self, *args):
        print(Window.size)
        self.check_custom_level()

    def check_custom_level(self):
        """Check if custom.txt exists and load its contents"""
        try:
            app = App.get_running_app()
            if os.path.exists("custom.txt"):
                with open("custom.txt", "r", encoding="utf-8") as file:
                    self.custom_level_data = self.parse_level_data(file.read())
                    if self.try_load(self.custom_level_data):
                        app.custom_level_data = self.custom_level_data
                        self.custom_level_status = "Level loaded"
                    else:
                        self.custom_level_data = None
                        self.custom_level_status = "Incorrect data format"
                print("Custom level loaded successfully")
            else:
                self.custom_level_data = None
                self.custom_level_status = "No custom.txt found"
                print("No custom.txt file found")
        except Exception as e:
            self.custom_level_data = None
            self.custom_level_status = str(e)
            print(f"Error loading custom level: {e}")

    def parse_level_data(self, content: str):
        """Parse the raw data from file into categories for easier processing"""
        result = {}
        current_categ = None
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                current_categ = line.split(':')[0].strip()
                if current_categ in self.categories:
                    result[current_categ] = []
                else:
                    raise ValueError(f"Category \'{current_categ}\' not found")
            elif '(' in line:
                print(line)
                line = f"[{line}]" # Enclose line with [] to make it a list
                parsed = ast.literal_eval(line)
                result[current_categ].extend(parsed)
            else:
                continue
        return result

    def try_load(self, data: dict):
        """Try to load the parsed data to see if it was formatted correctly"""
        try:
            if data.get('spawn_point'):
                player_data = data['spawn_point']
                x, y = player_data[0]
                Player(x=x, y=y, width=40, height=40)
            if data.get('death_trap'):
                death_trap_data = data['death_trap']
                for x, y, num_tiles_x, num_tiles_y, in death_trap_data:
                    death_trap = DeathTrap(x, y, num_tiles_x, num_tiles_y,
                                           texture_path=resource_path('assets/sprites/tech_laser.png'))
            if data.get('platform'):
                platforms_data = data['platform']
                for x, y, num_tiles_x, num_tiles_y in platforms_data:
                    platform = Platform(x, y, num_tiles_x, num_tiles_y,
                                        texture_path=resource_path(
                                            'assets/sprites/PixelTexturePack/Textures/Tech/BIGSQUARES.png'))
            if data.get('enemy'):
                enemy_data = data['enemy']
                for x, y in enemy_data:
                    enemy = Enemy(x=x, y=y, width=40, height=40,
                                  texture_path=resource_path('assets/sprites/Characters/Enemy.png'))
            if data.get('artifact'):
                artifact_data = data['artifact']
                for x, y in artifact_data:
                    artifact = Artifact(name="Custom", x=x, y=y)
            if data.get('exit'):
                exit_data = data['exit']
                for x, y in exit_data:
                    exit = LevelExit(x=x, y=y)

        except Exception as e:
            return False
        return True


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
        SoundManager.play_music(app.current_playing_screen)
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
        SoundManager.stop_music()

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
        SoundManager.stop_music()

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
        SoundManager.stop_music()   
        self.dismiss()
        app.root.current = 'main_menu'

    def quit_game(self):
        App.get_running_app().stop()

class GameOverPopup(Popup):
    def retry_level(self, instance):
        app = App.get_running_app()
        screen_name = app.current_playing_screen
        screen = app.root.get_screen(screen_name)
        if hasattr(screen, 'level_contents'):
            for puzzle in getattr(screen.level_contents, 'puzzles', []):
                if hasattr(puzzle, 'reset_puzzle'):
                    puzzle.reset_puzzle()
            
            screen.remove_widget(screen.level_contents)
            screen.level_contents = None
        
        screen.initialized = False
        screen.on_enter()
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
            if hasattr(screen.level_contents, 'active_puzzle_popup'):
                if screen.level_contents.active_puzzle_popup:
                    if hasattr(screen.level_contents.active_puzzle_popup, 'popup'):
                        if screen.level_contents.active_puzzle_popup.popup:
                            screen.level_contents.active_puzzle_popup.popup.dismiss()
                    screen.level_contents.active_puzzle_popup = None
            # Reset puzzle
            for puzzle in getattr(screen.level_contents, 'puzzles', []):
                if hasattr(puzzle, 'reset_puzzle'): 
                    puzzle.reset_puzzle()
            
        # Reset the screen completely
        screen.clear_widgets()
        screen.initialized = False
        screen.level_contents = None
        # Go back to main menu
        app.root.current = 'main_menu'
        self.dismiss()
        app.is_paused = False
        # clean music
        SoundManager.stop_music()

Factory.register('GameOverPopup', cls=GameOverPopup)
Factory.register('PausePopup', cls=PausePopup)

class ArtifactHunterApp(App):
    current_playing_screen = None
    is_paused = False  # NEW: Pause state flag
    custom_level_data = None

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
        sm.add_widget(Level_Custom_Class(name='level_custom'))
        return sm

    def on_key_down(self, window, key, *args):
        if key == 27:  # ESC
            current = self.root.current
            if self.is_paused:
                SoundManager.play_music(current)
                for w in Window.children:
                    if isinstance(w, Factory.PausePopup):
                        w.dismiss()
                        self.is_paused = False
                        # Resume: turn off pause in LevelContents
                        if hasattr(self.root.get_screen(current), 'level_contents'):
                            self.root.get_screen(current).level_contents.paused = False
                        break
            else:
                SoundManager.stop_music()
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
