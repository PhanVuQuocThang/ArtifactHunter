from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

# Define the KV language string
KV = '''
<GameMenu>:
    # Background image
    Image:
        source: 'backgrounds.jpg'
        allow_stretch: True
        keep_ratio: False

    # Game title
    Label:
        text: 'MY GAME'
        font_size: '40dp'
        pos_hint: {'center_x': 0.5, 'top': 0.9}
        color: 1, 1, 1, 1
        bold: True

    # Menu buttons
    Button:
        text: 'Start'
        size_hint: None, None
        size: 200, 60
        pos_hint: {'center_x': 0.5, 'center_y': 0.65}
        background_color: 0.2, 0.6, 1, 0.8
        background_normal: ''
        font_size: '20dp'
        on_press: root.start_game()

    Button:
        text: 'How to Play'
        size_hint: None, None
        size: 200, 60
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        background_color: 0.2, 0.6, 1, 0.8
        background_normal: ''
        font_size: '20dp'
        on_press: root.show_how_to_play()

    Button:
        text: 'Settings'
        size_hint: None, None
        size: 200, 60
        pos_hint: {'center_x': 0.5, 'center_y': 0.35}
        background_color: 0.2, 0.6, 1, 0.8
        background_normal: ''
        font_size: '20dp'
        on_press: root.show_settings()

    Button:
        text: 'Quit'
        size_hint: None, None
        size: 200, 60
        pos_hint: {'center_x': 0.5, 'center_y': 0.2}
        background_color: 0.2, 0.6, 1, 0.8
        background_normal: ''
        font_size: '20dp'
        on_press: root.quit_game()

<HowToPlayPopup>:
    title: 'How to Play'
    size_hint: 0.8, 0.8
    auto_dismiss: False

    FloatLayout:
        Label:
            text: 'How to Play:\\n\\n1. Use arrow keys to move\\n2. Press space to jump\\n3. Press \\'E\\' to interact\\n4. Collect all items to win!'
            size_hint: 0.8, 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}

        Button:
            text: 'Close'
            size_hint: 0.5, 0.15
            pos_hint: {'center_x': 0.5, 'center_y': 0.15}
            on_press: root.dismiss()

<SettingsPopup>:
    title: 'Settings'
    size_hint: 0.8, 0.8
    auto_dismiss: False

    FloatLayout:
        Label:
            text: 'Volume:'
            size_hint: 0.3, 0.1
            pos_hint: {'x': 0.1, 'y': 0.7}

        Button:
            text: '-'
            size_hint: 0.1, 0.1
            pos_hint: {'x': 0.45, 'y': 0.7}

        Button:
            text: '+'
            size_hint: 0.1, 0.1
            pos_hint: {'x': 0.6, 'y': 0.7}

        Label:
            text: 'Fullscreen:'
            size_hint: 0.3, 0.1
            pos_hint: {'x': 0.1, 'y': 0.5}

        Button:
            text: 'Toggle'
            size_hint: 0.25, 0.1
            pos_hint: {'x': 0.45, 'y': 0.5}

        Button:
            text: 'Save & Close'
            size_hint: 0.5, 0.15
            pos_hint: {'center_x': 0.5, 'center_y': 0.15}
            on_press: root.dismiss()
'''


class HowToPlayPopup(Popup):
    pass


class SettingsPopup(Popup):
    pass


class GameMenu(FloatLayout):
    def start_game(self):
        print("Starting the game...")
        # Here you would transition to the game screen

    def show_how_to_play(self):
        popup = HowToPlayPopup()
        popup.open()

    def show_settings(self):
        popup = SettingsPopup()
        popup.open()

    def quit_game(self):
        App.get_running_app().stop()


class GameApp(App):
    def build(self):
        # Set window size - adjust as needed
        Window.size = (800, 600)

        # Load the KV string
        Builder.load_string(KV)

        return GameMenu()


if __name__ == '__main__':
    GameApp().run()