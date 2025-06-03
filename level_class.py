from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.lang import Builder


class Artifact:
    def __init__(self):
        pass

class Platform(Widget):
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(**kwargs)
        self.pos = (x, y)
        self.size = (width, height)

        # Draw the platform as a brown rectangle
        with self.canvas:
            Color(0.6, 0.4, 0.2)  # Brown color
            self.rect = Rectangle(pos=self.pos, size=self.size)


class Entity(Widget):
    """
    This is still a WIP. Please read the comments of each attribute for details.
    """
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(**kwargs)
        self.pos = (x, y) # Position of bottom-left corner of the Entity rectangle.
        self.size = (width, height) # Width and height from the bottom-left corner. Should be positive.
        self.velocity = Vector(0, 0)
        self.on_ground = False # Prevent double jumping, do falling check, etc...
        self.gravity = -800 # pixels/second
        self.move_speed = 300 # pixels/second
        self.jump_speed = 400 # pixels/second
        # Unimplemented
        self.max_health = 100
        self.current_health = 100
        self.weapon = None
        self.damage = 0
        self.name = ""

    def update_graphic(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update(self, dt):
        """
        dt is delta time
        Without dt, movement would depend on frame rate. At 60 FPS you'd move 60 times per second,
        at 30 FPS only 30 times. Multiplying by dt makes movement consistent regardless of
        frame rate - the entity always moves the same distance per second.
        """
        if not self.on_ground:
            self.velocity.y += self.gravity * dt

        # Update position based on velocity
        self.pos = (
            self.pos[0] + self.velocity.x * dt,
            self.pos[1] + self.velocity.y * dt
        )

        # Keep entity within screen bounds (horizontal)
        if self.pos[0] < 0:
            self.pos = (0, self.pos[1])
        elif self.pos[0] > Window.width - self.size[0]:
            self.pos = (Window.width - self.size[0], self.pos[1])

        # Don't let entity fall below screen
        if self.pos[1] < 0:
            self.pos = (self.pos[0], 0)
            self.velocity.y = 0
            self.on_ground = True

        # May add a check for jumping above screen

    # These functions only change velocity, not position
    def jump(self):
        if self.on_ground:
            self.velocity.y = self.jump_speed
        self.on_ground = False
    def move_left(self):
        self.velocity.x = -self.move_speed

    def move_right(self):
        self.velocity.x = self.move_speed

    def stop_horizontal_movement(self):
        self.velocity.x = 0

class Player(Entity):
    def __init__(self, x=0, y=0, width=100, height=100, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.inventory = [] # Need to also handle inventory input
        self.inventory_popup = None # Inventory object

        # Input handling
        self.keys_pressed = set()
        self._keyboard = None

        # Draw the player as a blue rectangle
        with self.canvas:
            Color(0, 0, 1)  # Blue color
            self.rect = Rectangle(pos=self.pos, size=self.size)

        # Bind position changes to update the rectangle
        self.bind(pos=self.update_graphics, size=self.update_graphics)

        # Set up keyboard input
        self.setup_keyboard()

    def setup_keyboard(self):
        """Initialize keyboard input handling"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        """Clean up keyboard when it's closed"""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard.unbind(on_key_up=self._on_keyboard_up)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle key press events"""
        key = keycode[1]
        self.keys_pressed.add(key)

    def _on_keyboard_up(self, keyboard, keycode):
        """Handle key release events"""
        key = keycode[1]
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def update_graphics(self, *args):
        """Update the visual representation"""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def cleanup(self):
        """Clean up resources when player is destroyed"""
        self._keyboard_closed()

    def toggle_inventory(self, pressed_key: str='b'):
        """Open the inventory popup. If the popup is already opened, close the popup."""
        self.keys_pressed.remove(pressed_key)
        if self.inventory_popup and self.inventory_popup._window:
            self.inventory_popup.dismiss()
            self.inventory_popup = None
        else:
            self.inventory_popup = PlayerInventory(self.inventory)
            self.inventory_popup.bind(on_dismiss=self.inventory_close)
            self.inventory_popup.open()

    def inventory_close(self, *args):
        self.inventory_popup = None

    def inventory_add_item(self, item):
        self.inventory.append(item)

    def inventory_remove_item(self, item):
        self.inventory.remove(item)

    def process_input(self):
        """Process continuous key presses (called every frame)"""
        # Temporary solution to exit level. This will change.
        if 'q' in self.keys_pressed:
            # Switch to screen 'level_selection'
            # self.parent.parent.manager means it's trying to access attribute manager of
            # the class that is 2 levels above itself, which should be class Screen.
            # Note that this is NOT related to inheritance (which uses super(), not .parent)
            # self.parent -> LevelContents, self.parent.parent -> Level_1_Class
            self.parent.parent.manager.current = 'level_selection'
        # Handle jump
        if 'spacebar' in self.keys_pressed:
            self.jump()
        # Handle open inventory
        if 'b' in self.keys_pressed:
            self.toggle_inventory()
            print("Player open inventory")
        # Handle horizontal movement
        if 'left' in self.keys_pressed or 'a' in self.keys_pressed:
            self.move_left()
        elif 'right' in self.keys_pressed or 'd' in self.keys_pressed:
            self.move_right()
        else:
            self.stop_horizontal_movement()

Builder.load_file('inventory.kv')
class PlayerInventory(Popup):
    """NEED DOCUMENTATION"""
    def __init__(self, inventory, **kwargs):
        super().__init__(**kwargs)
        self.inventory_data = inventory

    def on_open(self):
        self.populate_inventory(self.inventory_data)

    def populate_inventory(self, inventory):
        """Populate the inventory container with items"""
        container = self.ids.inventory_container
        container.clear_widgets()

        if inventory:
            for item in inventory:
                item_label = Label(
                    text=str(item),
                    size_hint_y=None,
                    height=40,
                    text_size=(None, None)
                )
                container.add_widget(item_label)
        else:
            empty_label = Label(
                text="Inventory is empty",
                size_hint_y=None,
                height=40
            )
            container.add_widget(empty_label)
