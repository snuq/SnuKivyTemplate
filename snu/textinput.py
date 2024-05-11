import re
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.bubble import Bubble
from .navigation import Navigation
from kivy.lang.builder import Builder
Builder.load_string("""
<-TextInput>:
    canvas.before:
        Color:
            rgba: self.background_color
        BorderImage:
            display_border: [app.display_border/2, app.display_border/2, app.display_border/2, app.display_border/2]
            border: self.border
            pos: self.pos[0] + 3, self.pos[1] + 3
            size: self.size[0] -6, self.size[1] - 6
            source: self.background_active if self.focus else (self.background_disabled_normal if self.disabled else self.background_normal)
        Color:
            rgba:
                (self.cursor_color
                if self.focus and not self._cursor_blink
                else (0, 0, 0, 0))
        Rectangle:
            pos: self._cursor_visual_pos
            size: root.cursor_width, -self._cursor_visual_height
        Color:
            rgba: self.disabled_foreground_color if self.disabled else (self.hint_text_color if not self.text else self.foreground_color)
    padding: app.display_padding

<NormalInput>:
    mipmap: True
    cursor_color: app.theme.text
    write_tab: False
    background_color: app.theme.input_background
    hint_text_color: app.theme.disabled_text
    disabled_foreground_color: 1,1,1,.75
    foreground_color: app.theme.text
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale

<FloatInput>:
    multiline: False
    write_tab: False
    background_color: app.theme.input_background
    disabled_foreground_color: 1,1,1,.75
    foreground_color: app.theme.text
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale

<IntegerInput>:
    multiline: False
    write_tab: False
    background_color: app.theme.input_background
    disabled_foreground_color: 1,1,1,.75
    foreground_color: app.theme.text
    size_hint_y: None
    height: app.button_scale
    font_size: app.text_scale

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

    context_menu = BooleanProperty(True)
    long_press_time = NumericProperty(1)
    long_press_clock = None
    long_press_pos = None
    allow_mode = StringProperty()
    allow_negative = BooleanProperty(True)

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
        if self.context_menu:
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

    def on_focus(self, *_):
        app = App.get_running_app()
        app.navigation_enabled = not self.focus

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


class FloatInput(NormalInput):
    """Custom text input that only allows float numbers to be typed in.  Only allows numerals and one '.'"""

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
