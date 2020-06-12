import json
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from .textinput import InputMenu
from .popup import MessagePopupContent, NormalPopup
from .button import ClickFade
from .settings import *

themes = [
    {
        "name": "Clean And Bright",
        "button_down": [0.651, 0.651, 0.678, 1.0],
        "button_up": [0.8, 0.8, 0.8, 1.0],
        "button_text": [0.0, 0.0, 0.0, 1.0],
        "button_warn_down": [0.78, 0.33, 0.33, 1.0],
        "button_warn_up": [1.0, 0.493, 0.502, 1.0],
        "button_toggle_true": [0.31, 0.68, 0.46, 1.0],
        "button_toggle_false": [0.678, 0.651, 0.678, 1.0],
        "button_menu_up": [0.686, 0.686, 0.686, 1.0],
        "button_menu_down": [0.511, 0.52, 0.52, 1.0],
        "button_disabled": [0.686, 0.695, 0.721, 0.669],
        "button_disabled_text": [1.0, 1.0, 1.0, 0.748],
        "header_background": [1.0, 1.0, 1.0, 0.397],
        "header_text": [0.107, 0.099, 0.099, 1.0],
        "info_text": [0.0, 0.0, 0.0, 1.0],
        "info_background": [1.0, 1.0, 0.0, 0.75],
        "input_background": [1.0, 1.0, 1.0, 0.651],
        "scroller": [0.7, 0.7, 0.7, 0.388],
        "scroller_selected": [0.7, 0.7, 0.7, 0.9],
        "sidebar_background": [1.0, 1.0, 1.0, 0.792],
        "sidebar_resizer": [0.862, 1.0, 0.897, 1.0],
        "slider_grabber": [0.45, 0.45, 0.458, 1.0],
        "slider_background": [1.0, 1.0, 1.0, 1.0],
        "main_background": [0.616, 0.616, 0.616, 0.32],
        "menu_background": [0.529, 0.537, 0.537, 1.0],
        "area_background": [0.0, 0.0, 0.0, 0.046],
        "text": [0.0, 0.011, 0.0, 1.0],
        "disabled_text": [0.0, 0.0, 0.0, 0.572],
        "selected": [0.239, 1.0, 0.344, 0.634],
        "background": [1.0, 1.0, 1.0, 1.0],
    },
    {
        "name": "Blue And Green",
        "button_down": [0.48, 0.59, 0.62, 1.0],
        "button_up": [0.35, 0.49, 0.53, 1.0],
        "button_text": [1.0, 1.0, 1.0, 0.9],
        "button_warn_down": [0.78, 0.33, 0.33, 1.0],
        "button_warn_up": [0.8, 0.08, 0.08, 1.0],
        "button_toggle_true": [0.31, 0.68, 0.46, 1.0],
        "button_toggle_false": [0.38, 0.38, 0.38, 1.0],
        "button_menu_up": [0.14, 0.42, 0.35, 1.0],
        "button_menu_down": [0.15, 0.84, 0.67, 1.0],
        "button_disabled": [0.28, 0.28, 0.28, 1.0],
        "button_disabled_text": [1.0, 1.0, 1.0, 0.5],
        "header_background": [0.739, 0.739, 0.8, 1.0],
        "header_text": [1.0, 1.0, 1.0, 1.0],
        "info_text": [0.0, 0.0, 0.0, 1.0],
        "info_background": [1.0, 1.0, 0.0, 0.75],
        "input_background": [0.18, 0.18, 0.27, 1.0],
        "scroller": [0.7, 0.7, 0.7, 0.4],
        "scroller_selected": [0.7, 0.7, 0.7, 0.9],
        "slider_grabber": [0.5098, 0.8745, 0.6588, 1.0],
        "slider_background": [0.546, 0.59, 0.616, 1.0],
        "main_background": [0.5, 0.5, 0.634, 0.292],
        "menu_background": [0.26, 0.29, 0.31, 1.0],
        "text": [1.0, 1.0, 1.0, 0.9],
        "disabled_text": [1.0, 1.0, 1.0, 0.5],
        "selected": [0.5098, 0.8745, 0.6588, 0.5],
        "background": [0.0, 0.0, 0.0, 1.0],
    }
]


class Theme(Widget):
    """Theme class that stores all the colors used in the interface."""

    button_down = ListProperty()
    button_up = ListProperty()
    button_text = ListProperty()
    button_warn_down = ListProperty()
    button_warn_up = ListProperty()
    button_toggle_true = ListProperty()
    button_toggle_false = ListProperty()
    button_menu_up = ListProperty()
    button_menu_down = ListProperty()
    button_disabled = ListProperty()
    button_disabled_text = ListProperty()

    header_background = ListProperty()
    header_text = ListProperty()
    info_text = ListProperty()
    info_background = ListProperty()

    input_background = ListProperty()
    scroller = ListProperty()
    scroller_selected = ListProperty()
    slider_grabber = ListProperty()
    slider_background = ListProperty()

    main_background = ListProperty()
    menu_background = ListProperty()
    text = ListProperty()
    disabled_text = ListProperty()
    selected = ListProperty()
    background = ListProperty()


