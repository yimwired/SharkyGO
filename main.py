#main.py
from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics.context_instructions import Rotate
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
import random

class MenuScreen(Screen):
    volume = NumericProperty(0.5)

    def on_enter(self):
        screen_width = Window.width
        screen_height = Window.height
        print(f"Screen Width: {screen_width}, Screen Height: {screen_height}")
                
    def adjust_volume(self, value):
        #ปรับเสียงพื้นหลัง
        self.volume = value
        if hasattr(self, 'background_music') and self.background_music:
            self.background_music.volume = value

class GameScreen(Screen):
    def on_enter(self):
        self.game = self.ids.game
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

class SharkyGoGame(Widget):
    shark = ObjectProperty(None)
    top_pipe = ObjectProperty(None)
    bottom_pipe = ObjectProperty(None)
    score = NumericProperty(0)
    pipe_passed = BooleanProperty(False)
    game_over = False  # จนกว่าจะจบ
    pipe_speed = NumericProperty(-5)  #ความเร็วท่อ Begin
    level = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
        self.volume = 0.5
        self.collision_sound = SoundLoader.load('assets/sounds/hitcute.mp3')
        self.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
        self.Epic_music = SoundLoader.load('assets/sounds/BackgroundEpic.mp3')

        if self.background_music:
            self.background_music.loop = True
            self.background_music.volume = self.volume
            self.background_music.play()

        self.background = Image(source='assets/images/background.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

    def on_key_down(self, window, key, *args):
        if key == 32:  # Spacebar key
            if self.game_over:
                self.restart_game()
            else:
                self.shark.jump()
    
    def update(self, dt):
        if self.game_over:
            return  # จบแล้วพอ อย่ายื้อ เอื้อ เจ็บ

        self.shark.move()
        self.top_pipe.move()
        self.bottom_pipe.move()

        if self.shark.y <= 0 or self.shark.top >= self.height:
            self.end_game()  # เรียกฟังก์ชันจบเกมตอนชนบนล่าง

        if self.shark.collide_widget(self.top_pipe) or self.shark.collide_widget(self.bottom_pipe):
            self.end_game()  # เรียกฟังก์ชันจบเกมชนobject

        if not self.pipe_passed and self.shark.x > self.top_pipe.x + self.top_pipe.width:
            self.score += 1
            self.pipe_passed = True  # ป้องกันนับซ้ำหลังผ่านท่อ

        if self.top_pipe.x + self.top_pipe.width < 0:  # If the top pipe is completely off the screen
            self.reset_pipes()  # Reset the pipes

        # เพิ่มระดับทุก ๆ 15 คะแนน
        new_level = (self.score // 15) + 1
        if new_level > self.level:
            self.level = new_level
            self.pipe_speed -= 1.5  # เพิ่มความเร็ว
            self.change_background(f'assets/images/new_background{min(self.level, 3)}.png')
            print(f"Level Up! Now Level {self.level}")
            if self.level >= 6 and self.Epic_music:
                self.Epic_music.play()

    # Reverted and added level-dependent background change
    def change_background(self, new_background):  # ฟังก์ชันเปลี่ยนพื้นหลัง
        self.background.source = new_background
        self.background.reload()

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart_game()
        else:
            self.shark.jump()

    def restart_game(self):
        self.score = 0
        self.game_over = False
        self.pipe_speed = -5 # ความเร็วท่อ Begin
        self.level = 1 # รีระดับ

        if self.Epic_music:
            self.Epic_music.stop()

        self.change_background('assets/images/background.png')

        self.shark.y = self.height / 2  # รีน้องฉลาม
        self.shark.velocity = Vector(0, 0)  # รีความเร็ว
        self.reset_pipes()
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # ทำให้เกมเริ่มใหม่

        gameover = self.ids.gameover
        gameover.opacity = 0
        gameover.disabled = True

    def end_game(self):
        self.game_over = True
        print("Game Over!")
        if self.collision_sound:
            self.collision_sound.volume = self.volume
            self.collision_sound.play()
        if self.Epic_music:
            self.Epic_music.stop()
        Clock.unschedule(self.update)

        gameover = self.ids.gameover
        gameover.opacity = 1
        gameover.disabled = False

    def reset_pipes(self):
        # Define a minimum and maximum gap size based on the screen height
        min_gap = 150  # Minimum gap size (adjust as needed)
        max_gap = 250  # Maximum gap size (adjust as needed)
        gap = random.randint(min_gap, max_gap)  # Random gap between pipes

        # Define minimum and maximum pipe heights
        min_height = 50  # Minimum height for pipes
        max_height = self.height - gap - min_height  # Maximum height based on screen height and gap

        # Randomize pipe height, ensuring the pipe is within valid height range
        pipe_height = random.randint(min_height, max_height)
        pipe_width = 60  # Set the pipe width to a constant value (e.g., 60 pixels)

        # Set pipe images based on the level
        if self.level == 3:
            self.top_pipe.source = 'assets/images/rock.png'
            self.bottom_pipe.source = 'assets/images/rock.png'
        elif self.level == 2:
            self.top_pipe.source = 'assets/images/ice.png'
            self.bottom_pipe.source = 'assets/images/ice.png'
        else:
            self.top_pipe.source = 'assets/images/kelp.png'
            self.bottom_pipe.source = 'assets/images/kelp.png'

        # Flip the top pipe's texture vertically
        self.top_pipe.flip_texture_vertically()

        # Position and adjust pipe size
        self.top_pipe.x = self.width  # Place top pipe at the right edge of the screen
        self.top_pipe.width = pipe_width  # Set pipe width
        self.top_pipe.height = self.height - (pipe_height + gap)  # Top pipe height adjusted based on random height and gap

        self.bottom_pipe.x = self.width  # Place bottom pipe at the right edge of the screen
        self.bottom_pipe.width = pipe_width  # Set pipe width
        self.bottom_pipe.height = pipe_height  # Bottom pipe height is randomized

        self.bottom_pipe.y = 0  # Place bottom pipe at the bottom of the screen

        # Reset pipe passed flag and adjust pipe speeds
        self.pipe_passed = False
        self.top_pipe.velocity_x = self.pipe_speed
        self.bottom_pipe.velocity_x = self.pipe_speed

class Pipe(Image):
    velocity_x = NumericProperty(-5)  # ความเร็วท่อ

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/images/kelp.png'
        self.allow_stretch = True
        self.keep_ratio = False

    def move(self):
        self.x += self.velocity_x
        if self.x + self.width < 0:  # If the pipe is completely off the screen
            self.parent.reset_pipes()  # Reset the pipes

    def flip_texture_vertically(self):
        """Flips the texture vertically."""
        if self.texture:
            self.texture.flip_vertical()

class Shark(Image):
    velocity = ReferenceListProperty(NumericProperty(0), NumericProperty(0))
    gravity = -0.3
    jump_force = 7
    angle = NumericProperty(0)  # Define angle as a Kivy property

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.angle = 0  # Initialize the angle attribute
        self.start_x = 0  # กำหนดจุดเริ่ม
        self.source = 'assets/images/shark.png'

        # Apply rotation transformation
        with self.canvas.before:
            self.push_matrix = PushMatrix()
            self.rot = Rotate()
            self.rot.origin = (self.center_x, self.center_y)  # Rotate around center
            self.rot.angle = self.angle  # Initialize rotation angle
            self.pop_matrix = PopMatrix()

        # Bind properties
        self.bind(angle=self.update_rotation, pos=self.on_pos)

    def update_rotation(self, instance, value):
        """Updates the rotation angle using the canvas transformation."""
        self.rot.angle = value

    def on_pos(self, *args):
        """Update the rotation origin when the shark's position changes."""
        self.rot.origin = (self.center_x, self.center_y)

    def move(self):
        self.velocity = Vector(self.velocity[0], self.velocity[1] + self.gravity)
        self.y += self.velocity[1]

        # Add a tilt effect when moving
        if self.velocity[1] > 0:
            self.rotation_animation(15)  # Rotate up when moving up
        else:
            self.rotation_animation(-15)  # Rotate down when falling

    def jump(self):
        self.velocity = Vector(0, self.jump_force)
        self.jump_sound = SoundLoader.load('assets/sounds/jump.mp3')
        self.jump_sound.play()

        # Animate rotation slightly upwards when jumping
        self.rotation_animation(30)

    def rotation_animation(self, target_angle):
        anim = Animation(angle=target_angle, duration=0.2)
        anim.start(self)

class SharkyGoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    SharkyGoApp().run()