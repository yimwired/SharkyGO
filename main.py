from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window

class SharkyGoGame(Widget):
    shark = ObjectProperty(None)

    def update(self, dt):
        self.shark.move()

    def on_touch_down(self, touch):
        self.shark.velocity_y = 5

    def on_touch_up(self, touch):
        self.shark.velocity_y = -5

class SharkyGoApp(App):
    def build(self):
        game = SharkyGoGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

class Shark(Widget):
    velocity_y = NumericProperty(0)

    def move(self):
        self.y += self.velocity_y

if __name__ == '__main__':
    SharkyGoApp().run()