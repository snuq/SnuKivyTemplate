from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
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

<-TickerLabel>:
    canvas.before:
        StencilPush
        Rectangle:
            pos: self.pos
            size: self.size
        StencilUse
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: self.x - self.ticker_offset, self.center_y - self.texture_size[1] / 2
    canvas.after:
        StencilUnUse
        Rectangle:
            pos: self.pos
            size: self.size
        StencilPop
    mipmap: True
    color: app.theme.text
    font_size: app.text_scale
    size_hint_y: None
    height: app.button_scale

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


class TickerLabel(Label):
    """Label that will scroll a line of text back and forth if it is longer than the widget size"""
    ticker_delay = NumericProperty(1.5)  #delay in seconds before ticker starts, also is pause before scrolling back
    ticker_amount = NumericProperty(0.5)  #pixels to scroll by on each tick, can be less than 1
    ticker_transition = StringProperty('in_out_sine')  #type of animation to be used, try 'linear' also
    ticker_offset = NumericProperty(0)
    ticker_animate = ObjectProperty(allownone=True)
    ticker_delayer = ObjectProperty(allownone=True)

    def on_text(self, *_):
        self.reset_ticker()

    def on_size(self, *_):
        self.reset_ticker()

    def reset_ticker(self):
        self.stop_animate()
        if self.ticker_delayer:
            self.ticker_delayer.cancel()
            self.ticker_delayer = None
        self.ticker_delayer = Clock.schedule_once(self.setup_animate, self.ticker_delay)

    def stop_animate(self, *_):
        if self.ticker_animate:
            self.ticker_animate.cancel(self)
            self.ticker_animate = None
        self.ticker_offset = 0

    def setup_animate(self, *_):
        if not self.texture:
            return
        if self.texture.size[0] > self.width:
            self.ticker_offset = 0
            ticker_per_tick = (self.texture_size[0] - self.width) / self.ticker_amount
            ticker_time = ticker_per_tick / 100
            self.ticker_animate = Animation(ticker_offset=self.texture.width - self.width, duration=ticker_time, t=self.ticker_transition) + Animation(duration=self.ticker_delay) + Animation(ticker_offset=0, duration=ticker_time, t=self.ticker_transition) + Animation(duration=self.ticker_delay)
            self.ticker_animate.repeat = True
            self.ticker_animate.start(self)