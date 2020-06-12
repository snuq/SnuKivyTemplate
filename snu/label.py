from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.lang.builder import Builder
Builder.load_string("""
<NormalLabel>:
    mipmap: True
    color: app.theme.text
    font_size: app.text_scale
    size_hint_y: None
    height: app.button_scale

<ShortLabel>:
    shorten: True
    shorten_from: 'right'
    size_hint_x: 1
    size_hint_max_x: self.texture_size[0] + 20

<LeftNormalLabel>:
    shorten: True
    shorten_from: 'right'
    text_size: self.size
    halign: 'left'
    valign: 'middle'

<InfoLabel>:
    canvas.before:
        Color:
            rgba: root.bgcolor
        Rectangle:
            pos: self.pos
            size: self.size
    mipmap: True
    text: app.infotext
    color: app.theme.info_text

<HeaderLabel@Label>:
    mipmap: True
    color: app.theme.header_text
    font_size: int(app.text_scale * 1.5)
    size_hint_y: None
    height: app.button_scale
    bold: True
""")


class NormalLabel(Label):
    """Basic label widget"""
    pass


class ShortLabel(NormalLabel):
    """Label widget that will remain the minimum width to still display its text"""
    pass


class LeftNormalLabel(NormalLabel):
    """Label widget that displays text left-justified"""
    pass


class InfoLabel(ShortLabel):
    """Special label widget that automatically displays a message from the app class and blinks when the text is changed."""

    bgcolor = ListProperty([1, 1, 0, 0])
    blinker = ObjectProperty()

    def on_text(self, instance, text):
        del instance
        app = App.get_running_app()
        if self.blinker:
            self.stop_blinking()
        if text:
            no_bg = [.5, .5, .5, 0]
            yes_bg = app.theme.info_background
            self.blinker = Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33) + Animation(bgcolor=yes_bg, duration=0.33) + Animation(bgcolor=no_bg, duration=0.33)
            self.blinker.start(self)

    def stop_blinking(self, *_):
        if self.blinker:
            self.blinker.cancel(self)
        self.bgcolor = [1, 1, 0, 0]

