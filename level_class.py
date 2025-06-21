"""This file contains all the main classes that'll be used across the project."""

from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.lang import Builder
from kivy.clock import Clock

from abc import ABC, abstractmethod

class GameObject(Widget):
    """Base class for game objects that appear on the screen."""
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(**kwargs)
        self.pos = (x, y)
        self.size = (width, height)
        with self.canvas:
            Color(1, 1, 0)  # Default: Yellow for GameObjects
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Artifact(GameObject):
    """
    Represents a collectible artifact that grants the player special abilities
    and is required to complete a level.
    """
    def __init__(self, name, description, x=0, y=0, width=100, height=100, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.is_collected = False
        self.name = name
        self.description = description

        # Draw the artifact differently (e.g., gold color)
        with self.canvas:
            Color(1, 0.84, 0)  # Gold
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def pick_up(self, player):
        """
        Add this artifact to the player's inventory and mark it as collected.
        """
        if not self.is_collected:
            player.inventory_add_item(self)
            self.is_collected = True
            self.parent.remove_widget(self)  # Remove from scene if needed

    def unlock_level(self):
        """
        Logic to unlock the next level.
        You can implement actual screen/level management elsewhere.
        """

        if not self.is_collected:
            print(f"Cannot unlock level. Artifact '{self.name}' not collected.")
            return
        print(f"Artifact '{self.name}' collected! Unlocking next level...")


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
        # if self.on_ground:
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
        self.health = 3
        self.invincible = False
        # self.can_double_jump = False
        # self.has_double_jumped = False
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

    # def has_marioowo(self):
    #     """Check if player has 'Marioowo' in inventory."""
    #     for item in self.inventory:
    #         if hasattr(item, 'name') and item.name == 'Marioowo':
    #             return True
    #     return False

    def process_input(self):
        """Process continuous key presses (called every frame)"""
        # # Check for Marioowo in inventory to enable double jump
        # self.can_double_jump = self.has_marioowo()

        # Temporary solution to exit level. This will change.
        if 'q' in self.keys_pressed:
            self.parent.parent.manager.current = 'level_selection'
        # Handle jump
        if 'spacebar' in self.keys_pressed:
            if self.on_ground:
                self.jump()
            # elif self.can_double_jump and not self.has_double_jumped:
            #     self.jump()
            #     self.has_double_jumped = True
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

    def on_enemy_collision(self, enemy):
        if self.invincible:
            return

        print(f"Collided with enemy: {enemy}")
        self.health -= 1
        print(f"Player health: {self.health}")

        if self.health <= 0:
            self.die()
        else:
            self.become_invincible()

    def become_invincible(self):
        self.invincible = True
        Clock.schedule_once(self.end_invincibility, 2)  # 2 seconds of invincibility

    def end_invincibility(self, dt):
        self.invincible = False

    def die(self):
        print("Player died")
        #Implement death logic here, such as respawning or ending the game


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
class Enemy(Entity):
    """
    Represents an enemy that can move and attack the player.
    """
    def __init__(self, x=0, y=0, width=100, height=100, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.health = 100
        self.attack_damage = 1
        self.is_alive = True
        self.direction = 1  # 1 for right, -1 for left
        self.move_speed = 150  # Enemy moves slower than player

        # Draw the enemy as a red rectangle
        with self.canvas:
            Color(1, 0, 0)  # Red color
            self.rect = Rectangle(pos=self.pos, size=self.size)

        # Bind position changes to update the rectangle
        self.bind(pos=self.update_graphic, size=self.update_graphic)

    def update(self, dt, player, platforms):
        """
        Update enemy position, handle wall/gap detection, and check collision with player.
        :param dt: Delta time
        :param player: Player instance
        :param platforms: List of Platform instances
        """
        # Move horizontally
        self.velocity.x = self.direction * self.move_speed
        self.pos = (
            self.pos[0] + self.velocity.x * dt,
            self.pos[1] + self.velocity.y * dt
        )

        # Wall collision: reverse direction if hitting screen edge
        if self.pos[0] <= 0:
            self.move_right()
        elif self.pos[0] >= Window.width - self.size[0]:
            self.move_left()

        # Gap detection: if no platform under front foot, reverse direction
        if not self._is_platform_ahead(platforms):
            self.direction *= -1

        # Check collision with player
        if self.collide_widget(player):
            self.hit_player(player)

        self.update_graphic()

    def _is_platform_ahead(self, platforms):
        """
        Check if there is a platform under the enemy's front foot.
        """
        # Check the front foot position
        if self.direction == 1:
            foot_x = self.pos[0] + self.size[0] + 1
        else:
            foot_x = self.pos[0] - 1
        foot_y = self.pos[1] - 1  # Just below the enemy

        for platform in platforms:
            px, py = platform.pos
            pw, ph = platform.size
            if px <= foot_x <= px + pw and py <= foot_y <= py + ph:
                return True
        return False

    def hit_player(self, player):
        """
        Deal damage to the player if colliding.
        """
        if hasattr(player, "current_health"):
            player.current_health -= self.attack_damage
            # Optionally, you can add knockback or invulnerability frames here
        
    def update_graphic(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
class BaseLevelContents(Widget):
    """Contain the base contents of levels. This one only handles the main logic."""
    @abstractmethod
    def create_platform(self):
        pass

    def check_collisions(self):
        """Check collisions between player and platforms."""
        # Type hinting for IDEs so it's less of a pain to work with.
        # Doesn't interrupt the code with or without these.
        self.player : Player
        self.platform : Platform

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
            if (player_rect[0] < platform_rect[0] + platform_rect[2] and
                    player_rect[0] + player_rect[2] > platform_rect[0] and
                    player_rect[1] < platform_rect[1] + platform_rect[3] and
                    player_rect[1] + player_rect[3] > platform_rect[1]):

                # Calculate overlap distances for each direction
                # Read the comments to prevent misused of these variables. They follow standard naming for overlapping.
                overlap_left = (player_rect[0] + player_rect[2]) - platform_rect[0]  # platform's left - player's right
                overlap_right = (platform_rect[0] + platform_rect[2]) - player_rect[0]  # platform's right - player's left
                overlap_top = (platform_rect[1] + platform_rect[3]) - player_rect[1]  # platform’s top - player’s bottom
                overlap_bottom = (player_rect[1] + player_rect[3]) - platform_rect[1]  # platform's bottom - player's top
                min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

                # Player is falling down onto platform
                if self.player.velocity.y <= 0 and min_overlap == overlap_top:
                    # Place player on top of platform
                    self.player.pos = (
                        self.player.pos[0],
                        platform_rect[1] + platform_rect[3]
                    )
                    self.player.velocity.y = 0
                    on_ground_temp = True

                # Player is head hitting the bottom of platform
                elif self.player.velocity.y > 0 and min_overlap == overlap_bottom:
                    self.player.velocity.y = -50 # Makes the player fall faster

                # Player is touching the sides of platform
                elif self.player.velocity.x != 0 and (min_overlap == overlap_right or min_overlap == overlap_left):
                    self.player.velocity.x = 0
                break # Stop checking other platforms after first collision

        self.player.on_ground = on_ground_temp


    def update(self, dt):
        """Main game update loop. This is called by Clock.schedule_interval.
        Follow: process input -> check collisions -> update"""
        self.player.process_input()
        self.check_collisions()
        self.player.update(dt)

    def cleanup(self):
        """Clean up game resources"""
        self.clear_widgets()
        if hasattr(self.player, 'cleanup'):
            self.player.cleanup()
