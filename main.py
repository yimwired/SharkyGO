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

        if self.top_pipe.x < -50:
            self.reset_pipes() # ท่อหมดจอ

        # เพิ่มระดับทุก ๆ 20 คะแนน
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
        # Calculate the gap size, ensuring it doesn't get too small
        gap = random.randint(100, 200)  # Random gap between pipes
        min_height = 50
        max_height = self.height - gap - min_height

        # Randomize pipe height
        pipe_height = random.randint(min_height, max_height)
        pipe_width = 60  # Constant pipe width

        # Change pipe images based on the level
        if self.level == 3:
            self.top_pipe.source = 'assets/images/rock.png'
            self.bottom_pipe.source = 'assets/images/rock.png'
        elif self.level == 2:
            self.top_pipe.source = 'assets/images/ice.png'
            self.bottom_pipe.source = 'assets/images/ice.png'
        else:
            self.top_pipe.source = 'assets/images/kelp.png'
            self.bottom_pipe.source = 'assets/images/kelp.png'


        # Position and adjust pipe size
        self.top_pipe.x = self.width  # Place top pipe at the right edge of the screen
        self.top_pipe.width = pipe_width
        self.top_pipe.height = self.height - (pipe_height + gap)  # Top pipe is above the gap

        self.bottom_pipe.x = self.width  # Place bottom pipe at the right edge of the screen
        self.bottom_pipe.width = pipe_width
        self.bottom_pipe.height = pipe_height  # Bottom pipe height is randomized

        self.bottom_pipe.y = pipe_height + gap  # Place bottom pipe below the gap

        # Reset pipe passed flag and adjust pipe speeds
        self.pipe_passed = False
        self.top_pipe.velocity_x = self.pipe_speed
        self.bottom_pipe.velocity_x = self.pipe_speed

class Pipe(Image):
    velocity_x = NumericProperty(-5) # ความเร็วท่อ

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/images/kelp.png'
        self.allow_stretch = True
        self.keep_ratio = False

    def move(self):
        self.x += self.velocity_x

class Shark(Image):
    velocity = ReferenceListProperty(NumericProperty(0), NumericProperty(0))
    gravity = -0.3
    jump_force = 7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.start_x = 0  # กำหนดจุดเริ่ม
        self.source = 'assets/images/shark.png'

    def move(self):
        self.velocity = Vector(self.velocity[0], self.velocity[1] + self.gravity)
        self.y += self.velocity[1]

    def jump(self):
        self.velocity = Vector(0, self.jump_force)
        self.jump_sound = SoundLoader.load('assets/sounds/jump.mp3')
        self.jump_sound.play()

class SharkyGoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    SharkyGoApp().run()