class NormalApp(App):
    theme_index = NumericProperty(0)  #Override this to create an app with a different theme index
    popup_x = NumericProperty(640)  #Override this to set the default width of popups
    about_text = 'About'  #Override this to change the text that appears in the the about popup in the settings screen
    animations = BooleanProperty(True)  #Set this to disable animations in the app
    animation_length = NumericProperty(0.2)  #Set this to change the length in seconds that animations will take

    list_background_odd = ListProperty([0, 0, 0, 0])
    list_background_even = ListProperty([0, 0, 0, .1])
    button_scale = NumericProperty(100)
    text_scale = NumericProperty(100)
    display_padding = NumericProperty(8)
    display_border = NumericProperty(16)
    settings_cls = AppSettings
    last_height = NumericProperty(0)
    last_width = NumericProperty(0)
    bubble = ObjectProperty(allownone=True)

    clickfade_object = ObjectProperty()
    infotext = StringProperty('')
    infotext_setter = ObjectProperty()
    popup = ObjectProperty(allownone=True)
    theme = ObjectProperty()
    button_update = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.theme = Theme()
        self.load_theme(self.theme_index)
        Window.bind(on_draw=self.rescale_interface)
        super().__init__(**kwargs)

    def clickfade(self, widget, mode='opacity'):
        try:
            Window.remove_widget(self.clickfade_object)
        except:
            pass
        if self.clickfade_object is None:
            self.clickfade_object = ClickFade()
        self.clickfade_object.size = widget.size
        self.clickfade_object.pos = widget.to_window(*widget.pos)
        self.clickfade_object.begin(mode)
        Window.add_widget(self.clickfade_object)

    def load_theme(self, theme_index):
        """Load and display a theme from the current presets"""

        data = themes[theme_index]
        self.data_to_theme(data)

    def data_to_theme(self, data):
        """Converts a theme dictionary into the theme object that is used for displaying colors"""

        theme = self.theme
        for color in data:
            if hasattr(theme, color):
                new_color = data[color]
                r = float(new_color[0])
                g = float(new_color[1])
                b = float(new_color[2])
                a = float(new_color[3])
                new_color = [r, g, b, a]
                setattr(theme, color, new_color)
        self.button_update = not self.button_update

    def rescale_interface(self, *_, force=False):
        """Called when the window changes resolution, calculates variables dependent on screen size"""

        if Window.width != self.last_width:
            self.last_width = Window.width
            self.popup_x = min(Window.width, 640)

        if (Window.height != self.last_height) or force:
            self.last_height = Window.height
            self.button_scale = int((Window.height / 15) * int(self.config.get("Settings", "buttonsize")) / 100)
            self.text_scale = int((self.button_scale / 3) * int(self.config.get("Settings", "textsize")) / 100)
            self.display_border = self.button_scale / 3
            self.display_padding = self.button_scale / 4

    def popup_bubble(self, text_input, pos):
        """Calls the text input right-click popup menu"""

        self.close_bubble()
        text_input.unfocus_on_touch = False
        self.bubble = InputMenu(owner=text_input)
        window = self.root_window
        window.add_widget(self.bubble)
        posx = pos[0]
        posy = pos[1]
        #check position to ensure its not off screen
        if posx + self.bubble.width > window.width:
            posx = window.width - self.bubble.width
        if posy + self.bubble.height > window.height:
            posy = window.height - self.bubble.height
        self.bubble.pos = [posx, posy]

    def close_bubble(self, *_):
        """Closes the text input right-click popup menu"""

        if self.bubble:
            self.bubble.owner.unfocus_on_touch = True
            window = self.root_window
            window.remove_widget(self.bubble)
            self.bubble = None

    def message(self, text, timeout=20):
        """Sets the app.infotext variable to a specific message, and clears it after a set amount of time."""

        self.infotext = text
        if self.infotext_setter:
            self.infotext_setter.cancel()
        self.infotext_setter = Clock.schedule_once(self.clear_message, timeout)

    def clear_message(self, *_):
        """Clear the app.infotext variable"""

        self.infotext = ''

    def about(self):
        """Opens a special message popup with the app's about text in it"""

        title = "About This App"
        text = self.about_text
        self.message_popup(text, title=title)

    def message_popup(self, text, title='Notification'):
        """Opens a basic message popup with an ok button"""

        if self.popup:
            self.popup.dismiss()
        content = MessagePopupContent(text=text)
        self.popup = NormalPopup(title=title, content=content, size_hint=(None, None), size=(self.popup_x, self.button_scale * 4))
        self.popup.open()

    def build_config(self, config):
        """Setup config file if it is not found"""

        config.setdefaults(
            'Settings', {
                'buttonsize': 100,
                'textsize': 100,
            })

    def build_settings(self, settings):
        """Kivy settings dialog panel
        settings types: title, bool, numeric, options, string, path"""

        settingspanel = []
        settingspanel.append({
            "type": "aboutbutton",
            "title": "",
            "section": "Settings",
            "key": "buttonsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Button Scale",
            "desc": "Button Scale Percent",
            "section": "Settings",
            "key": "buttonsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Text Scale",
            "desc": "Font Scale Percent",
            "section": "Settings",
            "key": "textsize"
        })
        settings.add_json_panel('Settings', self.config, data=json.dumps(settingspanel))

    def on_config_change(self, config, section, key, value):
        """Called when the configuration file is changed"""

        self.rescale_interface(force=True)
