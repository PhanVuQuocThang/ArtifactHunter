from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.vector import Vector


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
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(**kwargs)
        self.pos = (x, y)
        self.size = (width, height)
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
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.inventory = []

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

        # Handle jump (immediate action)
        if key == 'spacebar':
            self.jump()

    def _on_keyboard_up(self, keyboard, keycode):
        """Handle key release events"""
        key = keycode[1]
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def process_input(self):
        """Process continuous key presses (called every frame)"""
        # Handle horizontal movement
        if 'left' in self.keys_pressed or 'a' in self.keys_pressed:
            self.move_left()
        elif 'right' in self.keys_pressed or 'd' in self.keys_pressed:
            self.move_right()
        else:
            self.stop_horizontal_movement()

    def update_graphics(self, *args):
        """Update the visual representation"""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def cleanup(self):
        """Clean up resources when player is destroyed"""
        self._keyboard_closed()