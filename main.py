from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window

class SharkyGoGame(Widget):
    def update(self, dt):
        print("Waiting for the game to start...")

class SharkyGoApp(App):
    def build(self):
        game = SharkyGoGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    SharkyGoApp().run()