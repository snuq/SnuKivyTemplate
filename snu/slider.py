from kivy.uix.slider import Slider
from kivy.clock import Clock
from .navigation import Navigation
from kivy.lang.builder import Builder
Builder.load_string("""
<-NormalSlider>:
    #:set sizing 18
    canvas:
        Color:
            rgba: app.theme.slider_background
        BorderImage:
            border: (0, sizing, 0, sizing)
            pos: self.pos
            size: self.size
            source: 'data/sliderbg.png'
        Color:
            rgba: app.theme.slider_grabber
        Rectangle:
            pos: (self.value_pos[0] - app.button_scale/4, self.center_y - app.button_scale/2)
            size: app.button_scale/2, app.button_scale
            source: 'data/buttonflat.png'
    size_hint_y: None
    height: app.button_scale
    min: -1
    max: 1
    value: 0
""")


class SpecialSlider(Slider):
    """Slider that adds a 'reset_value' function that is called on double-click.
    This function does not do anything by default, the user must bind a function to this function.

    Example in kvlang:
        SpecialSlider:
            reset_value: root.reset_function
    """

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            Clock.schedule_once(self.reset_value, 0.15)  #Need to delay this longer than self.scroll_timeout, or it wont work right...
            self.reset_value()
            return
        super(SpecialSlider, self).on_touch_down(touch)

    def reset_value(self, *_):
        pass


class NormalSlider(SpecialSlider, Navigation):
    def on_navigation_decrease(self):
        new_value = self.value - .1
        if new_value < self.min:
            self.value = self.min
        else:
            self.value = new_value

    def on_navigation_increase(self):
        new_value = self.value + .1
        if new_value > self.max:
            self.value = self.max
        else:
            self.value = new_value
