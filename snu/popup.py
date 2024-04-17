from kivy.app import App
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.lang.builder import Builder
Builder.load_string("""
<NormalPopup>:
    background_color: app.theme.menu_background
    background: 'data/panelbg.png'
    separator_color: 1, 1, 1, .25
    title_size: app.text_scale * 1.25
    title_color: app.theme.header_text

<NormalPopupPre2.0>:
    canvas:
        Color:
            rgba: 0, 0, 0, .75 * self._anim_alpha
        Rectangle:
            size: self._window.size if self._window else (0, 0)
        Color:
            rgba: app.theme.menu_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/panelbg.png'
    background_color: 1, 1, 1, 0
    background: 'data/transparent.png'
    separator_color: 1, 1, 1, .25
    title_size: app.text_scale * 1.25
    title_color: app.theme.header_text

<MessagePopupContent>:
    cols:1
    NormalLabel:
        text_size: self.size
        size_hint_y: 1
        valign: 'top'
        text: root.text
    GridLayout:
        cols:1
        size_hint_y: None
        height: app.button_scale
        WideButton:
            id: button
            text: root.button_text
            on_release: root.close()

<InputPopupContent>:
    cols:1
    NormalLabel:
        text_size: self.size
        size_hint_y: 1
        valign: 'top'
        text: root.text
    NormalInput:
        id: input
        allow_mode: root.input_allow_mode
        multiline: False
        hint_text: root.hint
        text: root.input_text
        on_text: root.input_text = self.text
        focus: True
    GridLayout:
        cols: 2
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: 'OK'
            on_release: root.dispatch('on_answer','yes')
        WideButton:
            text: 'Cancel'
            on_release: root.dispatch('on_answer', 'no')

<ConfirmPopupContent>:
    cols:1
    NormalLabel:
        text_size: self.size
        size_hint_y: 1
        valign: 'top'
        text: root.text
    GridLayout:
        cols: 2
        size_hint_y: None
        height: app.button_scale
        WideButton:
            text: root.yes_text
            on_release: root.dispatch('on_answer','yes')
            warn: root.warn_yes
        WideButton:
            text: root.no_text
            on_release: root.dispatch('on_answer', 'no')
            warn: root.warn_no
""")


class NormalPopup(Popup):
    """Popup widget that adds open and close animations."""

    def open(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            self.opacity = 0
            height = self.height
            self.height = 4 * self.height
            anim = Animation(opacity=1, height=height, duration=app.animation_length)
            anim.start(self)
        else:
            self.opacity = 1
        super(NormalPopup, self).open(*args, **kwargs)

    def dismiss(self, *args, **kwargs):
        app = App.get_running_app()
        if app.animations:
            anim = Animation(opacity=0, height=0, duration=app.animation_length)
            anim.start(self)
            anim.bind(on_complete=self.finish_dismiss)
        else:
            super(NormalPopup, self).dismiss()

    def finish_dismiss(self, *_):
        super(NormalPopup, self).dismiss()


class MessagePopupContent(GridLayout):
    """Basic popup message with a message and 'ok' button."""

    button_text = StringProperty('OK')
    text = StringProperty()
    data = ObjectProperty()  #Generic variable that can store data to be passed in/out of popup

    def close(self, *_):
        app = App.get_running_app()
        app.popup.dismiss()


class InputPopupContent(GridLayout):
    """Basic text input popup message.  Calls 'on_answer' when either button is clicked."""

    input_allow_mode = StringProperty()
    input_text = StringProperty()
    text = StringProperty()  #Text that the user has input
    hint = StringProperty()  #Grayed-out hint text in the input field
    data = ObjectProperty()  #Generic variable that can store data to be passed in/out of popup

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(InputPopupContent, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass


class ConfirmPopupContent(GridLayout):
    """Basic Yes/No popup message.  Calls 'on_answer' when either button is clicked."""

    text = StringProperty()
    yes_text = StringProperty('Yes')
    no_text = StringProperty('No')
    warn_yes = BooleanProperty(False)
    warn_no = BooleanProperty(False)
    data = ObjectProperty()  #Generic variable that can store data to be passed in/out of popup

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(ConfirmPopupContent, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass
