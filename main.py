from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import random

class MenuScreen(Screen):
    def on_enter(self):
        if not hasattr(self, 'background_music'):
            self.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
            if self.background_music:
                self.background_music.loop = True
                self.background_music.play()

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
    game_over = False #จนกว่าจะจบ

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collision_sound = SoundLoader.load('assets/sounds/hitcute.mp3')

    def update(self, dt):
        if self.game_over:
            return #จบแล้วพอ อย่ายื้อ เอื้อ เจ็บ

        self.shark.move()
        self.top_pipe.move()
        self.bottom_pipe.move()

        if self.shark.y <= 0 or self.shark.top >= self.height:
            self.end_game()#เรียกฟังก์ชันจบเกมตอนชนบนล่าง

        if self.shark.collide_widget(self.top_pipe) or self.shark.collide_widget(self.bottom_pipe):
            self.end_game()#เรียกฟังก์ชันจบเกมชนobject

        if not self.pipe_passed and self.shark.x > self.top_pipe.x + self.top_pipe.width:
            self.score += 1
            self.pipe_passed = True#ป้องกันนับซ้ำหลังผ่านท่อ

        if self.top_pipe.x < -50:
            self.reset_pipes()
            if self.score % 50 == 0:
                print("Harder!!!")

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart_game()
        else:
            self.shark.jump()

    def restart_game(self):
        self.score = 0
        self.game_over = False
        self.shark.y = self.height / 2  # Reset shark position
        self.shark.velocity = Vector(0, 0)  # Reset velocity
        self.reset_pipes()
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # Resume the game loop


    def end_game(self):
        self.game_over = True
        print("Game Over!")
        if self.collision_sound:
            self.collision_sound.play()
        Clock.unschedule(self.update)

    def reset_pipes(self):
        gap = 180 #ระยะห่างท่อ
        min_height = 50
        max_height = self.height - gap - min_height
        
        pipe_height = random.randint(min_height, max_height)

        self.top_pipe.x = self.width
        self.bottom_pipe.y = 0 #ท่อบน
        self.bottom_pipe.height = pipe_height

        self.bottom_pipe.x = self.width
        self.top_pipe.y = pipe_height + gap
        self.top_pipe.height = self.height - (pipe_height + gap) #ท่อล่าง

        self.pipe_passed = False#reset คะแนน

class Shark(Widget):
    velocity = ReferenceListProperty(NumericProperty(0), NumericProperty(0))
    gravity = -0.3
    jump_force = 7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.start_x = 0 #กำหนดจุดเริ่ม

    def move(self):
        #vector
        self.velocity = Vector(self.velocity[0], self.velocity[1] + self.gravity)
        self.y += self.velocity[1]

        #ล็อกจุด
        if self.start_x == 0:
            self.start_x = self.x
            self.x = self.start_x  

        #กันหลุกขอบ
        if self.y < 0:
            self.y = 0
            self.velocity = (0, 0)

        #กันขอบบน
        if self.top > self.parent.height:
            self.top = self.parent.height
            self.velocity = (0, 0)

    def jump(self):
        self.velocity = Vector(0, self.jump_force)
        self.jump_sound = SoundLoader.load('assets/sounds/jump.mp3')
        self.jump_sound.play()

class Pipe(Widget):
    velocity_x = NumericProperty(-5)

    def move(self):
        self.x += self.velocity_x

class SharkyGoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    SharkyGoApp().run()