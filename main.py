# main.py
from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ListProperty
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation

import random

class MenuScreen(Screen):
    volume = NumericProperty(0.5)
    background_music = None
    music_paused = BooleanProperty(False)
    scale = NumericProperty(1)  # เพิ่ม property สำหรับการขยายขนาด

    def animate_title(self, instance):
        # สร้าง Animation เพื่อปรับ scale
        anim = Animation(scale=1.1, duration=1) + Animation(scale=1, duration=1)
        anim.repeat = True
        anim.start(self)

    def on_enter(self):
        if MenuScreen.background_music is None:
            MenuScreen.background_music = SoundLoader.load('assets/sounds/BackgroundMermaid.mp3')
            if MenuScreen.background_music:
                MenuScreen.background_music.loop = True
                MenuScreen.background_music.volume = self.volume
                MenuScreen.background_music.play()
        else:
            # ถ้ามีเพลงเล่นอยู่แล้ว ให้ปรับระดับเสียงโดยไม่ต้องโหลดซ้ำ
            MenuScreen.background_music.volume = self.volume
            if not self.music_paused:  # ตรวจสอบสถานะของเพลง
                MenuScreen.background_music.play()

    def adjust_volume(self, value):
        self.volume = value
        if MenuScreen.background_music:
            MenuScreen.background_music.volume = value
    
    # ส่งค่า volume ไปยัง GameScreen
        game_screen = self.manager.get_screen('game')
        if game_screen and hasattr(game_screen.ids, 'game'):  # ตรวจสอบว่า game มีอยู่ใน ids หรือไม่
            game_screen.ids.game.adjust_epic_music_volume(value)

    def toggle_music(self, instance):
        if MenuScreen.background_music:
            if MenuScreen.background_music.state == 'play':
                MenuScreen.background_music.stop()  # หยุดเสียงเพลง
                self.music_paused = True
                instance.background_normal = 'assets/images/play.png'  # เปลี่ยนรูปเมื่อปิดเสียง
                instance.background_down = 'assets/images/mute.png'

                game_screen = self.manager.get_screen('game')
                if game_screen and hasattr(game_screen.ids, 'game'):
                    if game_screen.ids.game.Epic_music:
                        game_screen.ids.game.Epic_music.stop()
            else:
                MenuScreen.background_music.play()  # เล่นเสียงเพลง
                self.music_paused = False

class GameScreen(Screen):
    def on_enter(self):
        self.game = self.ids.game
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

class PipePair(Widget):
    velocity_x = NumericProperty(-5)
    passed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.top_pipe = Pipe()
        self.bottom_pipe = Pipe()
        self.add_widget(self.top_pipe)
        self.add_widget(self.bottom_pipe)
        self.gap = 200
        self.reset()
    def reset(self):
        min_height = 50
        parent_height = self.parent.height if self.parent else 600
        max_height = parent_height - self.gap - min_height

        # ตรวจสอบว่า max_height ต้องมากกว่า min_height
        if max_height < min_height:
            max_height = min_height + 10  # ปรับค่า max_height ให้มากกว่า min_height

        pipe_height = random.randint(min_height, max_height)

        self.bottom_pipe.size = (100, pipe_height)
        self.bottom_pipe.pos = (self.x, 0)

        top_pipe_height = parent_height - (pipe_height + self.gap)
        self.top_pipe.size = (100, top_pipe_height)
        self.top_pipe.pos = (self.x, pipe_height + self.gap)

        self.x = self.parent.width if self.parent else 0

    def move(self):
        self.x += self.velocity_x
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

