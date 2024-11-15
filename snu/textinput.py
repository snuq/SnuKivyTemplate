import re
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty, ColorProperty, ListProperty, AliasProperty
from kivy.uix.bubble import Bubble
from .navigation import Navigation
from kivy.lang.builder import Builder
Builder.load_string("""
<-NormalInput>:
    canvas.before:
        Color:
            rgba: self._current_background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.rounded]
        Color:
            rgba: self.background_border_color
        Line:
            width: self.background_border_width
            rounded_rectangle: (self.pos[0], self.pos[1], self.width, self.height, self.rounded)
        Color:
            rgba: (self.cursor_color if self.focus and not self._cursor_blink and int(self.x + self.padding[0]) <= self._cursor_visual_pos[0] <= int(self.x + self.width - self.padding[2]) else (0, 0, 0, 0))
        Rectangle:
            pos: self._cursor_visual_pos
            size: root.cursor_width, -self._cursor_visual_height
        Color:
            rgba: self.disabled_foreground_color if self.disabled else ((0, 0, 0, 0) if not self.text else self.foreground_color)
    canvas.after:
        Color:
            rgba: self.cursor_color if root._activated else (0, 0, 0, 0)
        Rectangle:  #underline
            pos: self.x + (self.rounded / 2) + (self.width * self.underline_pos * (1 - self._activated)), self.y
            size: (self.width - self.rounded) * self._activated, self._underline_size
        Color:
            rgba: self.hint_text_color if root.animate_hint or not self.text else (0, 0, 0, 0)
        Rectangle:  #hint text
            size: self._hint_label_size
            pos: self.x + self.padding[0], self.y + self.height - self._hint_label_size[1] - (self.height * .2 * (1 - self._activated_hint))
            texture: self._hint_label_texture if self._hint_label_texture else None
    _underline_size: max(1, app.button_scale / 10)
    padding: max(app.button_scale / 8, self.rounded), (self._hint_max_size * 0.3) + (app.button_scale / 8), max(app.button_scale / 8, self.rounded), app.button_scale / 8
    mipmap: True
    cursor_color: app.theme.text
    write_tab: False
    background_color: app.theme.input_background[:3]+[0.333]
    background_color_active: app.theme.input_background
    background_border_color: app.theme.text[:3]+[0.5]
    hint_text_color: app.theme.disabled_text
    disabled_foreground_color: 1,1,1,.75
    foreground_color: app.theme.text
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale

<FloatInput>:
    multiline: False
    write_tab: False

<IntegerInput>:
    multiline: False
    write_tab: False

<InputMenu>:
    canvas.before:
        Color:
            rgba: app.theme.menu_background
        BorderImage:
            display_border: [app.display_border, app.display_border, app.display_border, app.display_border]
            size: self.size
            pos: self.pos
            source: 'data/buttonflat.png'
    background_image: 'data/transparent.png'
    size_hint: None, None
    size: app.button_scale * 9, app.button_scale
    show_arrow: False
    BoxLayout:
        MenuButton:
            text: 'Select All'
            on_release: root.select_all()
        MenuButton:
            text: 'Cut'
            on_release: root.cut()
        MenuButton:
            text: 'Copy'
            on_release: root.copy()
        MenuButton:
            text: 'Paste'
            on_release: root.paste()
""")


