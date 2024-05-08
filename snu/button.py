from .navigation import Navigation
from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.modalview import ModalView
from kivy.lang.builder import Builder
Builder.load_string("""
<-Button,-ToggleButton>:
    state_image: self.background_normal if self.state == 'normal' else self.background_down
    disabled_image: self.background_disabled_normal if self.state == 'normal' else self.background_disabled_down
    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            display_border: [app.display_border, app.display_border, app.display_border, app.display_border]
            border: self.border
            pos: self.pos
            size: self.size
            source: self.disabled_image if self.disabled else self.state_image
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)

<ClickFade>:
    canvas:
        Color:
            rgba: app.theme.selected
        Rectangle:
            size: self.size
            pos: root.pos
    background: 'data/transparent.png'
    size_hint: None, None
    opacity: 0

<ButtonBase>:
    mipmap: True
    font_size: app.text_scale
    size_hint_y: None
    height: app.button_scale
    background_normal: 'data/button.png'
    background_down: 'data/button.png'
    background_disabled_down: 'data/button.png'
    background_disabled_normal: 'data/button.png'
    button_update: app.button_update

<NormalButton>:
    width: self.texture_size[0] + app.button_scale
    size_hint_x: None
    font_size: app.text_scale

<WideButton>:
    text_size: self.size
    halign: 'center'
    valign: 'middle'

<MenuButton>:
    menu: True
    size_hint_x: 1

<NormalMenuStarter>:
    canvas.after:
        Color:
            rgba: self.color
        Rectangle:
            pos: (root.pos[0]+root.width-(root.height/1.5)), root.pos[1]
            size: root.height/2, root.height
            source: 'data/menuarrows.png'
    menu: True
    size_hint_x: None
    width: self.texture_size[0] + (app.button_scale * 1.5)

<WideMenuStarter>:
    canvas.after:
        Color:
            rgba: self.color
        Rectangle:
            pos: (root.pos[0]+root.width-(root.height/1.5)), root.pos[1]
            size: root.height/2, root.height
            source: 'data/menuarrows.png'
    menu: True
    text_size: self.size
    halign: 'center'
    valign: 'middle'
    size_hint_x: 1

<NormalToggle>:
    toggle: True
    size_hint_x: None
    width: self.texture_size[0] + app.button_scale

<WideToggle>:
    toggle: True

<SettingsButton@NormalButton>:
    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            border: self.border
            pos: self.pos
            size: self.size
            source: 'data/settings.png'
    text: ''
    border: (0, 0, 0, 0)
    size_hint_x: None
    width: self.height
    background_normal: 'data/transparent.png'
    background_down: self.background_normal
    on_release: app.open_settings()

<NormalDropDown>:
    canvas.before:
        Color:
            rgba: app.theme.menu_background
        BorderImage:
            display_border: [app.display_border, app.display_border, app.display_border, app.display_border]
            size: root.width, root.height * root.show_percent
            pos: root.pos[0], root.pos[1] + (root.height * (1 - root.show_percent)) if root.invert else root.pos[1]
            source: 'data/buttonflat.png'
""")


class ClickFade(ModalView):
    animation = None

    def begin(self, mode='opacity'):
        app = App.get_running_app()
        self.opacity = 0

        if app.animations:
            if self.animation:
                self.animation.cancel(self)
            if mode == 'height':
                self.animation = Animation(opacity=1, duration=(app.animation_length / 4)) + Animation(height=0, pos=(self.pos[0], self.pos[1]+self.height), duration=(app.animation_length / 2))
            else:
                self.animation = Animation(opacity=1, duration=(app.animation_length / 4)) + Animation(opacity=0, duration=(app.animation_length / 2))
            self.animation.start(self)
            self.animation.bind(on_complete=self.finish_animation)
        else:
            self.finish_animation()

    def finish_animation(self, *_):
        self.animation = None
        try:
            self.parent.remove_widget(self)
        except:
            pass


