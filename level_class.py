"""This file contains all the main classes that'll be used across the project."""
from typing import List

from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.vector import Vector
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.app import App

from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.animation import Animation
from random import randint, shuffle
from utils import resource_path


class PlaceHolder(Widget):
    """
    Acts as placeholder for any object. Has no other functionality. This class shouldn't be inherited.
    """
    def __init__(self, position=(0, 0), size=(40, 40), color=(1, 1, 1), texture_path=None, **kwargs):
        super().__init__(**kwargs)

        # Set widget position and size
        self.pos = position
        self.size = size

        with self.canvas:
            if texture_path:
                texture = CoreImage(texture_path).texture
                Color(1, 1, 1, 1)
                self.rect = Rectangle(texture=texture, pos=position, size=size)
            else:
                Color(*color)
                self.rect = Rectangle(pos=position, size=size)

    def update(self, position, size, color=None, texture_path=None):
        """Update the square's position, size, and optionally color or texture"""
        self.rect.pos = position
        self.rect.size = size
        if texture_path:
            texture = CoreImage(texture_path).texture
            texture.wrap = 'repeat'
            texture.uvsize = (1, 1)  # Adjust as needed
            self.rect.texture = texture
        elif color:
            # Remove and redraw with new color (texture will be removed)
            self.canvas.remove(self.rect)
            with self.canvas:
                Color(*color)
                self.rect = Rectangle(pos=position, size=size)

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




class OldPlatform(Widget):
    def __init__(self, x, y, tile_size=40, texture_path=None, **kwargs):
        super().__init__(**kwargs)

        self.size = (tile_size, tile_size)
        self.pos = (x, y)

        with self.canvas:
            if texture_path:
                texture = CoreImage(texture_path).texture
                texture.wrap = 'repeat'
                Color(1, 1, 1, 1)  # Reset tint to white
                self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
            else:
                Color(0.6, 0.4, 0.2, 1)  # Default brown color
                self.rect = Rectangle(pos=self.pos, size=self.size)

        # Keep rect in sync if position changes
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Platform(Widget):
    def __init__(self, x, y, num_tiles_x, num_tiles_y, texture_path, tile_width=40, tile_height=40, **kwargs):
        super().__init__(**kwargs)
        self.size = (tile_width * num_tiles_x, tile_height * num_tiles_y)
        self.pos = (x, y)

        # Load texture
        texture = CoreImage(texture_path).texture
        texture.wrap = 'repeat'  # VERY important!
        texture.uvsize = (num_tiles_x, num_tiles_y)  # Repeat X times; flip Y if needed

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, pos=self.pos, size=self.size)

class DeathTrap(Platform):
    def __init__(self, x, y, num_tiles_x, num_tiles_y, texture_path, tile_width=40, tile_height=10, **kwargs):
        super().__init__(x=x, y=y,
                         num_tiles_x=num_tiles_x, num_tiles_y=num_tiles_y,
                         texture_path=texture_path,
                         tile_width=tile_width, tile_height=tile_height,
                         **kwargs)

        self.damage = 20

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
        self.last_direction = Vector(1, 0)

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
        self.last_direction = Vector(-1, 0)

    def move_right(self):
        self.velocity.x = self.move_speed
        self.last_direction = Vector(1, 0)

    def stop_horizontal_movement(self):
        self.velocity.x = 0

