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
    def on_enter(self):
        # Get screen size
        screen_width = Window.width
        screen_height = Window.height
        print(f"Screen Width: {screen_width}, Screen Height: {screen_height}")

        if not hasattr(self, 'background_music'):
            self.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
   #         if self.background_music:
    #            self.background_music.loop = True
     #           self.background_music.play()

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
    speed_boosted_50 = BooleanProperty(False)
    speed_boosted_100 = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collision_sound = SoundLoader.load('assets/sounds/hitcute.mp3')
        self.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
        self.Epic_music = SoundLoader.load('assets/sounds/BackgroundEpic.mp3')

        self.background = Image(source='assets/images/background.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

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
            self.score += 50
            self.pipe_passed = True  # ป้องกันนับซ้ำหลังผ่านท่อ

        if self.top_pipe.x < -50:
            self.reset_pipes() # ท่อหมดจอ

        if self.score >= 50 and not self.speed_boosted_50: # สร้างเงื่อนไขให้มีการเช็คครั้งเดียว
            self.pipe_speed -= 2  # ท่อเคลื่อนที่เร็วขึ้น
            self.change_background('assets/images/new_background.png')
            self.speed_boosted_50 = True
            print("Harder!!!")

        if self.score >= 100 and not self.speed_boosted_100: # สร้างเงื่อนไขให้มีการเช็คครั้งเดียว
            self.pipe_speed -= 2.5  # ท่อเร็วขึ้นอีก
            self.change_background('assets/images/new_background2.png')
            if self.Epic_music:
                self.Epic_music.play()
            self.speed_boosted_100 = True
            print("God Mode!!!")

    def change_background(self, new_background): # ฟังก์ชันเปลี่ยนพื้นหลัง
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
        self.speed_boosted_50 = False # รีความเร็วท่อ
        self.speed_boosted_100 = False # รีความเร็วท่อ

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
            self.collision_sound.play()
        if self.Epic_music:
            self.Epic_music.stop()
        Clock.unschedule(self.update)

        gameover = self.ids.gameover
        gameover.opacity = 1
        gameover.disabled = False

    def reset_pipes(self):
        gap = 200  # ระยะห่างท่อ
        min_height = 50
        max_height = self.height - gap - min_height

        pipe_height = random.randint(min_height, max_height)

        self.top_pipe.x = self.width
        self.bottom_pipe.y = 0  # ท่อบน
        self.bottom_pipe.height = pipe_height

        self.bottom_pipe.x = self.width
        self.top_pipe.y = pipe_height + gap
        self.top_pipe.height = self.height - (pipe_height + gap)  # ท่อล่าง

        self.pipe_passed = False  # reset คะแนน
        self.top_pipe.velocity_x = self.pipe_speed  # ปรับความเร็วของท่อ
        self.bottom_pipe.velocity_x = self.pipe_speed  # ปรับความเร็วของท่อ

class Pipe(Widget):
    velocity_x = NumericProperty(-5) # ความเร็วท่อ

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
        # vector
        self.velocity = Vector(self.velocity[0], self.velocity[1] + self.gravity)
        self.y += self.velocity[1]

        # ล็อกจุด
        if self.start_x == 0:
            self.start_x = self.x
            self.x = self.start_x  

        # กันหลุกขอบ
        if self.y < 0:
            self.y = 0
            self.velocity = (0, 0)

        # กันขอบบน
        if self.top > self.parent.height:
            self.top = self.parent.height
            self.velocity = (0, 0)

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