class ButtonBase(Button, Navigation):
    """Button widget that includes theme options and a variety of small additions over a basic button."""

    warn = BooleanProperty(False)
    target_background = ListProperty()
    target_text = ListProperty()
    background_animation = ObjectProperty()
    text_animation = ObjectProperty()
    last_disabled = False
    menu = BooleanProperty(False)
    toggle = BooleanProperty(False)

    button_update = BooleanProperty()

    def __init__(self, **kwargs):
        self.background_animation = Animation()
        self.text_animation = Animation()
        app = App.get_running_app()
        self.background_color = app.theme.button_up
        self.target_background = self.background_color
        self.color = app.theme.button_text
        self.target_text = self.color
        super(ButtonBase, self).__init__(**kwargs)

    def on_button_update(self, *_):
        Clock.schedule_once(lambda x: self.set_color())

    def set_color(self, instant=False):
        app = App.get_running_app()
        if self.disabled:
            self.set_text(app.theme.button_disabled_text, instant=instant)
            self.set_background(app.theme.button_disabled, instant=instant)
        else:
            self.set_text(app.theme.button_text, instant=instant)
            if self.menu:
                if self.state == 'down':
                    self.set_background(app.theme.button_menu_down, instant=True)
                else:
                    self.set_background(app.theme.button_menu_up, instant=instant)
            elif self.toggle:
                if self.state == 'down':
                    self.set_background(app.theme.button_toggle_true, instant=instant)
                else:
                    self.set_background(app.theme.button_toggle_false, instant=instant)

            elif self.warn:
                if self.state == 'down':
                    self.set_background(app.theme.button_warn_down, instant=True)
                else:
                    self.set_background(app.theme.button_warn_up, instant=instant)
            else:
                if self.state == 'down':
                    self.set_background(app.theme.button_down, instant=True)
                else:
                    self.set_background(app.theme.button_up, instant=instant)

    def on_disabled(self, *_):
        self.set_color()

    def on_menu(self, *_):
        self.set_color(instant=True)

    def on_toggle(self, *_):
        self.set_color(instant=True)

    def on_warn(self, *_):
        self.set_color(instant=True)

    def on_state(self, *_):
        self.set_color()

    def set_background(self, color, instant=False):
        if self.target_background == color:
            return
        app = App.get_running_app()
        self.background_animation.stop(self)
        if app.animations and not instant:
            self.background_animation = Animation(background_color=color, duration=app.animation_length)
            self.background_animation.start(self)
        else:
            self.background_color = color
        self.target_background = color

    def set_text(self, color, instant=False):
        if self.target_text == color:
            return
        app = App.get_running_app()
        self.text_animation.stop(self)
        if app.animations and not instant:
            self.text_animation = Animation(color=color, duration=app.animation_length)
            self.text_animation.start(self)
        else:
            self.color = color
        self.target_text = color


class ToggleBase(ToggleButton, ButtonBase):
    """Basic toggle button widget"""
    pass


class NormalToggle(ToggleBase):
    pass


class WideToggle(ToggleBase):
    pass


class NormalButton(ButtonBase):
    """Basic button widget."""
    pass


class WideButton(ButtonBase):
    """Full width button widget."""
    pass


class MenuButton(ButtonBase):
    """Basic class for a drop-down menu button item."""
    pass


class NormalMenuStarter(ButtonBase):
    pass


class WideMenuStarter(ButtonBase):
    pass


class NormalDropDown(DropDown):
    """Dropdown menu class with some nice animations."""

    show_percent = NumericProperty(1)
    invert = BooleanProperty(False)
    basic_animation = BooleanProperty(False)

    def open(self, *args, **kwargs):
        if self.parent:
            self.dismiss()
            return
        app = App.get_running_app()
        super(NormalDropDown, self).open(*args, **kwargs)

        self.container.do_layout()
        self._reposition()
        if app.animations:
            if self.basic_animation:
                #Dont do fancy child opacity animation
                self.opacity = 0
                self.show_percent = 1
                anim = Animation(opacity=1, duration=app.animation_length)
                anim.start(self)
            else:
                #determine if we opened up or down
                attach_to_window = self.attach_to.to_window(*self.attach_to.pos)
                if attach_to_window[1] > self.pos[1]:
                    self.invert = True
                    children = reversed(self.container.children)
                else:
                    self.invert = False
                    children = self.container.children

                #Animate background
                self.opacity = 1
                self.show_percent = 0
                anim = Animation(show_percent=1, duration=app.animation_length)
                anim.start(self)

                if len(self.container.children) > 0:
                    item_delay = app.animation_length / len(self.container.children)
                else:
                    item_delay = 0

                for i, w in enumerate(children):
                    anim = (Animation(duration=i * item_delay) + Animation(opacity=1, duration=app.animation_length))
                    w.opacity = 0
                    anim.start(w)
        else:
            self.opacity = 1

    def dismiss(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            anim = Animation(opacity=0, duration=app.animation_length)
            anim.start(self)
            anim.bind(on_complete=self.finish_dismiss)
        else:
            self.finish_dismiss()

    def finish_dismiss(self, *_):
        super(NormalDropDown, self).dismiss()
