from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen

class MenuScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class SharkyGoGame(Widget):
    shark = ObjectProperty(None)
    obstacle = ObjectProperty(None)
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(SharkyGoGame, self).__init__(**kwargs)
        self.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
        self.collision_sound = SoundLoader.load('assets/sounds/hit.wav')
        if self.background_music:
            self.background_music.loop = True
            self.background_music.play() 

    def update(self, dt):
        self.shark.move()
        self.obstacle.move()

        if self.shark.collide_widget(self.obstacle):
            if self.collision_sound:
                self.collision_sound.play()
            print("Game Over!")
            
        if self.obstacle.x < -50:
            self.score += 1
            self.obstacle.x = self.width
            if self.score % 5 == 0:
                self.change_level()
    
    def change_level(self):
        print("Harder!!!")

    def on_touch_down(self, touch):
        self.shark.velocity_y = 5

    def on_touch_up(self, touch):
        self.shark.velocity_y = -5

class SharkyGoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

class Shark(Widget):
    velocity_y = NumericProperty(0)

    def move(self):
        self.y += self.velocity_y

class Obstacle(Widget):
    velocity_x = NumericProperty(-5)

    def move(self):
        self.x += self.velocity_x

if __name__ == '__main__':
    SharkyGoApp().run()