import os
from kivy.app import App
from kivy.uix.settings import SettingsWithNoMenu, SettingTitle
from kivy.uix.settings import SettingItem as SettingItemOriginal
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.compat import text_type
from .scrollview import Scroller
from .button import WideButton, WideToggle
from .popup import NormalPopup, InputPopupContent
from .filebrowser import FileBrowser
from .navigation import Navigation

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
        HeaderLabel:
            text: "Settings"
        NormalButton:
            text: 'Close'
            on_release: app.close_settings()

<-SettingItem>:
    label_size_hint_x: 0.66
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
                size_hint_x: max(root.label_size_hint_x, 0.001)
                id: labellayout
                markup: True
                text: u"{0}\\n[size=13sp]{1}[/size]".format(root.title or "", root.desc or "")
                font_size: '15sp'
                text_size: self.width - 32, None
                color: app.theme.text
            BoxLayout:
                id: content
                size_hint_x: 1 - root.label_size_hint_x
        Widget:
            size_hint_x: .2

<SettingAboutButton>:
    label_size_hint_x: 0
    WideButton:
        text: "About This App"
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: app.about()

<AboutPopup>:
    background_color: app.theme.menu_background
    background: 'data/panelbg.png'
    separator_color: 1, 1, 1, .25
    title_size: app.text_scale * 1.25
    title_color: app.theme.header_text
    title: app.about_title
    size_hint: app.popup_size_hint_x, None
    height: app.button_scale * 5
    BoxLayout:
        orientation: 'vertical'
        Scroller:
            do_scroll_x: False
            NormalLabel:
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1] + 20
                text: app.about_text
        WideButton:
            id: button
            text: root.button_text
            on_release: root.close()

<-SettingTitle>:
    size_hint_y: None
    height: max(dp(20), self.texture_size[1] + dp(40))
    color: (.9, .9, .9, 1)
    font_size: '15sp'
    canvas:
        Color:
            rgb: .2, .2, .2
        Rectangle:
            pos: self.x, self.y - 2
            size: self.width, 1
    Label:
        padding: app.button_scale, 0
        size_hint: None, None
        size: root.size
        color: app.theme.text
        text: root.title
        text_size: self.size
        halign: 'left'
        valign: 'bottom'
        pos: root.pos
        font_size: '15sp'

<SettingString>:
    Label:
        text: root.value or ''
        pos: root.pos
        font_size: '15sp'
        color: app.theme.text

<SettingPath>:
    Label:
        text: root.value or ''
        pos: root.pos
        font_size: '15sp'
        color: app.theme.text

<SettingOptions>:
    Label:
        text: root.value or ''
        pos: root.pos
        font_size: '15sp'
        color: app.theme.text

<SettingBoolean>:
    true_text: 'On'
    false_text: 'Off'
    NormalToggle:
        size_hint_x: 1
        state: 'normal' if root.value == '0' else 'down'
        on_press: root.value = '0' if self.state == 'normal' else '1'
        text: root.true_text if root.value == '1' else root.false_text
""")


class SettingItem(SettingItemOriginal):
    label_size_hint_x = NumericProperty(0.66)


class SettingOptions(SettingItem, Navigation):
    """Options value in the settings screen.  Customizes the input popup"""

    options = ListProperty([])
    popup = ObjectProperty(None, allownone=True)

    def on_navigation_activate(self):
        self._create_popup(self)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def _dismiss(self, *_):
        app = App.get_running_app()
        if app.popup:
            app.popup.dismiss()

    def _set_option(self, instance):
        self.value = instance.text
        self._dismiss()

    def _create_popup(self, instance):
        app = App.get_running_app()
        if app.popup:
            app.popup.dismiss()
        content = BoxLayout(orientation='vertical')
        scroller = Scroller()
        content.add_widget(scroller)
        options_holder = BoxLayout(orientation='vertical', size_hint_y=None, height=len(self.options) * app.button_scale)
        for option in self.options:
            button = WideToggle(text=option)
            if self.value == option:
                button.state = 'down'
            options_holder.add_widget(button)
            button.bind(on_release=self._set_option)
        scroller.add_widget(options_holder)
        cancel_button = WideButton(text='Cancel')
        cancel_button.bind(on_release=self._dismiss)
        content.add_widget(cancel_button)
        max_height = app.root.height - (app.button_scale * 3)
        height = min((len(self.options) + 3) * app.button_scale, max_height)
        app.popup = NormalPopup(title=self.title, content=content, size_hint=(None, None), size=(app.popup_x, height))
        app.popup.open()


class SettingPath(SettingItem, Navigation):
    """Path value in the settings screen.  Customizes the input popup"""

    popup = ObjectProperty(None, allownone=True)
    show_hidden = BooleanProperty(True)
    dirselect = BooleanProperty(True)

    def on_navigation_activate(self):
        self._create_popup(self)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def _dismiss(self, *largs):
        app = App.get_running_app()
        if app.popup:
            app.popup.dismiss()
        app.popup = None

    def _validate(self, browser):
        value = browser.selected[0]
        self._dismiss()
        if not value:
            return
        self.value = os.path.realpath(value)

    def _create_popup(self, instance):
        app = App.get_running_app()
        if app.popup:
            app.popup.dismiss()

        if self.value:
            if not self.dirselect:
                initial_path, selected = os.path.split(self.value)
            else:
                initial_path = self.value
                selected = ''
        else:
            initial_path = os.getcwd()
            selected = ''
        content = FileBrowser(folder=initial_path, selected=[selected], show_hidden=self.show_hidden, file_select=not self.dirselect, folder_select=self.dirselect, show_files=not self.dirselect)
        content.bind(on_select=self._validate)
        content.bind(on_cancel=self._dismiss)
        app.popup = NormalPopup(title=self.title, content=content, size_hint=(0.9, 0.9))
        app.popup.open()


class SettingString(SettingItem, Navigation):
    """String value in the settings screen.  Customizes the input popup"""

    popup = ObjectProperty(None, allownone=True)
    textinput = ObjectProperty(None)

    def on_navigation_activate(self):
        self._create_popup(self)

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
        self.popup = NormalPopup(title=self.title, content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 3.1), auto_dismiss=True)
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
        self.register_type('options', SettingOptions)
        self.register_type('title', SettingTitle)
        self.register_type('path', SettingPath)
        self.register_type('numeric', SettingNumeric)
        self.register_type('aboutbutton', SettingAboutButton)


class SettingAboutButton(SettingItem):
    """Settings widget that opens an about dialog."""
    pass


class AboutPopup(Popup):
    """Basic popup message with a message and 'ok' button."""

    button_text = StringProperty('OK')

    def close(self, *_):
        app = App.get_running_app()
        app.popup.dismiss()