class Player(Entity):
    def __init__(self, x=0, y=0, width=40, height=40, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.inventory = [] # Need to also handle inventory input
        self.inventory_popup = None # Inventory object
        self.health = 3
        self.airborne_with_no_movement_input = False # This is for animation, look at the update method

        self.last_direction = Vector(1, 0)
        self.last_shot_time = Clock.get_boottime()  # For cooldown
        self.shoot_cooldown = 0.3  # seconds

        self.invincible = False
        self.can_double_jump = False
        self.has_double_jumped = False
        # Input handling
        self.keys_pressed = set()
        self._keyboard = None

        # Set up keyboard input
        self.setup_keyboard()

        # Animation setup
        self.current_animation = 'move_right'
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 0.2  # Seconds per frame

        # Load your sprite images (replace with your actual image paths)
        self.sprites = {
            'idle': [
                CoreImage(resource_path('assets/sprites/Characters/slime_character/slime_idle.png')).texture
            ],
            'move_left': [
                CoreImage(resource_path('assets/sprites/Characters/slime_character/slime_left.png')).texture
            ],
            'move_right': [
                CoreImage(resource_path('assets/sprites/Characters/slime_character/slime_right.png')).texture
            ],
            'jump': [CoreImage(resource_path('assets/sprites/Characters/slime_character/slime_jump.png')).texture]  # Single frame for jump
        }

        # Draw the player
        with self.canvas:
            Color(1, 1, 1)  # White color to show texture properly
            self.rect = Rectangle(pos=self.pos, size=self.size,
                                  texture=self.sprites['idle'][0])

        # Bind position changes to update the rectangle
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_animation(self, dt):
        """Update sprite animation frames"""
        self.animation_timer += dt

        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            frames = self.sprites[self.current_animation]

            if len(frames) > 1:  # Only animate if multiple frames
                self.frame_index = (self.frame_index + 1) % len(frames)
                self.rect.texture = frames[self.frame_index]

    def set_animation(self, animation_name):
        """Change animation state"""
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0
            # Set initial texture
            self.rect.texture = self.sprites[animation_name][0]

    def update(self, dt):
        super().update(dt)
        # Determine animation based on movement state
        if self.last_direction.x < 0:
            self.set_animation('move_left')
        elif self.last_direction.x > 0:
            self.set_animation('move_right')
        else:
            self.set_animation('idle')

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
        """Update rectangle position and size"""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def cleanup(self):
        """Clean up resources when player is destroyed"""
        self._keyboard_closed()
        # Cancel any scheduled events
        Clock.unschedule(self.end_invincibility)
        Clock.unschedule(self.restore_color)

    def toggle_inventory(self, pressed_key:str='b'):
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
    def apply_inventory_effects(self):
        """Apply item effects from inventory"""
        self.can_double_jump = False
        self.damage = 10
        self.max_health = 100
        self.current_health = min(getattr(self, "current_health", self.max_health), self.max_health)
    
        for item in self.inventory:
            name = getattr(item, 'name', str(item)).lower()
            if name == 'sky rocket':
                self.can_double_jump = True
            elif name == 'acient shotgun':
                self.damage = 20
            elif name == 'meat armor':
                self.max_health = 200
                self.current_health = min(self.current_health, self.max_health)


    # def has_marioowo(self):
    #     """Check if player has 'Marioowo' in inventory."""
    #     for item in self.inventory:
    #         if hasattr(item, 'name') and item.name == 'Marioowo':
    #             return True
    #     return False
    def jump(self):
        """Handle jumping logic, including double jump if applicable."""
        if self.on_ground:
            super().jump()
            self.has_double_jumped = False  # Reset on first jump
        elif self.can_double_jump and not self.has_double_jumped:
            self.velocity.y = self.jump_speed
            self.has_double_jumped = True

    def process_input(self):
        if getattr(self.parent, "paused", False):
            return
        """Process continuous key presses (called every frame)"""
        # Handle jump
        if 'up' in self.keys_pressed or 'w' in self.keys_pressed:
            if self.on_ground:
                self.jump()
            elif self.can_double_jump and not self.has_double_jumped:
                self.on_ground = True
                self.jump()
                self.has_double_jumped = True
        # Handle open inventory
        # if 'b' in self.keys_pressed:
        #     self.toggle_inventory()
        #     print("Player open inventory")
        # Handle shooting
        if 'spacebar' in self.keys_pressed:
            self.shoot_towards_cursor()
            print("Position:", self.pos)
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
        app = App.get_running_app()
        app.current_playing_screen = app.root.current 
        app.is_paused = True
        self.parent.paused = True
        SoundManager.play("gameover")
        popup = Factory.GameOverPopup()
        popup.open()

########
    def shoot_towards_cursor(self):
        # Get current time to enforce shooting cooldown
        now = Clock.get_boottime()
        if now - self.last_shot_time < self.shoot_cooldown:
            return  # Too soon to shoot again

        self.last_shot_time = now   # Update the last shot timestamp
        
        # Determine shooting direction based on key pressed
        if 'right' in self.keys_pressed or 'd' in self.keys_pressed:
            direction = Vector(1, 0)
            self.last_direction = direction
        elif 'left' in self.keys_pressed or 'a' in self.keys_pressed:
            direction = Vector(-1, 0)
            self.last_direction = direction
        else:
            direction = self.last_direction     # Default to last used direction

        # Create a new projectile and add it to the level
        proj = Projectile(x=self.center_x, y=self.center_y, direction=direction,
            speed=500, damage=10, owner="player")
        self.parent.add_widget(proj)
        self.parent.projectiles.append(proj)

        # Play shooting sound and trigger animation
        SoundManager.play("shoot")
        # self.animate_attack()

    # def animate_attack(self):
    #     # Simple visual feedback (flash color)
    #     self.canvas.remove(self.rect)
    #     with self.canvas:
    #         Color(1, 1, 0)  # yellow when attacking
    #         self.rect = Rectangle(pos=self.pos, size=self.size)
    #     Clock.schedule_once(self.restore_color, 0.1)
    # # Restore player's original color (blue) after attack animation
    # def restore_color(self, dt):
    #     self.canvas.remove(self.rect)
    #     with self.canvas:
    #         Color(0, 0, 1)
    #         self.rect = Rectangle(pos=self.pos, size=self.size)

####
#Builder.load_file('inventory.kv')
class PlayerInventory(Popup):
    """NEED DOCUMENTATION"""
    def __init__(self, inventory, **kwargs):
        super().__init__(**kwargs)
        self.inventory_data = inventory

    def on_open(self):
        self.apply_item_effects(self.inventory_data)
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

    def apply_item_effects(self, inventory):
        player = self.get_player_instance()
        if player:
            player.apply_inventory_effects()


    def get_player_instance(self):
        # Try to find the player instance from the popup's parent chain
        parent = self.parent
        while parent:
            if hasattr(parent, 'player'):
                return parent.player
            parent = getattr(parent, 'parent', None)
        return None
class Artifact(Entity):
    """
    Represents a collectible artifact that grants the player special abilities
    and is required to complete a level.
    """
    def __init__(self, name, x=0, y=0, width=100, height=100, texture_path=None, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.is_collected = False
        self.name = name  # Name of the artifact
        self.texture_path = texture_path

        # Draw the artifact
        with self.canvas:
            if self.texture_path:
                texture = CoreImage(self.texture_path).texture
                texture.wrap = 'repeat'  # Allow texture to repeat
                Color(1, 1, 1, 1)
                self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
            else:
                Color(1, 0.84, 0)  # Gold
                self.rect = Rectangle(pos=self.pos, size=self.size)

        # Bind position and size changes to update the rectangle
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        """Update the visual representation when position or size changes"""
        self.rect.pos = self.pos
        self.rect.size = self.size


    def pick_up(self, player):
        """
        Check collision with player and pick up the artifact if collided.
        """
        if self.is_collected:
            return  # Prevent picking up the same artifact multiple times

        if self.collide_widget(player):
            self.is_collected = True
            if hasattr(player, "inventory_add_item"):
                print(f"Artifact '{self.name}' collected by player!")
                player.inventory_add_item(self)

                # Immediately apply effects here
                if hasattr(player, 'apply_inventory_effects'):
                    player.apply_inventory_effects()

            # Optionally, remove the artifact from the screen
            if self.parent:
                self.parent.remove_widget(self)



    def unlock_level(self):
        """
        Logic to unlock the next level.
        You can implement actual screen/level management elsewhere.
        """
        if not self.is_collected:
            print(f"Cannot unlock level. Artifact '{self.name}' not collected.")
            return
        print(f"Artifact '{self.name}' collected! Unlocking next level...")

class Enemy(Entity):
    """
    Represents an enemy that can move and attack the player.
    """
    def __init__(self, x=0, y=0, width=100, height=100, texture_path=None, shoot_cooldown = 2.0, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.max_health = 30
        self.current_health = 30
        self.attack_damage = 10
        self.is_alive = True
        self.direction = 1  # 1 for right, -1 for left
        self.move_speed = 0  # Enemy moves slower than player

        # Cooldown bắn
        self.shoot_interval = shoot_cooldown  # seconds
        self.last_shot_time = Clock.get_boottime()

        self.texture_path = texture_path

        # Draw the enemy as a red rectangle or with texture if provided
        with self.canvas:
            if self.texture_path:
                texture = CoreImage(self.texture_path).texture
                Color(1, 1, 1, 1)
                self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
            else:
                Color(1, 0, 0)  # Red color
                self.rect = Rectangle(pos=self.pos, size=self.size)

        # Bind position changes to update the rectangle
        self.bind(pos=self.update_graphic, size=self.update_graphic)
    
    def alive(self):
        return self.current_health > 0
    
    def update(self, dt, player, platforms, level):
        """
        Update enemy position, handle wall/gap detection, and check collision with player.
        :param dt: Delta time
        :param player: Player instance
        :param platforms: List of Platform instances
        """
        if getattr(level, "paused", False):
            return 
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

        # Attempt to shoot if allowed by cooldown
        self.try_shoot(player, level)

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

####
    def try_shoot(self, player, level):
        # Get the current time since app started
        now = Clock.get_boottime()

        # Enforce shooting cooldown: exit if not enough time has passed
        if now - self.last_shot_time < self.shoot_interval:
            return

        distance = Vector(player.center_x - self.center_x,
                        player.center_y - self.center_y).length()
        if distance > 300:  # Only shoot if player is within 300 pixels
            return

        self.last_shot_time = now # Update the last shot time to current time

        # Determine direction vector from enemy to player and normalize it
        direction = Vector(player.center_x - self.center_x,
                        player.center_y - self.center_y).normalize()
        # Create the projectile moving in the calculated direction
        bullet = Projectile(x=self.center_x, y=self.center_y,
            direction=direction, speed=300, damage=10, owner="enemy"
        )
        # Add bullet to level scene and tracking list
        level.add_widget(bullet)
        level.projectiles.append(bullet)

        SoundManager.play("shoot")

    def update_graphic(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BaseLevelContents(Widget):
    """Contain the base contents of levels. This one only handles the main logic."""

    def check_collisions(self):
        """Check collisions between player and platforms and artifacts."""
        # Type hinting for IDEs so it's less of a pain to work with.
        # Doesn't interrupt the code with or without these.
        self.player : Player
        self.platforms : List[Platform]

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

                if isinstance(platform, DeathTrap):
                    self.player.current_health -= platform.damage
                    print("Player health:", self.player.current_health)

                if isinstance(platform, Artifact):
                    self.player.inventory_add_item(platform.name)
                    self.remove_widget(platform)
                    self.platforms.remove(platform)

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
                elif self.player.velocity.x > 0 and min_overlap == overlap_left:
                    self.player.velocity.x = 0
                elif self.player.velocity.x < 0 and min_overlap == overlap_right:
                    self.player.velocity.x = 0

        self.player.on_ground = on_ground_temp


    def update(self, dt):
        """Main game update loop. This is called by Clock.schedule_interval.
        Follow: process input -> check collisions -> update"""
        self.player.process_input()
        self.check_collisions()
        self.player.update(dt)

    def cleanup(self):
        """Clean up game resources"""
        if hasattr(self.player, 'cleanup'):
            self.player.cleanup()

class Projectile(Entity):
    def __init__(self, x, y, direction, speed, damage, owner, decay_time=2.0, max_bounce=0, **kwargs):
        super().__init__(x, y, 10, 4, **kwargs)
        self.direction = Vector(direction).normalize() # Normalize the direction vector
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.velocity = self.direction * self.speed
        self.decay_time = decay_time
        self.max_bounce = max_bounce
        self.bounce_count = 0

        self.spawn_time = Clock.get_boottime() # Time when projectile is created

        with self.canvas:
            Color(0, 1, 0, 1) if owner == "player" else Color(1, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update(self, dt, level):
        if not self.parent:
            return  # Don't update if removed from screen

        self.pos = (self.pos[0] + self.velocity.x * dt, self.pos[1] + self.velocity.y * dt)

        if Clock.get_boottime() - self.spawn_time > self.decay_time:
            if self.parent:
                self.parent.remove_widget(self)
            if self in level.projectiles:
                level.projectiles.remove(self)
            return

        for platform in level.platforms:
            if self.collide_widget(platform):
                if self.max_bounce > 0 and self.bounce_count < self.max_bounce:
                    self.velocity.x *= -1   # Reverse horizontal direction
                    self.bounce_count += 1
                else:
                    if self.parent:
                        self.parent.remove_widget(self)
                    if self in level.projectiles:
                        level.projectiles.remove(self)
                return

        targets = [level.player] if self.owner != "player" else level.enemies
        for target in targets:
            if self.collide_widget(target):
                if hasattr(target, 'current_health'):
                    target.current_health -= self.damage     # Apply damage
                    print(f"{target.name} trúng đạn! HP còn: {target.current_health}")
                    if isinstance(target, Player) and target.current_health <= 0:
                        target.die()
                # Xử lý chết
                if target.current_health <= 0 and target in level.enemies:
                    level.remove_widget(target)     # Remove dead enemy
                    level.enemies.remove(target)

                for _ in range(6):
                    part = Particle(self.center, color=(1, 0.6, 0)) # Create explosion particles
                    level.add_widget(part)
                    level.particles.append(part)
                if self.parent:
                    self.parent.remove_widget(self)
                if self in level.projectiles:
                    level.projectiles.remove(self)
                return


class Particle(Widget):
    def __init__(self, pos, color=(1, 1, 0), lifetime=0.3, **kwargs):
        super().__init__(**kwargs)
        self.size = (6, 6)
        self.pos = (pos[0] - 3, pos[1] - 3)
        self.velocity = Vector(1, 0).rotate(randint(0, 360)) * 100

        with self.canvas:
            Color(*color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_interval(self._update, 1/60)
        Clock.schedule_once(self._destroy, lifetime)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update(self, dt):
        self.pos = (self.pos[0] + self.velocity.x * dt, self.pos[1] + self.velocity.y * dt)

    def _destroy(self, dt):
        if self.parent:
            self.parent.remove_widget(self)

class PuzzleComponent(Widget):
    # List of all available quiz questions
    QUESTIONS = [
        ("Which ancient civilization developed the earliest writing system?", tuple(["Sumer", "Egypt", "Rome", "Greece"]), 0),
        ("Which ancient city is famous for being located in the Egyptian desert?", tuple(["Thebes", "Babylon", "Carthage", "Persepolis"]), 0),
        ("What type of roads did the Romans use to connect their empire?", tuple(["Stone roads", "Dirt roads", "Wooden roads", "Railroads"]), 0),
        ("Which technology is shaping the cities of the future?", tuple(["Artificial Intelligence", "Steam Engine", "Subway", "Mobile Phone"]), 0),
        ("Which city is famous for its canal system instead of roads?", tuple(["Venice", "Amsterdam", "Bangkok", "Singapore"]), 0),
        ("Which was the first city in the world to build a subway system?", tuple(["London", "Paris", "New York", "Berlin"]), 0),
    ]

    _used_questions = set() # Set to track already-used questions

    @classmethod
    def get_puzzles_for_level(cls, level_number):
        """Return a list of PuzzleComponent objects based on level.
        Level 1 → 1 question, Level 2 → 2 questions, Level 3 → 3 questions.
        """
        count_map = {1: 1, 2: 2, 3: 3}
        count = count_map.get(level_number, 0)

        remaining = [q for q in cls.QUESTIONS if q not in cls._used_questions]
        shuffle(remaining)
        selected = remaining[:count]
        cls._used_questions.update(selected)

        puzzles = []
        for i, (q, ans, correct) in enumerate(selected):
            pos = (400, 500 - i * 120)
            puzzles.append(cls(pos, q, list(ans), correct))

        return puzzles
    
    def __init__(self, pos, question, answers, correct_index, level_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        self.pos = pos
        self.question = question
        self.answers = answers
        self.correct_index = correct_index
        self.level_ref = level_ref  # Reference to the level (for enemy checking)

        self.max_wrong_attempts = 2
        self.wrong_attempts = 0
        self.locked_until_enemy_dead = False

        self.solved = False
        self.show_prompt = False

        with self.canvas:
            self.rect = Image(source=resource_path("assets/sprites/question_block.png"), pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_interval(self._check_player_interaction, 1 / 30)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def solve(self):
        self.solved = True
        self.show_hint("✅ Correct! You solved the puzzle.")
        
    def _check_player_interaction(self, dt):
        if not self.parent or not hasattr(self.parent, 'player'):
            return
        if self.collide_widget(self.parent.player) and not self.solved:
            self.show_question_popup()

    def show_question_popup(self):
        if self.show_prompt or self.solved:
            return

        if App.get_running_app().is_paused:
            return

        if self.locked_until_enemy_dead and any(e.alive() for e in self.level_ref.enemies):
            self.show_hint("🔒 Eliminate all enemies before continuing!")
            return
        self.locked_until_enemy_dead = False

        if self.level_ref:
            self.level_ref.active_puzzle_popup = self
            if hasattr(self.level_ref, "paused"):
                self.level_ref.paused = True  # Pause game
        self.show_prompt = True

        root = FloatLayout(size_hint=(1, 1))

        title_label = Label(text="🧠 Puzzle Time!", font_size='32sp',
            color=(1, 0.27, 0.27, 1), bold=True, size_hint=(None, None),
            size=(700, 60), pos_hint={'center_x': 0.5, 'top': 0.98})
        root.add_widget(title_label)

        main_box = Factory.MainBox()
        question_lbl = Factory.QuestionLabel(text=self.question)
        main_box.add_widget(question_lbl)

        for i, ans in enumerate(self.answers):
            btn = Factory.AnswerButton(text=ans)
            btn.bind(on_press=self._on_correct_answer if i == self.correct_index else self._on_wrong_answer)
            main_box.add_widget(btn)

        root.add_widget(main_box)

        self.popup = Popup(
            title='', content=root, size_hint=(None, None), size=(700, 550),
            auto_dismiss=False, separator_height=0,
            background='', background_color=(0, 0, 0, 0), opacity=0 )
        Animation(opacity=1, duration=0.35, t='out_quad').start(self.popup)
        self.popup.open()

    def _on_correct_answer(self, instance):
        if self.popup: 
            self.popup.dismiss()
        self.show_prompt = False
        if hasattr(self.level_ref, "paused"):
            self.level_ref.paused = False  # Resume game
        SoundManager.play("correct")  # 🔊 play correct sound
        self.solve()

    def _on_wrong_answer(self, instance):
        if self.popup: 
            self.popup.dismiss()
        self.show_prompt = False
        if hasattr(self.level_ref, "paused"):
            self.level_ref.paused = False  # Resume game
        self.wrong_attempts += 1
        SoundManager.play("incorrect")  # 🔊 play incorrect sound

        if self.wrong_attempts >= self.max_wrong_attempts:
            self.locked_until_enemy_dead = True   
            Clock.schedule_once(lambda dt: self.show_hint("❌ Incorrect twice! Defeat enemies to try again."), 2 )            
        else:
            self.show_hint("❌ Wrong! You have {}/{} attempts.".format(
                self.max_wrong_attempts - self.wrong_attempts, self.max_wrong_attempts))

    def show_hint(self, msg):
        offset = 60 if "🔒 Eliminate all enemies before continuing!" in msg else 20
        hint = Label(text=msg, pos=(self.x, self.top + offset), size_hint=(None, None),
            size=(300, 40), color=(1, 1, 1, 1), bold=True,font_size='18sp')
        
        Window.add_widget(hint)
        Clock.schedule_once(lambda dt: Window.remove_widget(hint), 2)
        
    def update(self):
        pass

class SoundManager:
    music_volume = 0.7
    sfx_volume = 0.8
    sounds = {}
    music = None

    @classmethod
    def load(cls):
        cls.sounds["shoot"] = SoundLoader.load(resource_path("assets/sounds/shoot.wav"))
        cls.sounds["correct"] = SoundLoader.load(resource_path("assets/sounds/correct.wav"))
        cls.sounds["incorrect"] = SoundLoader.load(resource_path("assets/sounds/incorrect.wav"))
        cls.sounds["gameover"] = SoundLoader.load(resource_path("assets/sounds/gameover.wav"))
        # ... add other sounds if available
        
        for sound in cls.sounds.values():
            if sound:
                sound.volume = cls.sfx_volume

        '''# Tải nhạc nền nếu có
        cls.music = SoundLoader.load(resource_path("assets/music/background_music.mp3"))
        if cls.music:
            cls.music.loop = True
            cls.music.volume = cls.music_volume
            cls.music.play()'''

    @classmethod
    def play(cls, name):
        sound = cls.sounds.get(name)
        if sound:
            sound.volume = cls.sfx_volume
            sound.stop()
            sound.play()

    @classmethod
    def set_music_volume(cls, volume):
        cls.music_volume = volume
        if cls.music:
            cls.music.volume = volume

    @classmethod
    def set_sfx_volume(cls, volume):
        cls.sfx_volume = volume
        for sound in cls.sounds.values():
            if sound:
                sound.volume = volume
   