class SharkyGoGame(Widget):
    shark = ObjectProperty(None)
    score = NumericProperty(0)
    game_over = False
    pipe_speed = NumericProperty(-5)
    speed_boosted_30 = BooleanProperty(False)
    speed_boosted_50 = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
        self.volume = 0.5
        self.collision_sound = SoundLoader.load('assets/sounds/hitcute.mp3')
        self.Epic_music = SoundLoader.load('assets/sounds/BackgroundEpic.mp3')
        
        self.background = Image(source='assets/images/background.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        self.pipes = []
        self.spawn_event = None
        self.start_spawning_pipes()

    def start_spawning_pipes(self):
        if self.spawn_event is not None:
            self.spawn_event.cancel()
        interval = self.calculate_spawn_interval()
        self.spawn_event = Clock.schedule_interval(self.spawn_pipes, interval)

    def calculate_spawn_interval(self):
        desired_spacing = 400
        speed = abs(self.pipe_speed)
        return desired_spacing / (speed * 60)

    def on_pipe_speed(self, instance, value):
        self.start_spawning_pipes()

    def spawn_pipes(self, dt):
        pipe_pair = PipePair()
        pipe_pair.velocity_x = self.pipe_speed
        # ตั้งค่าภาพท่อตามพื้นหลังปัจจุบัน
        if self.speed_boosted_50:
            pipe_pair.top_pipe.source = 'assets/images/iceRotate.png'
            pipe_pair.bottom_pipe.source = 'assets/images/ice.png'
        elif self.speed_boosted_30:
            pipe_pair.top_pipe.source = 'assets/images/rockRotate.png'
            pipe_pair.bottom_pipe.source = 'assets/images/rock.png'
        else:
            pipe_pair.top_pipe.source = 'assets/images/kelpRotate.png'
            pipe_pair.bottom_pipe.source = 'assets/images/kelp.png'
        self.add_widget(pipe_pair)
        self.pipes.append(pipe_pair)
        pipe_pair.reset()

    def adjust_epic_music_volume(self, volume):
        self.volume = volume
        if self.Epic_music:
            self.Epic_music.volume = volume

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

        for pipe_pair in self.pipes[:]:
            pipe_pair.move()

            if pipe_pair.x < -pipe_pair.top_pipe.width:
                self.remove_widget(pipe_pair)
                self.pipes.remove(pipe_pair)
                continue

            if self.shark.collide_widget(pipe_pair.top_pipe) or self.shark.collide_widget(pipe_pair.bottom_pipe):
                self.end_game()

            if not pipe_pair.passed and self.shark.x > pipe_pair.x + pipe_pair.top_pipe.width:
                self.score += 5
                pipe_pair.passed = True

        if self.score >= 10 and not self.speed_boosted_30: # สร้างเงื่อนไขให้มีการเช็คครั้งเดียว
            self.pipe_speed -= 2  # ท่อเคลื่อนที่เร็วขึ้น
            self.change_background('assets/images/new_background.png')
            self.speed_boosted_30 = True
            print("Harder!!!")

        if self.score >= 20 and not self.speed_boosted_50: # สร้างเงื่อนไขให้มีการเช็คครั้งเดียว
            self.pipe_speed -= 2.5  # ท่อเร็วขึ้นอีก
            self.change_background('assets/images/new_background2.png')
            menu_screen = self.parent.parent.get_screen('menu')
            if menu_screen and not menu_screen.music_paused:  # ตรวจสอบสถานะ music_paused
                if self.Epic_music:
                    self.Epic_music.play()
            self.speed_boosted_50 = True
            MenuScreen.background_music.stop()
            print("God Mode!!!")

    def change_background(self, new_background):
        self.background.source = new_background
        self.background.reload()
        # อัปเดตภาพท่อที่มีอยู่
        for pipe_pair in self.pipes:
            if self.speed_boosted_50:
                pipe_pair.top_pipe.source = 'assets/images/iceRotate.png'
                pipe_pair.bottom_pipe.source = 'assets/images/ice.png'
            elif self.speed_boosted_30:
                pipe_pair.top_pipe.source = 'assets/images/rockRotate.png'
                pipe_pair.bottom_pipe.source = 'assets/images/rock.png'
            else:
                pipe_pair.top_pipe.source = 'assets/images/kelpRotate.png'
                pipe_pair.bottom_pipe.source = 'assets/images/kelp.png'

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart_game()
        else:
            self.shark.jump()

    def restart_game(self):
        self.score = 0
        self.game_over = False
        self.pipe_speed = -5 # ความเร็วท่อ Begin
        self.speed_boosted_30 = False # รีความเร็วท่อ
        self.speed_boosted_50 = False # รีความเร็วท่อ

        if self.Epic_music:
            self.Epic_music.stop()

        self.change_background('assets/images/background.png')

        menu_screen = self.parent.parent.get_screen('menu')
        if menu_screen and menu_screen.background_music:
            if menu_screen.background_music.state == 'stop' and not menu_screen.music_paused:
                menu_screen.background_music.play()
            elif menu_screen.background_music.state == 'play':
                # เพลงกำลังเล่นอยู่แล้ว ไม่ต้องทำอะไร
                pass

        self.shark.y = self.height / 2  # รีน้องฉลาม
        self.shark.velocity = Vector(0, 0)  # รีความเร็ว
        # ลบท่อทั้งหมด
        for pipe_pair in self.pipes:
            self.remove_widget(pipe_pair)
        self.pipes = []
        self.start_spawning_pipes()
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

class Pipe(Image):
    velocity_x = NumericProperty(-5)  # ความเร็วท่อ

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
        # vector
        self.velocity = Vector(self.velocity[0], self.velocity[1] + self.gravity)
        self.y += self.velocity[1]

        # ล็อกจุด
        if self.start_x == 0:
            self.start_x = self.x
            self.x = self.start_x  

        # กันหลุดขอบ
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