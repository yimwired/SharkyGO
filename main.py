from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

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
    obstacle = ObjectProperty(None)
    score = NumericProperty(0)
    game_over = False #จนกว่าจะจบ

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collision_sound = SoundLoader.load('assets/sounds/hitcute.mp3')

    def update(self, dt):
        if self.game_over:
            return #จบแล้วพอ อย่ายื้อ เอื้อ เจ็บ

        self.shark.move()
        self.obstacle.move()

        if self.shark.y <= 0 or self.shark.top >= self.height:
            self.end_game()#เรียกฟังก์ชันจบเกมตอนชนบนล่าง

        if self.shark.collide_widget(self.obstacle):
            self.end_game()#เรียกฟังก์ชันจบเกมชนobject

        if self.obstacle.x < -50:
            self.score += 1
            self.obstacle.x = self.width
            if self.score % 50 == 0:
                print("Harder!!!")

    def on_touch_down(self, touch):
        if not self.game_over:
            self.shark.jump()

    def end_game(self):
        self.game_over = True
        print("Game Over!")
        if self.collision_sound:
            self.collision_sound.play()
        Clock.unschedule(self.update)

class Shark(Widget):
    velocity = ReferenceListProperty(NumericProperty(0), NumericProperty(0))
    gravity = -0.3
    jump_force = 7.2

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
        self.jump_sound = SoundLoader.load('assets/sounds/hitcute.mp3')
        self.jump_sound.play()

class Obstacle(Widget):
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