from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from .navigation import Navigation
from .roulettescroll import RouletteScrollEffect
from kivy.lang.builder import Builder
Builder.load_string("""
<SmoothSettingControl>:
    fit_mode: 'fill'
    size_hint_x: None

<SmoothSettingButton>:
    opacity: 0.25
    size_hint_x: None
    color: app.theme.button_text
    font_size: app.text_scale

<SmoothSetting>:
    canvas.before:
        Color:
            rgba: app.theme.slider_background
        RoundedRectangle:
            radius: [root.rounding]
            size: self.size
            pos: self.pos
        Color:
            rgba: 0, 0, 0, .1
        Line:
            width: 2
            rounded_rectangle: (self.x, self.y, self.width, self.height, root.rounding)
    orientation: 'horizontal'
    active: scrollerArea.active
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, root.gradient_transparency
            RoundedRectangle:
                radius: [root.rounding, 0.001, 0.001, root.rounding]
                pos: self.pos
                size: self.size
                source: 'data/gradient-left.png'
        pos: root.pos
        size_hint_x: None
        width: (root.width - scrollerArea.item_width) / 2
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, root.gradient_transparency
            RoundedRectangle:
                radius: [0.001, root.rounding, root.rounding, 0.001]
                pos: self.pos
                size: self.size
                source: 'data/gradient-right.png'
        pos: root.pos[0] + ((root.width + scrollerArea.item_width) / 2), root.pos[1]
        size_hint_x: None
        width: (root.width - scrollerArea.item_width) / 2

    SmoothSettingScroller:
        size_hint_x: None
        width: root.width - controlLeft.width - controlRight.width
        id: scrollerArea
        pos: (root.pos[0] + controlLeft.width, root.pos[1])
        content: root.content
        item_width: root.item_width if root.item_width is not None else root.height
        start_on: root.start_on
        scroll_distance: 1
        scroll_timeout: 10000
        bar_width: 0
        scroll_type: ['content']
        do_scroll_x: True
        do_scroll_y: False
        BoxLayout:
            id: fillArea
            padding: (self.parent.width - scrollerArea.item_width) / 2, 0
            size_hint_x: None
            width: self.parent.width + (scrollerArea.item_width * (len(self.parent.content) - 1))

    SmoothSettingControl:
        id: controlLeft
        color: app.theme.button_text
        repeat_length: root.repeat_length
        repeat_minimum: root.repeat_minimum
        scroller: scrollerArea
        direction: 'left'
        source: root.left_image
        width: root.control_width if root.control_width is not None else root.height
        opacity: 0 if self.width == 0 else 1
        disabled: True if self.width == 0 else False
        pos: root.pos

    SmoothSettingControl:
        id: controlRight
        color: app.theme.button_text
        repeat_length: root.repeat_length
        repeat_minimum: root.repeat_minimum
        scroller: scrollerArea
        direction: 'right'
        source: root.right_image
        width: root.control_width if root.control_width is not None else root.height
        opacity: 0 if self.width == 0 else 1
        disabled: True if self.width == 0 else False
        pos: root.pos[0] + root.width - self.width, root.pos[1]
""")


class SmoothSettingButton(Label):
    pass


class SmoothSettingControl(Image):
    scroller = ObjectProperty()
    direction = StringProperty('left')
    repeater = ObjectProperty(allownone=True)
    repeat_length = NumericProperty(1)
    repeat_minimum = NumericProperty(0.1)
    repeat_length_current = 1

    def on_touch_down(self, touch):
        if self.disabled:
            return
        if self.collide_point(*touch.pos):
            self.repeat_length_current = self.repeat_length
            touch.grab(self)
            self.scroll_repeat()

    def scroll_repeat(self, *_):
        if self.repeat_length_current > self.repeat_minimum:
            self.repeat_length_current = self.repeat_length_current / 2
        self.scroll_segment()
        self.repeater = Clock.schedule_once(self.scroll_repeat, self.repeat_length_current)

    def scroll_segment(self, *_):
        if self.direction == 'left':
            self.scroller.scroll_left()
        else:
            self.scroller.scroll_right()

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.repeater.cancel()
            touch.ungrab(self)


class SmoothSetting(FloatLayout, Navigation):
    rounding = NumericProperty(10)
    gradient_transparency = NumericProperty(0.5)
    content = ListProperty()
    repeat_length = NumericProperty(1)
    repeat_minimum = NumericProperty(0.1)
    left_image = StringProperty('data/left.png')
    right_image = StringProperty('data/right.png')
    control_width = NumericProperty(None)
    item_width = NumericProperty(None)
    start_on = NumericProperty(0)
    active = NumericProperty(0)

    def scroll_to_element(self, index, instant=False):
        Clock.schedule_once(lambda x: self.ids.scrollerArea.scroll_to_element(index, instant=instant))

    def on_navigation_decrease(self):
        self.ids.scrollerArea.scroll_left()

    def on_navigation_increase(self):
        self.ids.scrollerArea.scroll_right()

    def on_active(self, *_):
        pass


class SmoothSettingScroller(ScrollView):
    content = ListProperty()
    not_selected = NumericProperty(0.25)
    active = NumericProperty(0)
    scroll_anim = ObjectProperty(allownone=True)
    item_width = NumericProperty(40)
    start_on = NumericProperty(0)

    def cancel_anim(self):
        if self.scroll_anim is not None:
            self.scroll_anim.stop(self)
            self.scroll_anim = None

    def scroll_left(self):
        self.scroll_to_element(self.active - 1)

    def scroll_right(self):
        self.scroll_to_element(self.active + 1)

    def scroll_to_element(self, index, instant=False):
        divisors = len(self.content) - 1
        self.cancel_anim()
        scroll_to_x = index / divisors
        if scroll_to_x < 0:
            scroll_to_x = 0
        elif scroll_to_x > 1:
            scroll_to_x = 1
        if instant:
            self.scroll_x = scroll_to_x
        else:
            self.scroll_anim = Animation(scroll_x=scroll_to_x, duration=0.1)
            self.scroll_anim.start(self)

    def on_content(self, *_):
        self.populate_buttons()
        self.scroll_to_element(self.start_on, instant=True)
        self.on_active()

    def populate_buttons(self):
        fill_area = self.children[0]
        fill_area.clear_widgets()
        for element in self.content:
            button = SmoothSettingButton(text=element, width=self.item_width)
            self.bind(item_width=button.setter('width'))
            fill_area.add_widget(button)

    def on_item_width(self, *_):
        self.set_scroll_effect()

    def on_parent(self, *_):
        self.set_scroll_effect()

    def set_scroll_effect(self):
        self.effect_x = RouletteScrollEffect(anchor=self.item_width, interval=self.item_width)

    def on_scroll_x(self, *_):
        divisors = len(self.content) - 1
        self.active = round(self.scroll_x * divisors)

    def on_active(self, *_):
        divisors = len(self.content)
        for index, child in enumerate(self.children[0].children):
            if (divisors - index - 1) != self.active:
                child.opacity = self.not_selected
            else:
                child.opacity = 1
