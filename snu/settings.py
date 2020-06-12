from kivy.app import App
from kivy.uix.settings import SettingsWithNoMenu, SettingItem
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.compat import string_types, text_type
from .popup import NormalPopup, InputPopupContent

from kivy.lang.builder import Builder
Builder.load_string("""
<-SettingsPanel>:
    spacing: 5
    size_hint_y: None
    height: self.minimum_height

<-Settings>:
    canvas.before:
        Color:
            rgba: app.theme.background

        Rectangle:
            size: root.size
            pos: root.pos
        Color:
            rgba: app.theme.main_background
        Rectangle:
            size: root.size
            pos: root.pos
            source: 'data/mainbg.png'
    orientation: 'vertical'
    Header:
        NormalButton:
            text: 'Close Settings'
            on_release: app.close_settings()
        HeaderLabel:
            text: "Settings"

<-SettingItem>:
    size_hint: .25, None
    height: labellayout.texture_size[1] + dp(10)
    content: content

    BoxLayout:
        pos: root.pos
        Widget:
            size_hint_x: .2
        BoxLayout:
            canvas:
                Color:
                    rgba: 47 / 255., 167 / 255., 212 / 255., root.selected_alpha
                Rectangle:
                    pos: self.x, self.y + 1
                    size: self.size
                Color:
                    rgb: .2, .2, .2
                Rectangle:
                    pos: self.x, self.y - 2
                    size: self.width, 1
            Label:
                size_hint_x: .66
                id: labellayout
                markup: True
                text: u"{0}\\n[size=13sp]{1}[/size]".format(root.title or "", root.desc or "")
                font_size: '15sp'
                text_size: self.width - 32, None
                color: app.theme.text
            BoxLayout:
                id: content
                size_hint_x: .33
        Widget:
            size_hint_x: .2

<SettingAboutButton>:
    WideButton:
        text: "About This App"
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: app.about()

<AboutPopup>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, .75 * self._anim_alpha
        Rectangle:
            size: self._window.size if self._window else (0, 0)
        Color:
            rgba: app.theme.sidebar_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/panelbg.png'
    background_color: 1, 1, 1, 0
    background: 'data/transparent.png'
    separator_color: 1, 1, 1, .25
    title_size: app.text_scale * 1.25
    title_color: app.theme.header_text
    size_hint: .5, None
    height: self.width/2
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            Image:
                source: 'data/icon.png'
                size_hint_x: None
                size_hint_y: 1
                width: self.height
            Scroller:
                do_scroll_x: False
                ShortLabel:
                    size_hint_y: None
                    height: self.texture_size[1] + 20
                    text: app.about_text
        WideButton:
            id: button
            text: root.button_text
            on_release: root.close()

<SettingString>:
    size_hint_y: None
    Label:
        text: root.value or ''
        pos: root.pos
        font_size: '15sp'
        color: app.theme.text

<SettingBoolean>:
    true_text: 'On'
    false_text: 'Off'
    size_hint_y: None
    NormalToggle:
        size_hint_x: 1
        state: 'normal' if root.value == '0' else 'down'
        on_press: root.value = '0' if self.state == 'normal' else '1'
        text: root.true_text if root.value == '1' else root.false_text
""")


class SettingString(SettingItem):
    """String value in the settings screen.  Customizes the input popup"""

    popup = ObjectProperty(None, allownone=True)
    textinput = ObjectProperty(None)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def dismiss(self, *largs):
        if self.popup:
            self.popup.dismiss()
        app = App.get_running_app()
        if app.popup:
            app.popup = None
        self.popup = None

    def _validate(self, instance, answer):
        value = self.popup.content.ids['input'].text.strip()
        self.dismiss()
        if answer == 'yes':
            self.value = value

    def _create_popup(self, instance):
        content = InputPopupContent(text='', input_text=self.value)
        app = App.get_running_app()
        content.bind(on_answer=self._validate)
        self.popup = NormalPopup(title=self.title, content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5), auto_dismiss=True)
        app.popup = self.popup
        self.popup.open()


class SettingNumeric(SettingString):
    def _validate(self, instance, answer):
        # we know the type just by checking if there is a '.' in the original value
        is_float = '.' in str(self.value)
        value = self.popup.content.ids['input'].text
        self.dismiss()
        if answer == 'yes':
            try:
                if is_float:
                    self.value = text_type(float(value))
                else:
                    self.value = text_type(int(value))
            except ValueError:
                return


class AppSettings(SettingsWithNoMenu):
    """Expanded settings class to add new settings buttons and types."""

    def __init__(self, **kwargs):
        super(AppSettings, self).__init__(**kwargs)
        self.register_type('string', SettingString)
        self.register_type('numeric', SettingNumeric)
        self.register_type('aboutbutton', SettingAboutButton)


class SettingAboutButton(SettingItem):
    """Settings widget that opens an about dialog."""
    pass


class SettingsThemeButton(SettingItem):
    """Widget that opens the theme screen"""

    def show_theme(self):
        app = App.get_running_app()
        app.close_settings()
        app.show_theme()


class AboutPopup(Popup):
    """Basic popup message with a message and 'ok' button."""

    button_text = StringProperty('OK')

    def close(self, *_):
        app = App.get_running_app()
        app.popup.dismiss()