class NormalInput(TextInput, Navigation):
    """Text input widget that adds a popup menu for normal text operations."""

    hint_text = StringProperty("Enter Text")
    underline_pos = NumericProperty(0.5)  #Horizontal position (percent) from where the underline will grow from
    activate_time = NumericProperty(0.2)  #Time in seconds for the animate in
    deactivate_time = NumericProperty(0.2)  #Time in seconds for the animate out
    background_color = ColorProperty((1, 1, 1, 0.5))
    background_color_active = ColorProperty((1, 1, 1, 1))  #Color that the background will fade to when the text input is focused
    background_border_color = ColorProperty((0, 0, 0, 0.5))  #Color of the border line
    background_border_width = NumericProperty(1)  #Thickness of the border line
    rounded = NumericProperty(4)  #Radius of rounded corners on background
    animate_hint = BooleanProperty(False)

    _activated = NumericProperty(0)
    _activated_hint = NumericProperty(0)
    _activate_animation = None
    _underline_size = NumericProperty(1)
    _current_background_color = ColorProperty()
    _hint_label = None
    _hint_max_size = NumericProperty(0)
    _hint_min_size = NumericProperty(0)
    def update_hint_label(self):
        if not self._hint_label:
            self._hint_label = Label(opacity=0, size_hint=(None, None), size=(0, 0))
            #self._hint_label.
        self._hint_label.color = 1, 1, 1, 1
        self._hint_label.text = self.hint_text
        self._hint_max_size = min(self.font_size, self.height * 0.5)
        self._hint_min_size = self._hint_max_size * 0.5
        target_range = self._hint_max_size - self._hint_min_size
        self._hint_label.font_size = self._hint_min_size + target_range * (1 - self._activated_hint)
        self._hint_label.texture_update()
        if self._hint_label._label.texture:
            self._hint_label_size = self._hint_label._label.texture.size
        return self._hint_label._label.texture
    _hint_label_texture = AliasProperty(update_hint_label, bind=('size', 'font_size', 'hint_text_color', 'hint_text', '_activated_hint'))
    _hint_label_size = ListProperty([1, 1])
    context_menu = BooleanProperty(True)
    long_press_time = NumericProperty(1)
    long_press_clock = None
    long_press_pos = None
    allow_mode = StringProperty()
    allow_negative = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_background_color = self.background_color

    def _show_cut_copy_paste(self, pos, win, parent_changed=False, mode='', pos_in_window=False, *l):
        return

    def on_navigation_activate(self):
        self.focus = not self.focus

    def on_touch_up(self, touch):
        if self.long_press_clock:
            self.long_press_clock.cancel()
            self.long_press_clock = None
        return super(NormalInput, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        if self.context_menu and not self.disabled:
            if self.collide_point(*touch.pos):
                pos = self.to_window(*touch.pos)
                self.long_press_clock = Clock.schedule_once(self.do_long_press, self.long_press_time)
                self.long_press_pos = pos
                if hasattr(touch, 'button'):
                    if touch.button == 'right':
                        app = App.get_running_app()
                        app.popup_bubble(self, pos)
                        return True
        return super(NormalInput, self).on_touch_down(touch)

    def do_long_press(self, *_):
        app = App.get_running_app()
        app.popup_bubble(self, self.long_press_pos)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        app = App.get_running_app()
        app.close_bubble()
        if keycode[0] == 27:
            self.focus = False
            return True
        if keycode[0] in [13, 271]:
            self.press_enter(self, self.text)
            if not self.multiline:
                self.focus = False
                return True
        super().keyboard_on_key_down(window, keycode, text, modifiers)

    def press_enter(self, instance, text):
        pass

    def on_focus(self, widget, is_focused):
        app = App.get_running_app()
        app.navigation_enabled = not self.focus
        if is_focused:
            self.activate()
        else:
            self.deactivate()

    def insert_text(self, substring, from_undo=False):
        if self.allow_mode.lower() == 'float':
            pat = re.compile('[^0-9]')
            if self.allow_negative:
                if '-' in substring:
                    substring = substring.replace('-', '')
                    if '-' in self.text:
                        self.text = self.text.replace('-', '')
                    else:
                        self.text = '-' + self.text
            if '.' in self.text:
                s = re.sub(pat, '', substring)
            else:
                s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        elif self.allow_mode.lower() in ['int', 'integer']:
            pat = re.compile('[^0-9]')
            if self.allow_negative:
                if '-' in substring:
                    substring = substring.replace('-', '')
                    if '-' in self.text:
                        self.text = self.text.replace('-', '')
                    else:
                        self.text = '-' + self.text
            s = re.sub(pat, '', substring)
        elif self.allow_mode.lower() in ['file', 'filename']:
            s = "".join(i for i in substring if i not in "\\/:*?<>|")
        elif self.allow_mode.lower() == 'url':
            s = "".join(i for i in substring if i in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -._~!'()*")
        elif self.allow_mode.lower() in ['hex', 'hexadecimal']:
            s = "".join(i for i in substring if i in "0123456789ABCDEFabcdef")
        else:
            s = substring
        return super().insert_text(s, from_undo=from_undo)

    def on_background_color(self, *_):
        self._current_background_color = self.background_color

    def stop_animation(self):
        if self._activate_animation:
            self._activate_animation.stop(self)
            self._activate_animation = None

    def activate(self):
        self.stop_animation()
        if self.animate_hint:
            activated_hint_target = 1
        else:
            activated_hint_target = 0
        self._activate_animation = Animation(_activated=1, _activated_hint=activated_hint_target, _current_background_color=self.background_color_active, duration=self.activate_time)
        self._activate_animation.start(self)

    def deactivate(self):
        self.stop_animation()
        if self.text and self.animate_hint:
            activated_hint_target = 1
        else:
            activated_hint_target = 0
        self._activate_animation = Animation(_activated=0, _activated_hint=activated_hint_target, _current_background_color=self.background_color, duration=self.deactivate_time)
        self._activate_animation.start(self)


class FloatInput(NormalInput):
    """Custom text input that only allows float numbers to be typed in.  Only allows numerals and one '.'"""

    hint_text = StringProperty("0.0")
    allow_negative = BooleanProperty(True)
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if self.allow_negative:
            if '-' in substring:
                substring = substring.replace('-', '')
                if '-' in self.text:
                    self.text = self.text.replace('-', '')
                else:
                    self.text = '-' + self.text
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class IntegerInput(NormalInput):
    """Custom text input that only allows numbers to be typed in."""

    hint_text = StringProperty("0")
    allow_negative = BooleanProperty(True)
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if self.allow_negative:
            if '-' in substring:
                substring = substring.replace('-', '')
                if '-' in self.text:
                    self.text = self.text.replace('-', '')
                else:
                    self.text = '-' + self.text
        s = re.sub(pat, '', substring)
        return super(IntegerInput, self).insert_text(s, from_undo=from_undo)


class InputMenu(Bubble):
    """Class for the text input right-click popup menu.  Includes basic text operations."""

    owner = ObjectProperty()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            app = App.get_running_app()
            app.close_bubble()
        else:
            super(InputMenu, self).on_touch_down(touch)

    def select_all(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.select_all()
            app.close_bubble()

    def cut(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.cut()
            app.close_bubble()

    def copy(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.copy()
            app.close_bubble()

    def paste(self, *_):
        if self.owner:
            app = App.get_running_app()
            self.owner.paste()
            app.close_bubble()
